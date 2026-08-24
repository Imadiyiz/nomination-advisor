import random

from game_engine import GameState
from Utils.card_tools import *
from Utils.types import *
from bot import BotPlayer
import copy


class RolloutSimulator:
    """
    Simulates the actions within a rollout applying moves in logical order
    """
    def __init__(self, state: GameState):
        # local mutable copy
        self.state = state

    def random_rollout_round(self) -> dict[PlayerStr, int]:
        """
        Players play random moves until they run out of moves and the round terminates.
        Returns the scores from the round
        
        """
        self.state.winner = None  # Reset winner to ensure the trick is not considered complete at the start
        while not self.state.is_round_terminal():
            
            player = self.state.next_player()
            legal_moves = self.state.get_legal_moves(player)
            if not tuple(legal_moves):
                raise ValueError("There is a duplicate card in play, please check assigned cards")
            move = random.choice(tuple(legal_moves))  # Intentionally random

            self.state = self.state.apply_move(player, move)

        return self.state.round_scores

    def baseline_rollout_round(self, player_map: dict[PlayerStr, BotPlayer]) -> dict[PlayerStr, int]:  # Can't be real player as this is a rollout simulator
        """
        Players play moves to win or lose the trick based on bid until they run out of moves and the round terminates.
        Returns the scores from the round
        
        """
        self.state.winner = None  # Reset winner to ensure the trick is not considered complete at the start
        while not self.state.is_round_terminal():

    
            player = player_map[self.state.next_player()]
            legal_moves = self.state.get_legal_moves(player.name)
            if not tuple(legal_moves):
                raise ValueError("There is a duplicate card in play, please check assigned cards")

            # Player determines move instead of random
            move = player.determine_naive_move(
                current_trick=self.state.current_trick,
                trump_suit=self.state.trump_suit,
                player_amount=len(self.state.player_order),
                legal_moves=legal_moves,
                round_score=self.state.round_scores,
                bids=self.state.bids,
                )

            self.state = self.state.apply_move(player.name, move)

        return self.state.round_scores

    def rollout_trick(self, perspective: PlayerStr, chosen_card: CardInt) -> PlayerStr | None:

        """
        Similar to rollout round however, it terminates after finishing a trick
        """

        self.winner = None # reset winner before new one is assigned
        while not self.state.is_trick_terminal():
            player = self.state.next_player()
            legal_moves = self.state.get_legal_moves(player) # The real truth

            if not tuple(legal_moves):
                    raise ValueError("There is a duplicate card in play, please check assigned cards RT")

            # Perspective plays chosen card, others play random legal cards
            if player == perspective:
                move = chosen_card
            else:
                move = random.choice(tuple(legal_moves))  # Must change

            self.state = self.state.apply_move(player, move)

        return self.state.winner 

