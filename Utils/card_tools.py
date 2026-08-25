from Utils.types import CardInt, TrumpStr
from collections.abc import Iterable

# format for standard english

def format_string(s: str) -> str:
    """Formats irregular string into a lowercase string with uppercase starting character"""
    return s[0].upper() + s[1:].lower()

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

def get_suit_from_initial(initial:str) -> int:
    if initial[0].upper() not in SUIT_FROM_INITIAL:
        raise ValueError(f"{initial[0]} is not a valid initial")

    return SUIT_FROM_INITIAL[initial[0].upper()]

def get_rank(card: CardInt) -> str:
        return RANKS[card % 13]
    
def get_suit_str(card: CardInt) -> TrumpStr:
    return SUITS[card // 13]

def get_suit_symbol(card:CardInt) -> str:
    return SUITS_TO_SYMBOL[get_suit_str(card)]

def id_to_initials(card: CardInt) -> str:
    return f"{get_rank(card)}{get_suit_str(card)[0].upper()}"

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

def id_to_initial_list(id_list: Iterable[CardInt]) -> list[str]:
     """Turns list of card ids into a list of card initials"""
     return [id_to_initials(id) for id in id_list]
