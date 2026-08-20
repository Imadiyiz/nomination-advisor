# Contents of the GameManager class

from enum import Enum

from Utils.card_tools import SUITS_TO_SYMBOL, initials_to_id
from Utils.tools import clear_screen

from .BiddingFlow import BiddingFlow
from .BiddingManager import BiddingManager
from .CardClass import Card
from .DeckClass import Deck
from .InitialTrumpFlow import InitialTrumpFlow
from .IterativeTrumpFlow import IterativeTrumpFlow
from .LocalCardAssignmentFlow import LocalCardAssignmentFlow
from .PlayerClass import Player
from .PlayerSetupFlow import PlayerSetupFlow
from .PlayerStateManager import PlayerStateManager
from .PlayingFlow import PlayingFlow
from .ScoreboardClass import Scoreboard
from .StepClass import *
from .TableClass import Table
from .TrumpManager import TrumpManager
from .UIManager import UIManager

VALID_CARD_INITIALS = {
    (f"{rank}{suit}")
    for rank in (2,3,4,5,6,7,8,9,10,'J','Q','K','A')
    for suit in "CDHS"
    }

class Phase(Enum):
        PLAYER_SELECTION = "player_selection"
        HAND_ASSIGNMENT = 'hand_assignment'
        TRUMP_SELECTION = "trump_selection"
        TRUMP_REDECIDING = "trump_redeciding"
        BIDDING = "bidding"
        PLAYING = "playing"
        SCORING = "scoring"
        GAME_OVER = "game_over"



