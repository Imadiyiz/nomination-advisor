# Contents of the GameManager class

from .TableClass import Table
from .DeckClass import Deck
from .PlayerClass import Player
import random
from .ScoreboardClass import Scoreboard
from .UIManager import UIManager
from .BiddingManager import BiddingManager
from .PlayerStateManager import PlayerStateManager
from .TrumpManager import TrumpManager
from Utils.tools import clear_screen
from .StepClass import *
from .PlayerSetupFlow import PlayerSetupFlow
from .BiddingFlow import BiddingFlow
from .InitialTrumpFlow import InitialTrumpFlow
from .PlayingFlow import PlayingFlow
from .LocalCardAssignmentFlow import LocalCardAssignmentFlow
from enum import Enum
from .CardClass import Card

class Phase(Enum):
        PLAYER_SELECTION = "player_selection"
        HAND_ASSIGNMENT = 'hand_assignment'
        TRUMP_SELECTION = "trump_selection"
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
        self.cards_per_round = [8,7,6,6,7,8]
        self.phases = {
            Phase.PLAYER_SELECTION: self.handle_player_selection,
            Phase.HAND_ASSIGNMENT: self.handle_hand_assignment,
            Phase.TRUMP_SELECTION: self.handle_trump_selection,
            Phase.BIDDING: self.handle_bidding_phase,
            Phase.PLAYING: self.handle_playing_phase,
            Phase.SCORING: self.handle_scoring_phase,
        }

        #initial phase
        self.phase = Phase.PLAYER_SELECTION
        self.trump_suit = ''

        self.player_set = set()
        self.player_queue = [] #queue for playing during rounds
        self.original_queue = [] #queue for after round when winning the hand does not affect the order

        #IF SHUFFLE IS NECEESARY
        #places the shuffled players into the actual list in their new order
        #random.shuffle(self.player_queue)
        
        #run gameloop after creating the game   

    def start(self):
        self.create_game()
        self.run_game_phases()
        clear_screen(2)    

    def create_game(self):
        """
        Initialises the game and the objects it requires. 

        """        
        #generate deck
        self.deck = Deck()

        #Generates objects for the game
        self.scoreboard = Scoreboard(self.player_set)
        self.UIManager = UIManager()
        self.table = Table(self.UIManager)
        self.biddingManager = BiddingManager(self.UIManager)
        self.playerStateManager = PlayerStateManager(self.player_set)
        self.trumpManager = TrumpManager(self.UIManager)
        self.playerSetupFlow = PlayerSetupFlow()
        self.biddingFlow = BiddingFlow(self.player_queue)
        self.initialTrumpFlow = InitialTrumpFlow()
        self.playingFlow = PlayingFlow(
            self.table,
            self.scoreboard,
            self.deck.generate_valid_card_initials())
        self.localCardAssignmentFlow = LocalCardAssignmentFlow(
            self.deck.generate_valid_card_initials())

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
        Player selection logic

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

        self.phase = Phase.HAND_ASSIGNMENT

    def handle_hand_assignment(self):
        """
        Docstring for handle_hand_assignment

        Handles hand assingment for both types of players
        
        """

        for player in self.player_queue:

            if player.opponent:
                for _ in range(self.cards_per_round[self.round-1]):
                    card = self.deck.deck.pop()
                    player.hand.append(card)
                    player.own_hand()
                continue
            
            #iterate for amount of cards in hand for the current round
            while len(player.hand) < self.cards_per_round[self.round-1]:

                choice_of_initials = self.localCardAssignmentFlow.assign_card(
                    player
                )
                
                # choice of initials has already been sanitised
                chosen_card = self.deck.draw_card_from_initials(choice_of_initials)
                if chosen_card:
                    player.hand.append(chosen_card)
                    player.own_hand()
                else:
                    print(f"This card has already been played")
        

        self.phase = Phase.TRUMP_SELECTION

    def handle_trump_selection(self):
        """
        Docstring for trump_selection
        
        """

        context = self.initialTrumpFlow.run(self.deck.valid_card_initials)
        manual_trump_generation = context['manual_trump_generation']
        trump_card_initials = context['trump_card_initials']

        #   automatic trump generation
        if not manual_trump_generation:
            self.select_trump_automatically()
        #   need to allocate trump and selected card from deck

        #   manual trump selection
        else:
            card = self.deck.draw_card_from_initials(trump_card_initials)
            if not card:
                print("Invalid card")
                return
        
            self.trump_suit = card.suit[0]
            self.deck.remove_card(card)

        self.phase = Phase.BIDDING
    
    def select_trump_automatically(self):

        trump_card = self.deck.deck[0]
        self.deck.remove_card(trump_card)

        #determine trump
        #since deck is already shuffled, pick first card
        # choose the trump after cards have been assinged to players
        self.trump_suit = trump_card.suit[0]
        print("\nDECIDING INITIAL TRUMP")
        print("CARD RANDOMLY CHOSEN:: ", str(trump_card))
        print("TRUMP SUIT:: ", self.trump_suit, "\n")
    

    def handle_bidding_phase(self):
        """
        Bidding logic
        """

        self.max_cards = self.cards_per_round[self.round-1]
        self.playerStateManager.reset_players_handicap()

        #dealer shifts every time bidding starts
        if self.round > 1:
            self.original_queue = self.playerStateManager.update_dealer_order(self.original_queue)
            self.player_queue = self.original_queue
        
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
        for _ in range(cards):
            self.start_round()
        self.phase = Phase.SCORING
        if self.round > 1:
            self.trump_suit = self.trumpManager.decide_trump(player_set=self.player_set, current_trump=self.trump_suit)
    
    def handle_scoring_phase(self):
        """
        Scoring logic
        """
        if self.round < 6:
            self.round += 1
            self.phase = Phase.BIDDING
            #display total scoreboard
            self.scoreboard.update_total_scoreboard(self.player_queue, max_cards=self.max_cards)
            self.UIManager.display_message(self.scoreboard.display(round=False))
        else:
            self.phase = Phase.GAME_OVER

    def start_round(self):
        """
        Logic for the functionality of the playing round

        """
        self.table.reset()
        self.scoreboard.reorder_round_scoreboard(player_queue=self.player_queue)
         
        for player in self.player_queue:

            choice = self.playingFlow.play_turn(
                player=player,
                trump_suit=self.trump_suit)
                
            if player.opponent:
                selected_card = self._materialise_played_card(player, choice)
                self._remote_play_card(player, selected_card)
            else:
                selected_card = player.hand[choice-1]
                self._local_play_card(player, selected_card)  

        self.score_hand()
          
            

    def _local_play_card(self, player:Player, selected_card: Card):
        """
        Plays card to the table for local player and removes card from hand
        """

        self.table.play_card_to_table(
                selected_card, player
            )

        #after playing the card remove it from the player hand
        player.remove_card(card=selected_card)

    def _remote_play_card(self, player: Player, selected_card: Card):
        """
        Plays card to the table for remote player and removes it from the deck
        """
        self.deck.remove_card(selected_card)
        self.table.play_card_to_table(selected_card, player)
        
        
    def score_hand(self):
        """
        Scores on a play by play basis (multiple times per round)
        """

        winner_card = self.table.verify_winner(trump_suit=self.trump_suit)
        winning_player = winner_card.owner
        print(f"DONE, {winning_player} is the winner with {winner_card}")
        
        self.scoreboard.update_round_scoreboard(
            self.player_set, 
            winner_card=winner_card)
    
        self.player_queue = self.playerStateManager.update_winner_order(
            winner=winning_player, 
            player_queue=self.player_queue)

    def _materialise_played_card(self, player:Player, choice: str):
        """
        Turns a declared card into a real Card instance and assigns
        the card owner to the player
        choice is the initials for the card
        """
        card = self.deck.draw_card_from_initials(choice)
        if not card:
            raise ValueError(f"Card {choice} does not exist or already played")

        card.owner = player
        return card
