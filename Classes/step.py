# contains variations of the Step class

from Classes.ui_manager import CLI_format_hand, scoreboard_display
from Utils.card_serialization import (
    SUIT_FROM_INITIAL,
    SUITS,
    get_suit_from_initial,
)
from Utils.cli_tools import *


class Step:
    """
    Abstract representation of a CLI step

    """
    def prompt(self, args: dict = {}) -> str:
        raise NotImplementedError

    def validate(self, user_input: str, args: dict = {}):
        raise NotImplementedError
    
    def feedback(self, value, args: dict = {}) -> str:
        raise NotImplementedError

class NumPlayerStep(Step):
    """
    Docstring for NumPlayerStep
    """

    def prompt(self, args: dict = {}) -> str:
        return "Enter number of players (3-6): "
    
    def validate(self, user_input: str, args: dict = {}):

        if user_input.lower() == "b":
            return "BACK"
        
        if not user_input.isdigit():
            raise ValueError("Must be a number")
        
        value = int(user_input)

        if value < 3 or value > 6:
            raise ValueError(" Players must be between 3 and 6")
        
        return value
    
    def feedback(self, value, args: dict = {}) -> str:
        clear_screen()
        return f"{value} Players selected"
        

class PlayerNameStep(Step):
    """
    Docstring for NamePlayerStep
    """

    def prompt(self, args: dict = {}) -> str:
        return "Enter player name: "
    
    def validate(self, user_input: str, args: dict = {}) -> str:

        if user_input.lower() == "b":
            return "BACK"
        
        if not user_input.isalpha():
            raise ValueError("Must a be valid name without numbers or special characters")
        
        value = str(user_input)

        if 20 < len(value) or len(value) < 2:
            raise ValueError(" Player name lengths must be 3-20 characters")
        
        return value
    
    def feedback(self, player_input, args: dict = {}) -> str:
        return (f'{player_input} created' )
    
class OpponentBooleanStep(Step):
    """
    Docstring for OpponentBooleanStep
    """

    def prompt(self, args: dict = {}) -> str:
        return "Is this player an opponent? (Y/n): "
    
    def validate(self, user_input: str, args: dict = {}):
        
        if user_input.lower() == "b":
            return "BACK"
        
        if user_input.lower() in ('y', 'n', ''):
            return user_input
        else:
            raise ValueError("Enter 'y' or 'n'")            
        
    
    def feedback(self, value, args: dict = {}) -> str:
        return ''
    
class BiddingMenuStep(Step):
    """
    Docstring for BiddingMenuStep
    """

    prompt_required_arguments = {"player", 
                                 "player_hand_str",
                                 "trump_suit",
                                 "current_bids",
                                 "forbidden_bid",
                                 "is_handicapped"}
    
    validate_required_arguments = {"forbidden_bid"}
    
    def prompt(self, args: dict = {}) -> str:

        missing = self.prompt_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context {missing}")

        player = args['player']
        player_hand_str = args['player_hand_str']        
        trump_suit = args['trump_suit']        
        current_bids = args['current_bids']
        forbidden_bid = args['forbidden_bid']
        is_handicapped = args['is_handicapped']

        if forbidden_bid > -1 and is_handicapped:
            bidding_line = f"""{player}, enter your bid (BANNED: {forbidden_bid}) > """
        else:
            bidding_line = f"{player} enter your bid > " 

        return f"""{player}'s turn bidding\n
Current bids: {current_bids}
Trump: {trump_suit}
Hand: {player_hand_str}

{bidding_line}"""

    
    def validate(self, user_input: str, args: dict = {}):
        
        #ensure the arguments passed suitable for the function
        missing = self.validate_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        forbidden_bid = args['forbidden_bid']
        
        if user_input.lower() == "b":
            return "BACK"
        
        if not user_input.isdigit():
            raise ValueError("\nMust enter a positive number")
        
        value = int(user_input)  # can convert as input must be a number
        
        if value == forbidden_bid:
            raise ValueError("\nIllegal bid, enter a legal bid")
        
        if 8 < value or value < 0:
            raise ValueError("\nMust enter a number from 0-8")
        
        return value
        
    
    def feedback(self, value, args: dict = {}) -> str:
        return ''
        
