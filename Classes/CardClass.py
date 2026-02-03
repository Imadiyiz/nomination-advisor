# Class script for the cards in the deck

class Card:

    """
    Represents a playing card with a suit, value, and optional owner.

    Each card has a suit (e.g., "Heart", "♦"), a value (e.g., "10", 10),
    and can optionally have an owner (a Player object). Upon creation,
    the card generates an ASCII representation of itself.

    Attributes:
        suit (tuple): The suit of the card, e.g., ("Heart", "♥").
        value (tuple): The value of the card, e.g., ("10", 10) or ("Ace", 14).
        owner (Player, optional): The owner of the card.

    Methods:
        generate_picture():
            Generates and returns an ASCII representation of the card.

        __eq__(other):
            Checks equality between two Card objects based on suit and value.

        __str__():
            Returns a string representation of the card (e.g., "10 Heart").

        __hash__():
            Returns a hash value for the card, allowing it to be used in sets and dictionaries.
    """

    def __init__(self, suit: tuple, value: tuple, owner: 'Player' = None): # Forward reference to avoid nameError
        self.suit = suit
        self.value = value
        self.owner = owner

    @classmethod
    def from_initials(cls, initials: str):
        """
        Convert initials like '10H' or 'QS' into (value_str, suit_letter)

        e.g ("10", "H")
        """

        if not initials or len(initials) < 2:
            raise ValueError("Invalid card initials")
        
        value_part = initials[:-1].upper()  # removes the end character
        suit_part = initials[-1].upper()  # suit part is the last character

        return value_part, suit_part




    def __eq__(self, other):
        return self.suit == other.suit and self.value == other.value
    
    def __str__(self):
        return f"{self.value[0]} {self.suit[1]}"
    
    def __hash__(self):
        return hash(str(self))