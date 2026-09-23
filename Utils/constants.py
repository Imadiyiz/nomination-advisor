# Constants used throughout the game

VALID_CARD_INITIALS = {
    (f"{rank}{suit}")
    for rank in (2,3,4,5,6,7,8,9,10,'J','Q','K','A')
    for suit in "CDHS"
    }
CARDS_PER_ROUND = (1,2) # (8,7,6,6,7,8)