class TrumpSelectionStep(Step):
    """
    Docstring for TrumpSelectionStep
    """

    def prompt(self,
               args: dict) -> str:
        
        return "Manually enter initial trump value? (Y/n) "

    
    def validate(self,
                 user_input: str,
                 args: dict):
                
        if user_input.lower() == "b":
            return "BACK"
        
        if user_input.lower() in ('y', 'n', ''):
            return user_input
        else:
            raise ValueError("\nEnter 'y' or 'n'") 
                
    
    def feedback(self, value, args: dict = {}) -> str:

        option = 'Manual input'
        if value == 'n':
            option = 'Automatic generation'
        return f'{option} option chosen'
        
        
class ManualTrumpStep(Step):
    """
    Docstring for ManualTrumpStep
    """
    
    validate_required_arguments = {'player'}

    def prompt(self,
               args: dict) -> str:

        player = args['player']        
        return f""" {player} is deciding the trump suit.
        
[C] Clubs
[S] Spades
[H] Hearts
[D] Diamonds 

Enter trump suit initial: """

    
    def validate(self,
                 user_input: str,
                 args: dict):
        
        #ensure the arguments passed suitable for the function
        missing = self.validate_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        
        if user_input.lower() == "b":
            return "BACK"
        
        user_input = user_input.upper()

        if user_input not in SUIT_FROM_INITIAL:
            raise ValueError("\nMust enter a suit initial e.g 'H'")
        
        if len(user_input) != 1:
            raise ValueError("\nInvalid suit initial - must be singular character")
        
        if user_input == '':
            raise ValueError("\nMust enter an initial")
        
        return user_input
        
    
    def feedback(self, value, args: dict = {}) -> str:
        return f'\n{args["player"]} selected {get_suit_from_initial(value.upper())} as trump '
    
class PlayerPlayCardStep(Step):
    """
    Docstring for PlayerPlayCard

    Local player playing
    """
    
    prompt_required_arguments = {"player_name",
                                 "player_hand",
                                 "expanded_player_hand_str",
                                 "trump_suit",
                                 "table_str",
                                 "round_scoreboard"}
    
    validate_required_arguments = {"player"}


    def prompt(self,
               args: dict) -> str:

        #ensure the arguments passed suitable for the function
        missing = self.prompt_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        round_scoreboard = args['round_scoreboard']
        player_hand = args['player_hand']
        expanded_player_hand_str = args['expanded_player_hand_str']
        player_name = args['player_name']
        trump_suit = args['trump_suit']
        table_str = args['table_str']

        player_headline_string = f"▶\t {player_name} to play\t|\tTrump: {trump_suit}"
        round_scoreboard_string = f"Round score: {round_scoreboard}"
        if len(player_hand) > 1:
            choose_card_string = f"Choose card [1-{len(player_hand)}] > "
        else:
            choose_card_string = f"Choose card [1] > "       
        clear_screen() #3
        return (
            "".join([
                player_headline_string,
                "\n", 
                "\n", 
                round_scoreboard_string, 
                "\n",
                "\n",
                table_str,
                "\n",
                expanded_player_hand_str, 
                "\n",
                "\n",
                choose_card_string
            ]
            )
        )

    
    def validate(self,
                 user_input: str,
                 args: dict):
        
        #ensure the arguments passed suitable for the function
        missing = self.validate_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        player_hand = args['player_hand']
        
        if not user_input.isdigit():
            raise ValueError("Must enter a number")

        index = int(user_input)

        if  index < 1 or index > len(player_hand):
            raise ValueError(f"Must enter a valid number ({1}-{len(player_hand)})")
        
        if user_input == '':
            raise ValueError("Must enter a value")
        
        return index
        
    
    def feedback(self, value, args: dict = {}) -> str:
        #ensure the arguments passed suitable for the function

        return ''
    
