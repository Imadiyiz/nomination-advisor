# Contents of the Scoreboard class which keeps track of the scores in the game
from Utils.types import PlayerStr, CardInt

from game_state import GameState


class Scoreboard:
    """
    Scoreboard class used to monitor and update the scores of multiple players.
    Note: Why is it necessary to keep passing the player list to the scoreboard if this never changes
    """

    def __init__(self, players: list[PlayerStr]):
        self.round_scoreboard = {p: 0 for p in players}
        self.total_scoreboard = {p: 0 for p in players}
        
        
    def display(self, state: GameState, round: bool = True) -> str:
        """
        Function for outputting the scores in the game

        Args:
            Round (bool): True by default and determines whether the display should be the 
            round scoreboard or total scoreboard 

        Returns:
           List: Formatted and sorted version of the scoreboard for readability 
        """

        scoreboard = self.round_scoreboard if round else self.total_scoreboard 

        formatted_scoreboard = sorted(
            scoreboard.items(), 
            key= lambda x:x[1], #sort by the second element of each function
            reverse = True
        )

        return " | ".join([
            f"{name} {score} ({state.bids[name]})" 
            for name, score in formatted_scoreboard
        ]

        ) if round else " | ".join([
            f"{name} {score}" 
            for name, score in formatted_scoreboard
        ]

        )
    
    def reorder_round_scoreboard(self, player_queue:list):
        """
        Reorders the round scoreboard to ensure it aligns with the current bids

        Args:
            player_queue (list): The player queue is necessary to preserve the correct order
        """

        temp_dict = {}
        for player in player_queue:
            temp_dict[player.name] = player.round_score
        self.round_scoreboard = temp_dict

    def reset_round_scoreboard(self):

        self.round_scoreboard = {}