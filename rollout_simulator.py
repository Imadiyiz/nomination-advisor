import copy
import random

from bot import BotPlayer
from game_engine import GameState
from Utils.card_tools import *
from Utils.types import *


class RolloutSimulator:
    """
    Simulates the actions within a rollout applying moves in logical order
    """
    def __init__(self, state: GameState):
        # local mutable copy
        self.state = copy.deepcopy(state)

        # Every player including perspective will be an MC bot during sim
        self.bot_players_map = {p: BotPlayer(name=p) for p in state.player_order}  

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

    def naive_rollout_round(self) -> dict[PlayerStr, int]:  # Can't be real player as this is a rollout simulator
        """
        Players play moves to win or lose the trick based on bid until they run out of moves and the round terminates.
        Returns the scores from the round. Basic heurisic and acts as the baseline. Uses bot players created to imitate real players
        during the rollout, including perspective.
        
        """
        self.state.winner = None  # Reset winner to ensure the trick is not considered complete at the start
        while not self.state.is_round_terminal():

            player = self.bot_players_map[self.state.next_player()]
            legal_moves = self.state.get_legal_moves(player.name)
            if not tuple(legal_moves):
                raise ValueError("There is a duplicate card in play, please check assigned cards")

            # Player determines move instead of random
            move = player.determine_naive_move(
                current_trick=self.state.current_trick,
                trump_suit=self.state.trump_suit,
                legal_moves=legal_moves,
                round_score=self.state.round_scores,
                bids=self.state.bids,
                )

            if move is None:
                raise ValueError(f"Invalid move selected by {player.name}, {move}, is not a valid move")

            self.state = self.state.apply_move(player.name, move)

        return self.state.round_scores

