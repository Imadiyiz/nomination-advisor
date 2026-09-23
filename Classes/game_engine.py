# Contents of the GameManager class
# SELF.STATE ISSUE TODO:
import random
from enum import Enum

from game_state import GameState
from Utils.card_serialization import (
        SUITS,
        SUITS_TO_SYMBOL,
        get_suit_str,
        id_to_initials,
        id_to_prose,
        initials_to_id,
)
from Utils.cli_tools import clear_screen
from Utils.types import CardInt, PlayerStr, TrumpStr

from .bidding_flow import BiddingFlow
from .deck import Deck
from .human_player import HumanPlayer
from .iterative_trump_flow import IterativeTrumpFlow
from .local_card_assignment_flow import LocalCardAssignmentFlow
from .manual_trump_selection_flow import ManualTrumpSelectionFlow
from .player_setup_flow import PlayerSetupFlow
from .playing_flow import PlayingFlow
from .step import *
from .trump_manager import TrumpManager
from .trump_selection_type_flow import TrumpSelectionTypeFlow
from .ui_manager import UIManager

class Phase(Enum):
        PLAYER_SELECTION = "player_selection"
        HAND_ASSIGNMENT = 'hand_assignment'
        INITIAL_TRUMP_SELECTION = "initial_trump_selection"
        TRUMP_REDECIDING = "trump_redeciding"
        BIDDING = "bidding"
        PLAYING = "playing"
        SCORING = "scoring"
        GAME_OVER = "game_over"

