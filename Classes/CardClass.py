from Utils.card_tools import *

class Card:

    """
    Represents a playing card with a suit, value, and optional owner.

    Each card has a suit (e.g., "Heart", "♦"), a value (e.g., "10", 10),
    and can optionally have an owner (a Player object). Upon creation,
    the card generates an ASCII representation of itself.

    Attributes:
        suit (int): The suit of the card, (0-3).
        value (str): "Jack"  
        owner (Player, optional): The owner of the card.

    Methods:

        __eq__(other):
            Checks equality between two Card objects based on suit and value.

        __str__():
            Returns a string representation of the card (e.g., "10 ♥").

        __hash__():
            Returns a hash value for the card, allowing it to be used in sets and dictionaries.
    """

    def __init__(self, owner: 'Player' = None, card_id: int = 0): # Forward reference to avoid nameError
        self.suit = get_suit_str(card_id)
        self.value = get_rank(card_id)
        self.owner = owner
        self.id = card_id
        self.initials = id_to_initials(card_id)

    @classmethod
    def from_initials(cls, initials: str):
        """
        Convert initials like '10H' or 'QS' into (value_str, suit_letter)
        e.g ("10", "H"), ("Q", "S")
        """

        if not initials or len(initials) < 2:
            print("ERROR", initials)
            raise ValueError("Invalid card initials")
        
        value_part = initials[:-1].upper()  # removes the end character
        suit_part = initials[-1].upper()  # suit part is the last character
        return value_part, suit_part

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return str(self) == str(other)
    
    def __str__(self):
        v, _ = self.from_initials(self.initials)
        symbol = get_suit_symbol(self.id)
        return f"{v} {symbol}"
    
    def __hash__(self):
        return hash(str(self))