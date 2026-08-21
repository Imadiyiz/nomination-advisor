# Contents for the table class in the Nomination game

from Utils.types import TrumpStr

from .card import Card
from .player import Player


class Table:
    """
    Manages the stack of cards during each round.

    This class handles:
    - Adding and validating played cards
    - Determining the winning card in the stack
    - Resetting the table between rounds
    """

    def __init__(self, UIManager, stack: list[Card] = []):
        """
        Initialises the Table object

        Args:
            UIManager (UIManager): The UI manager instance for displaying messages
        """

        self.stack = stack
        self.UIManager = UIManager

    
    def display_stack(self) -> str:
        """
        Returns the string representation of the current stack
    
        Returns: 
            str: Formatted representation of the stack,
            or a message if the stack is empty 
        """

        if self.stack:

            _reversed_stack = self.stack
            _reversed_stack = reversed(_reversed_stack)
            string = ""

            for card in _reversed_stack:
                if len(card.initials) >= 3:
                     string += f"{card}   ~  {card.owner}\n"
                else:
                     string += f" {card}   ~  {card.owner}\n"
            return string
        return "(Empty)" 

    def _add_to_stack(self, card: Card):
        """
        Adds a card to the table stack

        Note: The caller must ensure the card is removed from the player's hand.
        
        Args:
            card (Card): The card to add to the stack.
        """
        self.stack.append(card)

    
    def _valid_add_to_stack(self, card: Card, player_hand: list[Card], trump_suit: TrumpStr) -> bool:
        """
        Validates whether a card can be played based on suit-following rules.
        
        Args:
            card (Card): The card the player wants to play
            player_hand (list[Card]): The player's current hand.
            trump_suit(int): Ensures that the player is able to override common rules if trumped

        Returns:
            bool: True if the play is valid, False otherwise.
            Displays a message if invalid.
        """

        if self.stack: 

            if card.suit == trump_suit:
                 return True
            
            first_card = self.stack[0] # gets the first card in stack

            first_suit = first_card.suit
            
            # True if any of the cards' suits match the first card
            must_follow_suit = self._has_suit(hand=player_hand,
                                              suit=first_suit)
            #must play first card suit
            if must_follow_suit and card.suit[0].lower() != first_card.suit[0].lower():
                if first_card.suit != trump_suit:
                    print(
                    f"Invalid card choice - Must be {first_card.suit} or {trump_suit} suit")
                else:
                    print(f"Invalid card choice - Must be {trump_suit} suit") 
                return False
        return True


    def verify_winner(self, trump_suit: TrumpStr) -> Card:
        """
        Rules:
        1. Trump suit beats all other suits
        2. If no trump is played, highest card of the leading suit wins

        Args:
            trump_suit (TrumpStr): The trump suit used to prioritise winning cards

        Returns: 
            Card: The winning card based on the rules. Returns None if stack is empty
        """

        if not self.stack:
            raise ValueError("No stack on the table, cannot verify winner")
        
        trump_suit = trump_suit.lower()
        first_suit = self.stack[0].suit.lower()

        #gets all the trump cards in the current stack
        trump_cards = [c for c in self.stack if c.suit.lower() == trump_suit]

        if trump_cards:
            return max(trump_cards, key=lambda c: c.value)
        
        follow_suit_cards = [
        c for c in self.stack if c.suit.lower() == first_suit]

        return max(follow_suit_cards, key=lambda c: c.value)

    def reset(self):
        """
        Resets the table by clearing the stack
        """
        self.stack = []

    def _has_suit(self, hand: list[Card], suit: str):
        """
        Returns boolean value depending on whether
        the suit is present in the hand
        """
        return any(
            card.suit.lower() == suit for card in hand)

    def play_card_to_table(self, card: Card, 
                        player: Player,
                        trump_suit: str):
        """
        Docstring for play_card

        Given the card and player, adds the card to the stack
        
        :param self: Description
        """

        if self._valid_add_to_stack(
                    card=card, 
                    player_hand = player.hand,
                    trump_suit=trump_suit):
                    
                    #if valid then add it to the queue
                    self._add_to_stack(card=card)
                    return True
                    
        return False