class GameEngine:
    """
    Class for managing the game state and orchestrating the gamee

    Attributes:
        round (int): An integer value of the current round the game is in
        cards_per_round (list): A ;ist of the maximum cards per round
        phase (str): A string which indicates the current action of the game object
    """

    def __init__(self):  # ACTION: Must validate mode
        """
        When initialised, the game object should receive the player parameters
        """
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


        self.player_objects = [] # Makes it clear whether a player is a human or robot

        # THOUGHT: Requires HumanPlayer class and Bot class, in order to make decisions, maps to PlayerStr though

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
        self.trump_selection_type_flow = TrumpSelectionTypeFlow()
        self.manual_trump_selection_flow = ManualTrumpSelectionFlow()
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
        self.UIManager.print_game_over_message(state=self.game_state)
        
    def handle_player_selection(self): 
        """
        Player selection logic and gamestate

        """
        context = self.playerSetupFlow.run()

        #verified names list
        verified_names = self.playerSetupFlow.remove_duplicates(
            input_players = context['player_names']
            )

        perspective = context['perspective']

        # creating player queue
        for name in verified_names:
            self.player_objects.append(HumanPlayer(name))

        # Can initialise the gamestate object now, as it requires the player queue to be initialised
        self.game_state = GameState(
            player_order=tuple(player for player in verified_names), 
            hands={player: set() for player in verified_names},
            trump_suit='',
            current_trick=(),
            round_scores={player: 0 for player in verified_names},
            total_scores={player: 0 for player in verified_names},
            bids={player: 0 for player in verified_names},
            perspective = perspective)

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

        # THOUGHT: Assistant only? WHY LOOP IF YOU KNOW PERSPECTIVE
        for player in self.game_state.player_order:

            # local players only
            if player == self.game_state.perspective: 
                self.localCardAssignmentFlow.generate_prompt(player)
                
                #iterate for amount of cards in hand for the current round
                while len(self.game_state.hands[player]) < CARDS_PER_ROUND[self.game_state.round-1]:

                    choice_of_initials = self.localCardAssignmentFlow.assign_card(
                        player, self.game_state
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
                        self.game_state.hands[player].add(chosen_card)
                        

        # THOUGHT: This confuses me, I'm assuming that the trump is selected elsewhere asif it were selected in person,
        # However, that won't always be the case as trump selection should be universal to adhere to sim logic
        if self.game_state.round == 1:
            self.phase = Phase.INITIAL_TRUMP_SELECTION
        else:
            self.phase = Phase.TRUMP_REDECIDING


    def handle_initial_trump_selection(self):
        """
        Docstring for trump_selection. Repeats until a valid trump suit has been selected.
        
        """

        clear_screen() #2

        self.UIManager.print_opening_bidding_round_statement(self.game_state)
        
        manual_trump_generation = self.trump_selection_type_flow.run()

        #   automatic trump generation
        if not manual_trump_generation:
            self._select_trump_automatically()

        #   manual trump selection
        else:
            self._select_trump_manually()

        # Everything is valid hence move on to next phase
        self.phase = Phase.BIDDING
    
    def _select_trump_automatically(self):  # THOUGHT: Could migrate to trump manager
        """
        Selects trump card automatically, assigning it to game_state,
        while also outputting information depending on the gamemode.
        """

        self.game_state.trump_suit = random.choice(SUITS)


        if self.gamemode == 'assistant':
            clear_screen()
            self.UIManager.print_random_trump_confirmation(state=self.game_state)
    
         *** # Currently at this part of the game engine, right after automatic trump selection, where I am converting it to round manager
    def handle_bidding_phase(self):
        """
        Bidding logic
        """
        # THOUGHT: Why do we get next round state for the initial bidding phase
        # shouldnt I check before enforcing this

        #starts the bidding process and must update state
        if self.gamemode == GameMode.ASSISTANT:
            self.state = self.biddingFlow.run(state=self.game_state)

        self.phase = Phase.PLAYING

    def handle_playing_phase(self):
        """
        Playing logic
        """
        max_cards_this_round = CARDS_PER_ROUND[self.game_state.round-1]

        # Loop through the number of cards in the round, as each player will play one card per trick
        # Assumes all the players start with the same amount of cards
        for _ in range(max_cards_this_round):
            self.play_out_trick()

        self.phase = Phase.SCORING

    def handle_redeciding_trump(self):
        """
        Docstring for handle_redeciding_trump
        """

        # redecide trump
        self.iterativeTrumpFlow = IterativeTrumpFlow()

        chosen_player = self.trumpManager.decide_trump(state=self.state)
        context = self.iterativeTrumpFlow.run(chosen_player)

        self.game_state.trump_suit = context['trump_suit']

        self.phase = Phase.BIDDING

    def handle_scoring_phase(self):
        """
        Scoring logic
        """
        if self.game_state.round < 6:  # 6
            self.game_state.round += 1
            #display total scoreboard

            # Total Score board is updated by itself now
            clear_screen(5)

            self.UIManager.print_total_score(self.state)

            # ACTION: Now hand_assignment
            self.phase = Phase.HAND_ASSIGNMENT  
        else:
            self.phase = Phase.GAME_OVER
            return

    def play_out_trick(self):
        """
        Logic for the functionality of the playing each trick
        """

        # Probably needs state now
        self.playingFlow = PlayingFlow()

        # THOUGHT: only need this for assistant mode maybe single player too
        # THOUFHT: Can not use get legal moves in ASsistant mode for non-perspective
        # Players as it needs to know what their hands consist of.
        player = self.game_state.next_player()
        legal_moves = self.game_state.get_legal_moves(player)

        if not legal_moves:
            raise ValueError("There is a duplicate card in play, please check assigned cards")

        while True:

            choice = self.playingFlow.play_turn(player, state=self.game_state)

            self.UIManager.print_choice_made(choice)
            
            if choice not in self.game_state.hands[player]:
                self.UIManager.print_invalid_choice_not_in_hand(choice)
                continue

            if choice not in self.game_state.get_legal_moves(player):
                self.UIManager.print_invalid_choice_not_legal(choice)
                continue

            if player == self.game_state.perspective:
                self.UIManager.print_perspective_choice_made(choice)
            else:
                self.UIManager.print_player_choice_made(player, choice)

            self.state = self.game_state.apply_move(player=player,
                                        card=choice)
            break  # successful play

    def _select_trump_manually(self):
        """Assigns trump suit to game state based on user input from
        manual trump selection flow"""

        selected_trump_suit = self.manual_trump_selection_flow.run()


        self.game_state.trump_suit = selected_trump_suit