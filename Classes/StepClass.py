# contains variations of the Step class

from Utils.tools import clear_screen
from .PlayerClass import Player
from Utils.ViewFormat import *


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
        clear_screen(0)
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
                                 "trump_suit",
                                 "current_bids",
                                 "max_cards",}
    
    def prompt(self, args: dict = {}) -> str:

        missing = self.prompt_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context {missing}")

        player = args['player']        
        trump_suit = args['trump_suit']        
        current_bids = args['current_bids']
        max_cards = args['max_cards']

        return f"""{player}'s TURN BIDDING

                CURRENT BIDS: {current_bids}
                TRUMP: {trump_suit.upper()}
                HAND: {player.display_hand_str(max_cards)}
                
                PRESS ENTER TO CONTINUE...
                """

    
    def validate(self, user_input: str, args: dict = {}):
        
        if user_input.lower() == "b":
            return "BACK"
        
        return '' 
        
    
    def feedback(self, value, args: dict = {}) -> str:
        return ''
        
class BiddingStep(Step):
    """
    Docstring for BiddingStep
    """

    prompt_required_arguments = {"player", 
                                 "forbidden_bid",}
    
    validate_required_arguments = {"forbidden_bid"}

    def prompt(self,
               args: dict = {}) -> str:
        
        #ensure the arguments passed suitable for the function
        missing = self.prompt_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        forbidden_bid = args['forbidden_bid']
        player = args['player']
        
        return (f"ENTER BID (BANNED: {forbidden_bid})\n" 
                if player.handicapped_bid and forbidden_bid > -1 
                else "ENTER BID\n"
        )

    
    def validate(self,
                 user_input: str,
                 args: dict = {}):
        
        #ensure the arguments passed suitable for the function
        missing = self.validate_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        forbidden_bid = args['forbidden_bid']
        
        if user_input.lower() == "b":
            return "BACK"
        
        if not user_input.isdigit():
            raise ValueError("Must enter a positive number")
        
        value = int(user_input)  # can convert as input must be a number
        
        if value == forbidden_bid:
            raise ValueError("Illegal bid, enter a legal bid")
        
        if 8 < value or value < 0:
            raise ValueError("Must enter a number from 0-8")
        
        
        return value
        
    
    def feedback(self, value, args: dict = {}) -> str:
        return ''
        
class TrumpSelectionStep(Step):
    """
    Docstring for TrumpSelectionStep
    """

    def prompt(self,
               args: dict) -> str:
        
        return "Manually enter initial trump value? (Y/n)"

    
    def validate(self,
                 user_input: str,
                 args: dict):
                
        if user_input.lower() == "b":
            return "BACK"
        
        if user_input.lower() in ('y', 'n', ''):
            return user_input
        else:
            raise ValueError("Enter 'y' or 'n'") 
                
    
    def feedback(self, value, args: dict = {}) -> str:

        option = 'Manual input'
        if value == 'n':
            option = 'Automatic generation'
        return f'{option} option chosen'
        
class ManualTrumpStep(Step):
    """
    Docstring for ManualTrumpStep
    """
    
    validate_required_arguments = {"valid_card_initials"}

    def prompt(self,
               args: dict) -> str:
        
        return (f"""Enter the initial trump card from the IRL game.\n 
                (Format: '10D' = 10 of Diamonds)\n 
                ('KS' = King of Spades)
                """
        )

    
    def validate(self,
                 user_input: str,
                 args: dict):
        
        #ensure the arguments passed suitable for the function
        missing = self.validate_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        card_initials = args['valid_card_initials']
        
        if user_input.lower() == "b":
            return "BACK"
        
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
    
class PlayerPlayCardStep(Step):
    """
    Docstring for PlayerPlayCard

    Local player playing
    """
    
    prompt_required_arguments = {"player", 
                                   "trump_suit_symbol",
                                   "table",
                                   "scoreboard"}
    
    validate_required_arguments = {"player"
    ""}


    def prompt(self,
               args: dict) -> str:

        #ensure the arguments passed suitable for the function
        missing = self.prompt_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        scoreboard = args['scoreboard']
        player = args['player']
        trump_suit_symbol = args['trump_suit_symbol']
        table = args['table']

        player_headline_string = f"▶\t {player.name} to play\t|\tTrump: {trump_suit_symbol} "
        round_scoreboard_string = f"Round score: {scoreboard.display()}"
        table_string = f"Table:\n{table.display_stack()}"
        hand_string = f"Hand:\n{format_hand(player.hand)}"
        choose_card_string = f"Choose card [1-{len(player.hand)}] > "
        
        return (
            "".join([
                player_headline_string,
                "\n", 
                "\n", 
                round_scoreboard_string, 
                "\n",
                "\n",
                table_string,
                "\n",
                "\n",
                hand_string, 
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
        
        player = args['player']
        
        if not user_input.isdigit():
            raise ValueError("Must enter a number")

        index = int(user_input)

        if  index < 1 or index > len(player.hand):
            raise ValueError(f"Must enter a valid number ({1}-{len(player.hand)})")
        
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
    
    prompt_required_arguments = {"opponent", 
                                   "trump_suit_symbol",
                                   "table",
                                   "scoreboard",}
    
    validate_required_arguments = {"valid_card_initials"}

    def prompt(self,
               args: dict) -> str:

        #ensure the arguments passed suitable for the function
        missing = self.prompt_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        scoreboard = args['scoreboard']
        opponent = args['opponent']
        trump_suit_symbol = args['trump_suit_symbol']
        table = args['table']
        
        player_headline_string = f"▶\t{opponent.name} to play | Trump: {trump_suit_symbol}"
        round_scoreboard_string = f"Round score: {scoreboard.display()}"
        table_string = f"Table:\n{table.display_stack()}"
        hand_string = f"Hand:\n{format_hand(opponent.hand)}"
        choose_card_string = f"Enter initials of card e.g. '7H' > "
        
        #clear_screen()
        return (
            "".join([
                player_headline_string,
                "\n", 
                "\n", 
                round_scoreboard_string, 
                "\n",
                "\n",
                table_string,
                "\n",
                "\n",
                hand_string, 
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
    
    prompt_required_arguments = {"player", "maximum_cards"}
    
    validate_required_arguments = {"valid_card_initials"}

    def prompt(self,
               args: dict) -> str:

        #ensure the arguments passed suitable for the function
        missing = self.prompt_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        player = args['player']
        max_cards = args['maximum_cards']

        cards_remaining_line = f"Cards remaining: {max_cards-len(player.hand)}"
        current_hand_line = f"Current Hand:\n {player.display_hand_str()} "
        prompt_line = "Enter card initials (e.g. JH, 10D) > "
        
        return (
            "".join([
                "\n",
                cards_remaining_line,
                "\n",
                current_hand_line,
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