class OpponentPlayCardStep(Step):
    """
    Docstring for OpponentPlayCardStep

    Opponent player playing
    """
    
    prompt_required_arguments = {"opponent_name",
                                 "opponent_hand_str" 
                                   "trump_suit",
                                   "table_str",
                                   "round_scoreboard",}
    
    validate_required_arguments = {"valid_card_initials"}

    def prompt(self,
               args: dict) -> str:

        #ensure the arguments passed suitable for the function
        missing = self.prompt_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        round_scoreboard = args['round_scoreboard']
        opponent_hand_str = args['opponent_hand_str']
        opponent_name = args['opponent_name']
        trump_suit = args['trump_suit']
        table_str = args['table_str']
        
        player_headline_string = f"▶\t{opponent_name} to play\t|\tTrump: {trump_suit}"
        round_scoreboard_string = f"Round score: {round_scoreboard}"
        choose_card_string = f"Enter initials of card e.g. '7H' > "
        
        clear_screen() #3
        return (
            "".join([
                player_headline_string,
                "\n", 
                "\n", 
                round_scoreboard_string, 
                "\n",
                "\n",
                table_str,
                "\n",
                "\n",
                opponent_hand_str, 
                "\n",
                "\n",
                choose_card_string
            ]
            )
        )

    
    def validate(self,
                 user_input: str,
                 args: dict):
        
        #ensure the arguments passed suitable for the function
        missing = self.validate_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        card_initials = args['valid_card_initials']
        
        user_input = user_input.upper()

        if user_input not in card_initials:
            raise ValueError("Must enter a valid card initial e.g '7H'")
        
        if len(user_input) < 2 or len(user_input) > 3:
            raise ValueError("Invalid card initial - must be 2-3 characters long")
        
        if user_input == '':
            raise ValueError("Must enter a value")
        
        return user_input
        
    
    def feedback(self, value, args: dict = {}) -> str:
        #ensure the arguments passed suitable for the function

        return ''
    

class LocalAddCardStep(Step):

    "First prompt for Local Add Card Step"

    prompt_required_arguments = {"player"}

    def prompt(self,
               args: dict) -> str:

        #ensure the arguments passed suitable for the function
        missing = self.prompt_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        player = args['player']

        player_assignment_line = f"Assigning cards to: {player}"
        enter_line = f"Press Enter to continue > "

        clear_screen()
        
        return "".join([
            player_assignment_line, 
            "\n",
            enter_line
            ])

    def validate(self,
                 user_input: str,
                 args: dict):
        
        return ''
        
    
    def feedback(self, value, args: dict = {}) -> str:

        return ''

class IterableLocalAddCardStep(Step):
    """
    Docstring for LocalAddCardStep

    Step for adding card to local player's hand
    """
    
    prompt_required_arguments = {"player_hand",
                                 "maximum_cards",
                                 "player_hand_str"}
    
    validate_required_arguments = {"valid_card_initials"}

    def prompt(self,
               args: dict) -> str:

        #ensure the arguments passed suitable for the function
        missing = self.prompt_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        player_hand = args['player_hand']
        player_hand_str = args['player_hand_str']
        max_cards = args['maximum_cards']

        cards_remaining_line = f"Cards remaining: {max_cards-len(player_hand)}"
        prompt_line = "Enter card initials (e.g. JH, 10D) > "
        
        return (
            "".join([
                "\n",
                cards_remaining_line,
                "\n",
                player_hand_str,
                "\n",
                prompt_line
                ]
            )
        )

    
    def validate(self,
                 user_input: str,
                 args: dict):
        
        #ensure the arguments passed suitable for the function
        missing = self.validate_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        card_initials = args['valid_card_initials']

        user_input = user_input.upper()
        
        if user_input not in card_initials:
            raise ValueError("Must enter a valid card initial e.g '7H'")
        
        if len(user_input) < 2 or len(user_input) > 3:
            raise ValueError("Invalid card initial - must be 2-3 characters long")
        
        if user_input == '':
            raise ValueError("Must enter a value")
        
        return user_input
        
    
    def feedback(self, value, args: dict = {}) -> str:

        return ''