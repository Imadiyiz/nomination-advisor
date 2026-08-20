import random

from Classes.CardClass import Card
from Utils.card_tools import initials_to_id


class Deck:

    """
    Single source of truth of the deck
    Able to draw only
    """
    def __init__(self):
        self.cards = [Card(card_id = id) for id in range(52)]
        random.shuffle(self.cards)

    def draw_random(self):
        return self.cards.pop()

    def draw_specific_card(self, specific_card: str) -> Card:
        """Receives initials, removes the card from the deck and returns associated card object"""
        _id = initials_to_id(specific_card)
        for card in self.cards:
            if _id == card.id:
                self.cards.remove(card)
                return card
        raise ValueError(f"{specific_card} card does not exist within this deck")

    def contains(self, card: int):
        """Only requires card id"""
        return Card(card_id = card) in self.cards

    def __len__(self):
        return len(self.cards)