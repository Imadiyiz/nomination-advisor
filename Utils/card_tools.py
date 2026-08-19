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


def get_rank(card: int) -> str:
        return RANKS[card % 13]
    
def get_suit(card: int) -> str:
    return SUITS[card // 13]

def get_suit_symbol(card:int) -> str:
    return SUITS_TO_SYMBOL[get_suit(card)]

def card_to_initials(card: int) -> str:
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
    return f"{value} of {suit}"

def initials_to_id(initials: str) -> int:

    rank = RANK_FROM_INITIAL[initials[:-1].upper()]
    suit = SUIT_FROM_INITIAL[initials[-1].upper()]

    return suit * 13 + rank