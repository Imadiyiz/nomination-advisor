# Contents for the table class in the Nomination game

from .CardClass import Card

class Table:
    """
    Manages the stack of cards during each round.

    This class handles:
    - Adding and validating played cards
    - Determining the winning card in the stack
    - Resetting the table between rounds
    """

    def __init__(self, UIManager):
        """
        Initialises the Table object

        Args:
            UIManager (UIManager): The UI manager instance for displaying messages
        """

        self.stack = list()
        self.winning_suit = None
        self.UIManager = UIManager

    
    def display_stack(self, visual: bool = False) -> str:
        """
        Returns the string representation of the current stack
        
        Args:
        visual (bool): If True, returns ASCII-style card pictures.
        If False, returns simple string names.

        Returns: 
            str: Formatted representation of the stack,
            or a message if the stack is empty 
        """

        if self.stack:
            string = ""
            for card in self.stack:
                string += f"{card.picture if visual else str(card)}\n"
            return string
        return "Stack is currently empty" 

    def add_to_stack(self, card: Card = None):
        """
        Adds a card to the table stack

        Note: The caller must ensure the card is removed from the player's hand.
        
        Args:
            card (Card): The card to add to the stack.
        """
        self.stack.append(card)

    
    def valid_add_to_stack(self, card: Card = None, player_hand: list = []) -> bool:
        """
        Validates whether a card can be played based on suit-following rules.
        
        Args:
            card (Card): The card the player wants to play
            player_hand (list[Card]): The player's current hand.

        Returns:
            bool: True if the play is valid, False otherwise.
            Displays a message if invalid.
        """

        if self.stack: 
            first_card = self.stack[0] # gets the first card in stack
            
            must_follow_suit = any(
                hand_card.suit[0].lower() == first_card.suit[0].lower()
                for hand_card in player_hand
            ) # True if any of the cards' suits match the first card
            
            #must play first card suit
            if must_follow_suit and card.suit[0].lower() != first_card.suit[0].lower():
                self.UIManager.display_message(
                    f"INVALID CARD CHOICE - WRONG SUIT: MUST BE {first_card.suit[0]}")
                return False
        return True


    def verify_winner(self, trump_suit: str) -> Card:
        """
        Determines who is currently winning the stack on the table

        Args:
            trump_suit (str): The trump suit used to prioritise winning cards

        Returns: 
            Card: The winning card based on the rules. Returns None if stack is empty
        """
        #reset winning card and suits
        winning_card = None

        #checks whether the stack has been trumped
        trumped = any(card.suit[0].lower() == trump_suit.lower() for card in self.stack)

        #trumped cards are in the stack
        if trumped:
            for card in self.stack:
                if card.suit[0].lower() == trump_suit.lower():
                    if winning_card is None or card.value[1] > winning_card.value[1]:
                        winning_card = card
        else:
        #No trumps in stack
            for card in self.stack:
                if winning_card:
                    if card.suit[0].lower() == self.winning_suit.lower() and card.value[1] > winning_card.value[1]:
                        winning_card = card
                else:
                    winning_card = card
                    self.winning_suit = card.suit[0].lower()

        return winning_card

    def reset(self):
        """
        Resets the table by clearing the stack and winning suit
        """

        self.winning_suit = None
        self.stack = list()
