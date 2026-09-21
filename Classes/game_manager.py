# Contents of the GameManager class

from enum import Enum

from Utils.card_serialization import SUITS_TO_SYMBOL, initials_to_id, get_suit_str, id_to_prose
from Utils.cli_tools import clear_screen
from Utils.types import CardInt, PlayerStr, TrumpStr

from .bidding_flow import BiddingFlow
from .deck import Deck
from .initial_trump_flow import InitialTrumpFlow
from .iterative_trump_flow import IterativeTrumpFlow
from .local_card_assignment import LocalCardAssignmentFlow
from .human_player import Player
from .player_setup_flow import PlayerSetupFlow
from .playing_flow import PlayingFlow
from .scoreboard import Scoreboard
from .step import *
from .trump_manager import TrumpManager
from .ui_manager import UIManager

from game_state import GameState

VALID_CARD_INITIALS = {
    (f"{rank}{suit}")
    for rank in (2,3,4,5,6,7,8,9,10,'J','Q','K','A')
    for suit in "CDHS"
    }
CARDS_PER_ROUND = (8,7,6,6,7,8)

class Phase(Enum):
        PLAYER_SELECTION = "player_selection"
        HAND_ASSIGNMENT = 'hand_assignment'
        INITIAL_TRUMP_SELECTION = "initial_trump_selection"
        TRUMP_REDECIDING = "trump_redeciding"
        BIDDING = "bidding"
        PLAYING = "playing"
        SCORING = "scoring"
        GAME_OVER = "game_over"

class GameMode(Enum):
    ASSISTANT = 'assistant'
    SIM = 'simulation'
    SINGLE_PLAYER = 'single_player'