class Game:
    """
    Class for managing the game state and orchestrating the gamee

    Attributes:
        player_queue (list): A list which stores the order of which the players are playing
        menu_options (dict): A dictionary which stores the current options for the menu
        round (int): An integer value of the current round the game is in
        cards_per_round (list): A ;ist of the maximum cards per round
        phase (str): A string which indicates the current action of the game object
    """

    def __init__(self,*args, **kwargs):
        """
        When initialised, the game object should receive the player parameters
        """
        self.menu_options = {
            "S": "SHOW HAND",
            "B": "BID" 
        }

        self.round = 1
        self.cards_per_round = [2,3,6,6,7,8] #change to 8
        self.phases = {
            Phase.PLAYER_SELECTION: self.handle_player_selection,
            Phase.HAND_ASSIGNMENT: self.handle_hand_assignment,
            Phase.TRUMP_SELECTION: self.handle_trump_selection,
            Phase.TRUMP_REDECIDING: self.handle_redeciding_trump,
            Phase.BIDDING: self.handle_bidding_phase,
            Phase.PLAYING: self.handle_playing_phase,
            Phase.SCORING: self.handle_scoring_phase,
        }

        #initial phase
        self.phase = Phase.PLAYER_SELECTION
        self.trump_suit = ''

        self.player_queue = [] #queue for playing during rounds

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
        self.table = Table(self.UIManager)
        self.biddingManager = BiddingManager(self.UIManager)
        self.playerStateManager = PlayerStateManager(self.player_queue)
        self.trumpManager = TrumpManager(self.UIManager)
        self.playerSetupFlow = PlayerSetupFlow()
        self.biddingFlow = BiddingFlow(self.player_queue)
        self.initialTrumpFlow = InitialTrumpFlow()
        self.localCardAssignmentFlow = LocalCardAssignmentFlow(
            VALID_CARD_INITIALS)

    def run_game_phases(self):
        """
        Starts the game 
        """
        while self.phase != Phase.GAME_OVER:
                _phase_handler = self.phases.get(self.phase)
                if _phase_handler:
                    _phase_handler() # function from the dictionary is performed
                else:
                    raise ValueError(f"Unknown game phase: {self.phase}") 

        
    def handle_player_selection(self):
        """
        Player selection logic and initialises the scoreboards as they rely on player selection

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

        # round player_queue
        self.temp_player_queue = self.player_queue

        # Can initialise scoreboard now
        self.scoreboard = Scoreboard(self.player_queue)

        self.phase = Phase.HAND_ASSIGNMENT

    def handle_hand_assignment(self):
        """
        Docstring for handle_hand_assignment

        Handles hand assingment for both types of players
        
        """
        
        #initialise objects and reset
        max_cards = self.cards_per_round[self.round-1]
        self.scoreboard.reset_round_scoreboard()

        for player in self.player_queue:

            # local players only
            if not player.opponent: 
                self.localCardAssignmentFlow.generate_prompt(player)
                
                #iterate for amount of cards in hand for the current round
                while len(player.hand) < self.cards_per_round[self.round-1]:

                    choice_of_initials = self.localCardAssignmentFlow.assign_card(
                        player, max_cards
                    )
                    
                    # choice of initials has not been sanitised ANYMORE
                    if not self.deck.contains(initials_to_id(choice_of_initials)):
                        print(f"{choice_of_initials} has already been used and is no longer in the deck")
                        continue # loops until there is a valid card

                    chosen_card = self.deck.draw_specific_card(choice_of_initials)
                    print(chosen_card, "chosen card")
                    if chosen_card:
                        player.hand.append(chosen_card)
                        player.own_hand()
                    else:
                        print(f"{choice_of_initials} is no longer in the deck")
                        print(len(self.deck))

        
        if self.round == 1:
            self.phase = Phase.TRUMP_SELECTION
        else:
            self.phase = Phase.BIDDING

    def handle_trump_selection(self):
        """
        Docstring for trump_selection
        
        """

        clear_screen() #2
        cards =  self.cards_per_round[self.round-1]
        print(f"ROUND {self.round} - Bidding Phase ({cards} cards per hand)\n")

        context = self.initialTrumpFlow.run(VALID_CARD_INITIALS)
        manual_trump_generation = context['manual_trump_generation']
        trump_card_initials = context['trump_card_initials']

        #   automatic trump generation
        if not manual_trump_generation:
            card = self.select_trump_automatically()

        #   manual trump selection
        else:
            if self.deck.contains(
                card=initials_to_id(trump_card_initials)):
                card = self.deck.draw_specific_card(trump_card_initials)
            else:
                return
            if not card:
                print("Invalid card")
                return
        
            self.trump_suit = card.suit

        self.phase = Phase.BIDDING
    
    def select_trump_automatically(self):

        clear_screen()
        trump_card = self.deck.draw_random()
        #determine trump
        #since deck is already shuffled, pick first card
        # choose the trump after cards have been assinged to players
        self.trump_suit = trump_card.suit
        print(f"Random trump card - {trump_card}")
        print("Trump suit: ", self.trump_suit)

        return trump_card
    

    def handle_bidding_phase(self):
        """
        Bidding logic
        """

        self.max_cards = self.cards_per_round[self.round-1]
        self.playerStateManager.reset_players_handicap()

        #dealer shifts every time bidding starts
        if self.round > 1:
            self.player_queue = self.playerStateManager.update_dealer_order(self.player_queue)
        
        self.player_queue[-1].handicapped_bid = True
        self.biddingManager.reset_bids(self.player_queue)
        self.biddingManager.update_current_bids(self.player_queue)

        #starts the bidding process
        self.biddingFlow.run(
            round_no=self.round,
            max_cards=self.max_cards,
            players = self.player_queue,
            bidding_manager=self.biddingManager,
            trump_suit=self.trump_suit,
        )

        self.phase = Phase.PLAYING

    def handle_playing_phase(self):
        """
        Playing logic
        """
        cards = self.cards_per_round[self.round-1]
        self.scoreboard.reset_round_scoreboard()

        for _ in range(cards):
            self.start_round()

        self.phase = Phase.SCORING

    def handle_redeciding_trump(self):
        """
        Docstring for handle_redeciding_trump
        """

        # redecide trump
        self.iterativeTrumpFlow = IterativeTrumpFlow()

        chosen_player = self.trumpManager.decide_trump(
            players=self.player_queue)
        context = self.iterativeTrumpFlow.run(chosen_player)

        self.trump_suit = context['trump_suit']

        #reset players after selecting trump to ensure that round scores are valid
        for player in self.player_queue:
                player.reset() 

        # part of the rest is getting a new deck
        self.deck = Deck()
    
        self.phase = Phase.HAND_ASSIGNMENT

    def handle_scoring_phase(self):
        """
        Scoring logic
        """
        if self.round < 6:
            self.round += 1
            #display total scoreboard
            print("Scoreboard before ts", self.scoreboard.total_scoreboard)
            self.scoreboard.update_total_scoreboard(
                player_list=self.player_queue,
                max_cards=self.max_cards
                )
            clear_screen(5)
            print("Total score: ",(self.scoreboard.display(round=False)))
            self.phase = Phase.TRUMP_REDECIDING
        else:
            self.phase = Phase.GAME_OVER
            return

    def start_round(self):
        """
        Logic for the functionality of the playing round
        """
        self.table.reset()
        self.scoreboard.reorder_round_scoreboard(
            player_queue=self.temp_player_queue
            )
        self.playingFlow = PlayingFlow(
            self.table,
            self.scoreboard,
            VALID_CARD_INITIALS)
        
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

        self.score_hand()
          
            

    def _local_play_card(self, player:Player, selected_card: Card):
        """
        Plays card to the table for local player and removes card from hand

        returns False if unable to play the card
        """

        if not self.table.play_card_to_table(
                selected_card, player, self.trump_suit
            ):
                return None
        
        #after playing the card remove it from the player hand
        player.remove_card(card=selected_card)
        return True


    def _remote_play_card(self, player: Player, selected_card: Card):
        """
        Plays card to the table for remote player and removes it from the deck
        """
        
        if self.table.play_card_to_table(selected_card, player, self.trump_suit) == False:
            raise ValueError("unable to play card to table")

        
        
    def score_hand(self):
        """
        Scores on a play by play basis (multiple times per round)
        """

        winner_card = self.table.verify_winner(trump_suit=self.trump_suit)
        winning_player = winner_card.owner
        print(f"\n{winning_player} is the winner with {winner_card}\n")
        
        self.scoreboard.update_round_scoreboard(
            player_list=self.player_queue, 
            winner_card=winner_card)
    
        # used for updating the winner order at the end of each hand
        # effective a round_player_queue
        self.temp_player_queue = self.playerStateManager.update_winner_order(
            winner=winning_player, 
            player_queue=self.player_queue)

    def _materialise_played_card(self, player:Player, choice: str):
        """
        Turns a declared card into a real Card instance and assigns
        the card owner to the player
        choice is the initials for the card
        """

        if not self.deck.contains(initials_to_id(choice)):
            return None
        
        card = self.deck.draw_specific_card(choice)

        card.owner = player
        return card
