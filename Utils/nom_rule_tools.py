# Holds helper methods which help enforce the rules of the nomination game

from Utils.types import CardInt, TrumpStr
from Utils.card_tools import SUIT_FROM_INITIAL

def calculate_correct_bid_score(tricks_won: int) -> int:
        """Based on Nomination rules returns correct bid score"""

        if tricks_won > 8:
            return tricks_won
        if tricks_won == 8:
            return 36
        return tricks_won + 10

def calculate_winning_card(trick: list[CardInt], trump_suit: TrumpStr) -> CardInt | None:

    """Returns winning card based on Nomination rules, returns None if trick is empty"""


    if not trick:
        return None
    
    first_card = trick[0]
    trump_suit_id = SUIT_FROM_INITIAL[trump_suit[0].upper()]
    first_suit = first_card // 13

    # Gets all the trump cards in the current stack
    trump_cards = [c for c in trick if c // 13 == trump_suit_id]
    
    if trump_cards:
        return max(trump_cards, key=lambda c: c % 13)
            
    follow_suit_cards = [
        c for c in trick if c // 13 == first_suit]
    
    return max(follow_suit_cards, key=lambda c: c % 13)
             
                
             
             