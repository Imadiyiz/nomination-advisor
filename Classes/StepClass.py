# contains variations of the Step class

from Utils.tools import clear_screen
from .PlayerClass import Player

class Step:
    """
    Abstract representation of a CLI step

    """
    key = None # used for state storage

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

    key = 'num_players'

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

    key = 'player_name'

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

    key = 'is_opponent'

    def prompt(self, args: dict = {}) -> str:
        return "Is this player an opponent? (Y/n): "
    
    def validate(self, user_input: str, args: dict = {}):
        
        if user_input.lower() == "b":
            return "BACK"
        
        if user_input.lower() in ('y', 'n', ''):
            return ''
        else:
            raise ValueError("Enter 'y' or 'n'")            
        
    
    def feedback(self, value, args: dict = {}) -> str:
        return ''
    
class BiddingMenuStep(Step):
    """
    Docstring for BiddingMenuStep
    """

    key = 'bid_menu'

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

    key = 'choose_bid'
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

    key = 'trump_selected'

    def prompt(self,
               args: dict) -> str:
        
        return "Manually enter initial trump value? (Y/n)"

    
    def validate(self,
                 args: dict,  
                 user_input: str):
                
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

    key = 'manual_trump'
    
    validate_required_arguments = {"valid_card_initials"}

    def prompt(self,
               args: dict) -> str:
        
        return (f"""Enter the initial trump card from the IRL game.\n 
                (Format: '10D' = 10 of Diamonds)\n 
                ('KS' = King of Spades)
                """
        )

    
    def validate(self,
                 args: dict,  
                 user_input: str):
        
        #ensure the arguments passed suitable for the function
        missing = self.validate_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        card_initials = args['valid_card_initials']
        
        if user_input.lower() == "b":
            return "BACK"
        
        if user_input not in card_initials:
            raise ValueError("Must enter a valid card initial e.g '7H'")
        
        if len(user_input) < 2 or len(user_input) > 3:
            raise ValueError("Invalid card initial - must be 2-3 characters long")
        
        if user_input == '':
            raise ValueError("Must enter a value")
        
        return user_input
        
    
    def feedback(self, value, args: dict = {}) -> str:
        return ''
    
class PlayerPlayCard(Step):
    """
    Docstring for PlayerPlayCard

    Local player playing
    """

    key = 'play_card'
    
    prompt_required_arguments = {"player", 
                                   "trump_suit",
                                   "stack",
                                   "scoreboard"}
    
    validate_required_arguments = {"player"
    ""}

    feedback_required_arguments = {
        "player", "card"
    }

    def prompt(self,
               args: dict) -> str:

        #ensure the arguments passed suitable for the function
        missing = self.prompt_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        round_scoreboard = args['scoreboard']
        player = args['player']
        trump_suit = args['trump_suit']
        stack_str = args['stack']
        
        return (f"""
                {player.name} STARTS PLAYING

                ROUND SCOREBOARD{round_scoreboard}
                TRUMP: {trump_suit}
                HAND:\n {player.display_hand_str()}
                STACK: {stack_str}

                ENTER THE INDEX VALUE OF THE CARD YOU WANT TO PLAY
                INPUT RANGE: {1}-{len(player.hand)}\n"""
        )

    
    def validate(self,
                 args: dict,  
                 user_input: str):
        
        #ensure the arguments passed suitable for the function
        missing = self.validate_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        player = args['player']
        
        if user_input.lower() == "b":
            return "BACK"
        
        if not user_input.isdigit():
            raise ValueError("Must enter a number")

        if user_input not in range(1, len(player.hand)+1):
            raise ValueError(f"Must enter a valid number ({1}-{len(player.hand)})")
        
        if user_input == '':
            raise ValueError("Must enter a value")
        
        return user_input
        
    
    def feedback(self, value, args: dict = {}) -> str:
        #ensure the arguments passed suitable for the function
        missing = self.feedback_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        player = args['player']
        card = args['card']

        return (f"{player.name} played {card}")
    
class OpponentPlayCard(Step):
    """
    Docstring for OpponentPlayCard

    Opponent player playing
    """

    key = 'play_card'
    
    prompt_required_arguments = {"opponent", 
                                   "trump_suit",
                                   "stack",
                                   "scoreboard"}
    
    validate_required_arguments = {"valid_card_initials"}

    feedback_required_arguments = {
        "opponent", "card"}

    def prompt(self,
               args: dict) -> str:

        #ensure the arguments passed suitable for the function
        missing = self.prompt_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        scoreboard = args['scoreboard']
        opponent = args['opponent']
        trump_suit = args['trump_suit']
        stack_str = args['stack']
        
        return (f"""
                {opponent.name} STARTS PLAYING

                ROUND SCOREBOARD {scoreboard.round_scoreboard}
                TRUMP: {trump_suit}
                HAND: {opponent.display_hand_str()}
                STACK: {stack_str}

                ENTER THE INITIALS OF THE CARD THE OPPONENT WANTS TO PLAY
        """)

    
    def validate(self,
                 args: dict,  
                 user_input: str):
        
        #ensure the arguments passed suitable for the function
        missing = self.validate_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
                
        if user_input.lower() == "b":
            return "BACK"
        
        card_initials = args['valid_card_initials']
        
        if user_input.lower() == "b":
            return "BACK"
        
        if user_input not in card_initials:
            raise ValueError("Must enter a valid card initial e.g '7H'")
        
        if len(user_input) < 2 or len(user_input) > 3:
            raise ValueError("Invalid card initial - must be 2-3 characters long")
        
        if user_input == '':
            raise ValueError("Must enter a value")
        
        return user_input
        
    
    def feedback(self, value, args: dict = {}) -> str:
        #ensure the arguments passed suitable for the function
        missing = self.feedback_required_arguments - args.keys()
        if missing:
            raise RuntimeError(f"Missing context: {missing}")
        
        opponent = args['opponent']
        card = args['card']

        return (f"{opponent.name} played {card}")