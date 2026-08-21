import random

from Classes.deck import Deck
from Utils.types import CardInt, TrumpStr


def weak_hand(deck: Deck, size=8) -> set[CardInt]:
    """Generates a weak hand as well as modifying the deck instance passed so that the 
    cards are removed from the deck
    """

    weak_cards = [card.id for card in deck.cards if card.id % 13 < 6]
    sample = set(random.sample(weak_cards, size))
    deck.cards = [card for card in deck.cards if card.id not in sample]
    return sample 

def strong_hand(deck: Deck, size=8) -> set[CardInt]:
    """Generates a strong hand as well as modifying the deck instance passed so that the 
        cards are removed from the deck"""
    strong_cards = [card.id for card in deck.cards if card.id % 13 > 9]
    sample = set(random.sample(strong_cards, size))
    deck.cards = [card for card in deck.cards if card.id not in sample]
    return sample 

def random_hand(deck: Deck, size=8) -> set[CardInt]:
    """Generates a random hand as well as modifying the deck instance passed so that the 
        cards are removed from the deck"""
    card_ids = [card.id for card in deck.cards]
    sample = set(random.sample(card_ids, size))
    deck.cards = [card for card in deck.cards if card.id not in sample]
    return sample 

def suited_hand(deck: Deck, size=8) -> set[CardInt]:
    """Generates a single suit hand as well as modifying the deck instance passed so that the 
        cards are removed from the deck"""
    
    random_suit = random.choice(range(3))  
    suited_cards = [card.id for card in deck.cards if card.id // 13 == random_suit]
    sample = set(random.sample(suited_cards, size))
    deck.cards = [card for card in deck.cards if card.id not in sample]
    return sample 

def dynamic_hand(trump_suit: TrumpStr, size:int=8, strength: float = 0.0) -> set[CardInt]:
    """Takes the trump_suit, size of the hand and the strength of the dynamic hand (0-1), and returns
    the new hand"""

    if not 0.0 < strength < 1.0:
        raise ValueError(f"Strength value must be within 0-1, {strength} is beyond this scope")

    # SUIT_FROM_INITIAL()

def generate_hand(hand_type: str, deck: Deck, size: int = 8):
    """Generates hand based the parameters. Options are
    'strong', 'weak', 'suited', 'random' """
    if hand_type == "strong":
        return strong_hand(deck, size)

    if hand_type == "weak":
        return weak_hand(deck, size)

    if hand_type == "suited":
        return suited_hand(deck, size)

    if hand_type == "random":
        return random_hand(deck, size)

    raise ValueError(f"Unknown hand type: {hand_type}")