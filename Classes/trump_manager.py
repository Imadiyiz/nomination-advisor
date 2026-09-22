# Contents of the Trump Manager Class
import random

from Utils.types import PlayerStr
from game_state import GameState

class TrumpManager:
    """
    Handles the trump selection

    """

    def decide_trump(self, state: GameState) -> PlayerStr:
        """
        Determines which player is choosing trump for the next round

        Args:
            state (GameState): Current state to make decision from
        Returns:
            PlayerStr: The player who decides trump
        """

        #find top scorers
        scores = {}
        top_players = []
        for player in state.player_order:
            scores[player] = state.round_scores[player]
        top_score = max(scores.values())
        
        for player in state.player_order:
            if scores[player] == top_score:
                top_players.append(player)

        chosen_player = random.choice(top_players) # Why must it be randomised if equal,
        # Cons of player A choose trump and player B gets first play is what if it is a 3 way tie (extremely rare)
        
        if chosen_player is None:
            raise ValueError("Unable to find Trump Decider")
        
        return chosen_player
    
