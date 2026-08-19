import random

from Utils.types import CardInt

# 0-based indexing used to generate rank
RANKS = (
"2", "3", "4", "5", "6", "7", "8",
"9", "10", "J", "Q", "K", "A"
)

SUITS_TO_SYMBOL = {
    "Clubs": "♣",
    "Diamonds": "♦",
    "Hearts": "♥",
    "Spades": "♠"
    }

SUITS = (
    "Clubs",
    "Diamonds",
    "Hearts",
    "Spades"
)

DECK = list(range(52))

VALUE_PROSE = ('Jack', 'Queen', 'King', 'Ace')

RANK_FROM_INITIAL = {
    rank:index
    for index, rank in enumerate(RANKS)
}

SUIT_FROM_INITIAL = {
    "C": 0,
    "D": 1,
    "H": 2,
    "S": 3,
}


def get_rank(card: CardInt) -> str:
        return RANKS[card % 13]
    
def get_suit(card: CardInt) -> str:
    return SUITS[card // 13]

def get_suit_symbol(card:CardInt) -> str:
    return SUITS_TO_SYMBOL[get_suit(card)]

def id_to_initials(card: CardInt) -> str:
    return f"{get_rank(card)}{get_suit(card)[0].upper()}"

def initials_to_prose(value: str, suit: str) -> str:
    """ Returns prose from receiving the value and suit part of the initials"""
    if RANK_FROM_INITIAL[value] >= 9: # Must be picture card
         for item in VALUE_PROSE:
              if value == item[0]:
                   value = item
    for item in SUITS:
         if item[0] == suit:
              suit = item
    return f"{value} {suit}"

def initials_to_id(initials: str) -> CardInt:

    rank = RANK_FROM_INITIAL[initials[:-1].upper()]
    suit = SUIT_FROM_INITIAL[initials[-1].upper()]

    return suit * 13 + rank

########

def weak_hand(size=8) -> set[CardInt]:
    weak_cards = [num for num in DECK if num % 13 < 6]
    return set(random.sample(weak_cards, size))

def strong_hand(size=8) -> set[CardInt]:
    strong_cards = [num for num in DECK if num % 13 > 9]
    return set(random.sample(strong_cards, size))

def random_hand(size=8) -> set[CardInt]:
    return set(random.sample(DECK, size))

def suited_hand(size=8) -> set[CardInt]:
    random_suit = random.choice(range(3))
    suited_cards = [num for num in DECK 
                    if num // 13 == random_suit]
    return set(random.sample(suited_cards, size))

def generate_hand(hand_type: str, size: int = 8):
    """Generates hand based the parameters. Options are
    'strong', 'weak', 'suited', 'random' """
    if hand_type == "strong":
        return strong_hand(size)

    if hand_type == "weak":
        return weak_hand(size)

    if hand_type == "suited":
        return suited_hand(size)

    if hand_type == "random":
        return random_hand(size)

    raise ValueError(f"Unknown hand type: {hand_type}")