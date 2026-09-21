import random

from Utils.card_serialization import initials_to_id
from Utils.types import CardInt


class Deck:

    """
    Single source of truth of the deck
    Able to draw only
    """
    def __init__(self):
        self.cards = [i for i in range(52)]
        random.shuffle(self.cards)

    def draw_random(self):
        return self.cards.pop()

    def draw_specific_card(self, specific_card: str) -> CardInt:
        """Receives initials, removes the card from the deck and 
        returns card integer corresponding to the card. Fails silently, if no card
        was found."""
        _id = initials_to_id(specific_card)
        for card in self.cards:
            if _id == card:
                self.cards.remove(card)
                return card
        raise ValueError(f"{specific_card} card does not exist within this deck")

    def contains(self, card: CardInt) -> bool:
        """Only requires card id, does not alter deck"""
        return card in self.cards

    def __len__(self):
        return len(self.cards)