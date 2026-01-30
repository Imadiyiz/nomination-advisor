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
            "player_selection": self.player_selection,
            "trump_selection": self.trump_selection,
            "bidding": self.handle_bidding_phase,
            "playing": self.handle_playing_phase,
            "scoring": self.handle_scoring_phase,
        }

        #initial phase
        self.phase = "player_selection"
        self.trump_suit = ''

        self.player_set = set()
        self.player_queue = [] #queue for playing during rounds
        self.original_queue = [] #queue for after round when winning the hand does not affect the order

        #IF SHUFFLE IS NECEESARY
        #places the shuffled players into the actual list in their new order
        #random.shuffle(self.player_queue)
        
        #run gameloop after creating the game

        self.create_game()
        self.run_game()
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

    def run_game(self):
        """
        Starts the game 
        """
        while self.phase != "game_over":
                _phase_handler = self.phases.get(self.phase)
                if _phase_handler:
                    _phase_handler() # function from the dictionary is performed
                else:
                    raise ValueError(f"Unknown game phase: {self.phase}") 

        
    def player_selection(self):
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

        self.phase = "trump_selection"
        
    def trump_selection(self):
        """
        Docstring for trump_selection
        
        """

        context = self.initialTrumpFlow.run(self.deck.valid_card_initials)
        manual_trump_generation = context['manual_trump_generation']
        trump_card_initials = context['trump_card_initials']
        picture_initials = ['J', 'Q', 'K', 'A']

        # need to allocate trump and selected card from deck
        if manual_trump_generation:
            for suit in self.deck.suit_gen:
                if trump_card_initials[-1].upper() == suit[0][0]:
                    trump_value = trump_card_initials[:-1]  # removes last character to leave just the number
                    if trump_value.isalpha():
                        for index, char in enumerate(picture_initials):
                            if char == trump_value:
                                integer_trump_value = 11 + index

                    else:
                        integer_trump_value = trump_value

                    self.deck.remove_card(suit[0][0], integer_trump_value)
                    self.trump_suit = suit[0][0]


        # automatic trump generation
        else:
            trump_card = self.deck.deck[0]
            self.deck.remove_card(trump_card.suit[0], trump_card.value[0])

            #determine trump
            #since deck is already shuffled, pick first card
            # choose the trump after cards have been assinged to players
            self.trump_suit = trump_card.suit[0]
            print("\nDECIDING INITIAL TRUMP")
            print("CARD RANDOMLY CHOSEN:: ", self.deck.deck[0])
            print("TRUMP SUIT:: ", self.trump_suit, "\n")

        self.phase = 'bidding'
        return


    def handle_bidding_phase(self):
        """
        Bidding logic
        """

        self.max_cards = self.cards_per_round[self.round-1]
        self.playerStateManager.reset_players_handicap()

        #dealer shifts eveery time bidding starts
        if self.round > 1:
            self.original_queue = self.playerStateManager.update_dealer_order(self.original_queue)
            self.player_queue = self.original_queue
        
        self.player_queue[-1].handicapped_bid = True
        self.biddingManager.reset_bids(self.player_queue)
        self.biddingManager.update_current_bids(self.player_queue)
        self.deck.generate_deck()

        #starts the bidding process
        self.biddingManager.start_bidding(trump_suit=self.trump_suit,
                                        round_no=self.round, player_queue=self.player_queue,
                                        max_cards=self.max_cards)
        self.phase = "playing"

    def handle_playing_phase(self):
        """
        Playing logic
        """
        cards = self.cards_per_round[self.round-1]
        for _ in range(cards):
            self.start_round()
            self.score_hand()
        self.phase = "scoring"
        if self.round > 1:
            self.trump_suit = self.trumpManager.decide_trump(player_set=self.player_set, current_trump=self.trump_suit)
    
    def handle_scoring_phase(self):
        """
        Scoring logic
        """
        if self.round < 6:
            self.round += 1
            self.phase = "bidding"
            #display total scoreboard
            self.scoreboard.update_total_scoreboard(self.player_queue, max_cards=self.max_cards)
            self.UIManager.display_message(self.scoreboard.display(round=False))
        else:
            self.phase = "game_over"

    def start_round(self):
        """
        Function for the functionality of the playing round

        "Remember to shuffle the order of the player list so that the person in first position is now last"
        """
        user_choice = ""
        self.table.reset()
        self.scoreboard.reorder_round_scoreboard(player_queue=self.player_queue)

        for player in self.player_queue:
            run = True
            while run:
                    if player.computer:
                        for card in player.hand:
                            if self.table.valid_add_to_stack(player_hand=player.hand,
                                                            card=card):
                                self.table.add_to_stack(card=card)
                                self.UIManager.display_message(f"{player.name} played a {card}")
                                player.remove_card(card)
                                break
                        run = False
                    else:
                       
                        #logic for selecting a card to add to the stack
                        user_choice  = self.UIManager.get_player_input(
                            self.display_ingame_menu(player))
                        if user_choice[0].isdigit():
                            user_choice = int(user_choice[0])
                            if user_choice <= len(player.hand):
                                if self.table.valid_add_to_stack(card=player.hand[user_choice], 
                                                                player_hand = player.hand):
                                    #if valid then add it to the queue
                                    self.table.add_to_stack(card=player.hand[user_choice])
                                    player.remove_card(card=player.hand[user_choice])
                                    run = False
                            else:
                                self.UIManager.display_message(f"INVALID CARD CHOICE - OPTION MUST BE LESS THAN MAX LENGTH")
                        else:
                            self.UIManager.display_message("INVALID OPTION")
        print("DEBUG: Complete round")

    def score_hand(self):
        """
        Scores on a play by play basis (multiple times per round)
        """

        winner_card = self.table.verify_winner(trump_suit=self.trump_suit)
        winning_player = winner_card.owner
        self.UIManager.display_message(message=f"DONE, {winning_player} is the winner with {winner_card}")
        self.scoreboard.update_round_scoreboard(self.player_set, winner_card=winner_card)
        self.player_queue = self.playerStateManager.update_winner_order(winner=winning_player, player_queue=self.player_queue)

    def display_ingame_menu(self, player:Player) -> str:
        """
        Displays the menu for the player during the round

        The menu includes:
        PLAY_cARD, 
        """
        round_scoreboard = self.scoreboard.display()
        stack_str = self.table.display_stack()
        _string = f"""
                    {player.name} STARTS PLAYING

                    ROUND SCOREBOARD{round_scoreboard}
                    TRUMP: {self.trump_suit}
                    HAND:\n {player.display_hand_str()}
                    STACK: {stack_str}
                    ENTER THE INDEX VALUE OF THE CARD YOU WANT TO PLAY
                    INPUT RANGE: {0}-{len(player.hand)-1}\n"""
        return _string