class Game:
    """
    Class for managing the game state and orchestrating the gamee

    Attributes:
        player_queue (list): A list which stores the order of which the players are playing
        round (int): An integer value of the current round the game is in
        cards_per_round (list): A ;ist of the maximum cards per round
        phase (str): A string which indicates the current action of the game object
    """

    def __init__(self, gamemode: str = ''):  # ACTION: Must validate mode is valid mode
        """
        When initialised, the game object should receive the player parameters
        """


        self.gamemode = gamemode
        self.phases = {
            Phase.PLAYER_SELECTION: self.handle_player_selection,
            Phase.HAND_ASSIGNMENT: self.handle_hand_assignment,
            Phase.INITIAL_TRUMP_SELECTION: self.handle_initial_trump_selection,
            Phase.TRUMP_REDECIDING: self.handle_redeciding_trump,
            Phase.BIDDING: self.handle_bidding_phase,
            Phase.PLAYING: self.handle_playing_phase,
            Phase.SCORING: self.handle_scoring_phase,
        }

        #initial phase
        self.phase = Phase.PLAYER_SELECTION
        self.trump_suit = ''

        self.player_queue = [] #queue for playing during rounds

        # THOUGHT: Requires Player class and Bot class, in order to make decisions, maps to PlayerStr though

    def start(self):
        clear_screen() 
        self.create_game()
        self.run_game_phases()
        clear_screen() #2   

    def create_game(self):
        """
        Initialises the game and the objects it requires. 

        """        
        #generate deck
        self.deck = Deck()

        #Generates objects for the game
        self.UIManager = UIManager()
        self.trumpManager = TrumpManager()
        self.playerSetupFlow = PlayerSetupFlow()
        self.biddingFlow = BiddingFlow()
        self.initialTrumpFlow = InitialTrumpFlow()
        self.localCardAssignmentFlow = LocalCardAssignmentFlow(VALID_CARD_INITIALS)

    def run_game_phases(self):
        """
        Starts the game 
        """
        while self.phase != Phase.GAME_OVER:  # THOUGHT: Could change this to query gamestate object, 
                # Don't know if that will smoothly reset things within the phase though, need to remove round from this class
                _phase_handler = self.phases.get(self.phase)
                if _phase_handler:
                    _phase_handler() # function from the dictionary is performed
                else:
                    raise ValueError(f"Unknown game phase: {self.phase}") 

        # Game over, need to prompt a retry button
        self.UIManager.game_over_message(state=self.game_state)
        
    def handle_player_selection(self): 
        """
        Player selection logic and gamestate

        """
        context = self.playerSetupFlow.run()

        #verified names list
        verified_names = self.playerSetupFlow.remove_duplicates(
            input_players = [player['name'] 
                             for player in context['player_names']]
            )

        opponents_flags = [player['opponent'] for player in context['player_names']]

        # creating player queue
        for index, name in enumerate(verified_names):
            self.player_queue.append( Player(
                name=name,
                opponent=opponents_flags[index])
            )

        # Can initialise the gamestate object now, as it requires the player queue to be initialised
        self.game_state = GameState(
            player_order=tuple(player.name for player in self.player_queue), 
            hands={player.name: set(player.hand) for player in self.player_queue},
            trump_suit=self.trump_suit,
            current_trick=(),
            round_scores={player.name: 0 for player in self.player_queue},
            total_scores={player.name: 0 for player in self.player_queue},
            bids={player.name: 0 for player in self.player_queue})

        # ACTION: Remove scoreboard init 
        # Can initialise scoreboard now
        self.scoreboard = Scoreboard()


        self.phase = Phase.HAND_ASSIGNMENT

    def handle_hand_assignment(self):
        """
        Docstring for handle_hand_assignment

        Handles hand assingment for both types of players, in assistant mode. 
        Responsible for resetting the game state for the new round
        
        """

        # Reset Deck
        self.deck = Deck()

        # After initial round reset for new round
        if self.game_state.round > 1:
            self.game_state = self.game_state.get_next_round_state()

        # THOUGHT: Assistant only?
        for player in self.player_queue:

            # local players only
            if player.opponent is False: 
                self.localCardAssignmentFlow.generate_prompt(player)
                
                #iterate for amount of cards in hand for the current round
                while len(self.game_state.hands[player.name]) < CARDS_PER_ROUND[self.game_state.round-1]:

                    player_card_list = self.game_state.hands[player.name]
                    choice_of_initials = self.localCardAssignmentFlow.assign_card(
                        player.name, self.game_state
                    )
                    
                    if not self.deck.contains(initials_to_id(choice_of_initials)):

                        # ACTION: Assistant mode
                        self.UIManager.print_trump_initials_error(choice_of_initials)
                        continue # loops until there is a valid card

                    chosen_card = self.deck.draw_specific_card(choice_of_initials)

                    # ACTION: Remove chosen card print out
                    self.UIManager.print_chosen_card(chosen_card)

                    if not chosen_card:
                        self.UIManager.print_initials_choice_error(choice_of_initials)
                    else:
                        self.game_state.hands[player.name].add(chosen_card)
                        

        # THOUGHT: This confuses me, I'm assuming that the trump is selected elsewhere asif it were selected in person,
        # However, that won't always be the case as trump selection should be universal to adhere to sim logic
        if self.game_state.round == 1:
            self.phase = Phase.INITIAL_TRUMP_SELECTION
        else:
            self.phase = Phase.BIDDING


    def handle_initial_trump_selection(self):
        """
        Docstring for trump_selection. Repeats until a valid trump suit has been selected.
        
        """

        clear_screen() #2

        # ACTION: Remove print statement opening round and bidding phase
        self.UIManager.print_opening_bidding_round_statement(self.game_state)
        
        context = self.initialTrumpFlow.run(VALID_CARD_INITIALS)
        manual_trump_generation = context['manual_trump_generation']
        trump_card_initials = context['trump_card_initials']

        #   automatic trump generation
        if not manual_trump_generation:
            card = self.select_trump_automatically()

        #   manual trump selection
        else:

            # verify tc initials exist
            if not trump_card_initials:
                return 
            
            if not self.deck.contains(initials_to_id(trump_card_initials)):
                return
            
            selected_card = self.deck.draw_specific_card(trump_card_initials)
            if not selected_card:
                # Ok for simple print as it is assumed that
                # manual trump selection will be done only in Assistant mode
                self.UIManager.display_message("Invalid card")
                return
        
            self.game_state.trump_suit = get_suit_str(selected_card)

        # Everything is valid hence move on to next phase
        self.phase = Phase.BIDDING
    
    def select_trump_automatically(self) -> CardInt:
        """
        Selects trump card automatically while also outputting
        information depending on the gamemode.
        """
        
        trump_card = self.deck.draw_random()
        #since deck is already shuffled, pick first card
        self.game_state.trump_suit = get_suit_str(trump_card)

        if self.gamemode == 'assistant':
            clear_screen()
            self.UIManager.print_random_trump_confirmation(state=self.game_state,
                                                         trump_card = id_to_prose(trump_card))
        return trump_card
    

    def handle_bidding_phase(self):
        """
        Bidding logic
        """
        # THOUGHT: Why do we get next round state for the initial bidding phase
        # shouldnt I check before enforcing this

        #starts the bidding process and must update state
        if self.gamemode == 'assistant':
            print("Bidding Phase Commencing\n")  # FIx
            self.state = self.biddingFlow.run(state=self.game_state)

        self.phase = Phase.PLAYING

    def handle_playing_phase(self):
        """
        Playing logic
        """
        max_cards_this_round = CARDS_PER_ROUND[self.game_state.round-1]

        for _ in range(max_cards_this_round):
            self.start_trick()

        self.phase = Phase.SCORING

    def handle_redeciding_trump(self):
        """
        Docstring for handle_redeciding_trump
        """

        # redecide trump
        self.iterativeTrumpFlow = IterativeTrumpFlow()

        chosen_player = self.trumpManager.decide_trump(
            state=)
        context = self.iterativeTrumpFlow.run(chosen_player)

        self.trump_suit = context['trump_suit']

        #reset players after selecting trump to ensure that round scores are valid
        for player in self.player_queue:
                player.reset() 
    
        self.phase = Phase.HAND_ASSIGNMENT

    def handle_scoring_phase(self):
        """
        Scoring logic
        """
        if self.game_state.round < 1:  # 6
            self.game_state.round += 1
            #display total scoreboard

            # ACTION: Remove print statement of score board before updating
            print("Scoreboard before ts", self.scoreboard.total_scoreboard)
            self.scoreboard.update_total_scoreboard(
                player_list=self.player_queue,
                max_cards=CARDS_PER_ROUND[self.game_state.round-1]
                )
            clear_screen(5)

            # Action: Remove total score output after round completion
            print("Total score: ",(self.scoreboard.display(round=False)))
            self.phase = Phase.TRUMP_REDECIDING
        else:
            self.phase = Phase.GAME_OVER
            return

    def start_trick(self):
        """
        Logic for the functionality of the playing each trick
        """

        # Action: Remove table reset, should now be state reset round scores and trick 
        self.table.reset()

        # ACtion: Remove reorder round scoreboard 
        self.scoreboard.reorder_round_scoreboard(
            player_queue=self.temp_player_queue
            )

        # Probably needs state now
        self.playingFlow = PlayingFlow(
            self.table,
            self.scoreboard,
            VALID_CARD_INITIALS)

        # THOUGHT: Idk what temp_player_queue means
        for player in self.temp_player_queue:

            while True:

                # Will alter trump suit to include the symbol as well
                choice = self.playingFlow.play_turn(
                    player=player,
                    trump_suit=f"{self.trump_suit} {SUITS_TO_SYMBOL[self.trump_suit]}")
                
                if player.opponent:
                    print("choice", choice)
                    selected_card = self._materialise_played_card(player, str(choice))
                    if not selected_card:
                        print(f"invalid card input, {selected_card} is not longer in the deck")
                        continue

                    print(f"{player} selected card", selected_card)
                    self._remote_play_card(player, selected_card)
                    break  # successful play

                else:
                    # local player

                    try: 
                        selected_card = player.hand[int(choice)-1]
                        print(f"{player} selected card", selected_card)
                    except:
                        print("Invalid Card Index")
                        continue
                
                    if not self._local_play_card(player, selected_card):
                        continue
                    break 

        # ACTION: Remove Score hand function
        self.score_hand()
          
            

    def _local_play_card(self, player: PlayerStr, selected_card: CardInt):
        """
        Plays card to the table for local player and removes card from hand

        returns False if unable to play the card
        """

        if not self.table.play_card_to_table(
                selected_card, player, self.trump_suit
            ):
                return None
        
        #after playing the card remove it from the player hand  ##Fix
        self.game_state.hands[player].remove(selected_card)
        return True


    def _remote_play_card(self, player: Player, selected_card: Card):
        """
        Plays card to the table for remote player and removes it from the deck
        """
        
        if self.table.play_card_to_table(selected_card, player, self.trump_suit) == False:
            raise ValueError("unable to play card to table")
