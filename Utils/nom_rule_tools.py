# Holds helper methods which help enforce the rules of the nomination game

from Utils.card_serialization import SUIT_FROM_INITIAL
from Utils.types import CardInt, TrumpStr


def calculate_correct_bid_score(tricks_won: int) -> int:
        """Based on Nomination rules returns correct bid score for the given number of tricks won by a player

        Args:
            tricks_won (int): The number of tricks won by the player

        Returns:
            int: The score corresponding to the number of tricks won according to Nomination rules
        """

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
             
def calculate_total_score_difference(original_total_score: dict[str, int], new_total_score: dict[str, int]) -> dict[str, int]:
    """Calculates the difference between the original and new total scores for each player.

    Args:
        original_total_score (dict[str, int]): The original total scores of the players.
        new_total_score (dict[str, int]): The new total scores of the players.

    Returns:
        dict[str, int]: A dictionary mapping each player to the difference in their total score.
    """
    return {player: new_total_score.get(player, 0) - original_total_score.get(player, 0)
            for player in original_total_score}
             