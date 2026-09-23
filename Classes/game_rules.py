from Utils.card_serialization import get_suit_str
from Utils.types import CardInt, PlayerStr

class GameRules:

    @staticmethod
    def get_legal_moves(
        hand: set[CardInt],
        current_trick: tuple,
    ) -> set[CardInt]:
        """
        Function for identifing legal moves based on the player's known cards;
        enforces follow-suit and respects trump rules
        
        :returns set of legal moves
        """

        if not hand:
            raise ValueError("No cards in hand")

        if not current_trick:
            return set(hand)

        lead_suit = get_suit_str(current_trick[0][1])
        
        follow_cards = {card for card in hand 
                        if get_suit_str(card) == lead_suit
        }
        
        if follow_cards:  # Can not play trumps if in possesion of follow card
            return set(follow_cards) 
        else:
            # if no legal moves, any card can be discarded
            return set(hand)


    @staticmethod
    def get_game_winner(total_scores: dict[PlayerStr, int],
                        player_order: list[PlayerStr]
                        ) -> tuple[list[PlayerStr], int]:
        """
        Determines the winner(s) of the game based on total scores and player order.

        Args:
            total_scores (dict[PlayerStr, int]): A dictionary mapping players to their total scores.
            player_order (list[PlayerStr]): The order of players to consider for tie-breaking.

        Returns:
            tuple[list[PlayerStr], int]: A tuple containing the list of winning players and the winning score.
        """

        winning_score = max(total_scores.values())

        winning_players = [player for player in player_order
                           if total_scores[player] == winning_score]

        return winning_players, winning_score