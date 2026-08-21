# Holds helper methods which help enforce the rules of the nomination game

def calculate_correct_bid_score(tricks_won: int) -> int:
        """Based on nomination rules returns correct bid score"""

        if tricks_won > 8:
            return tricks_won
        if tricks_won == 8:
            return 36
        return tricks_won + 10