

class Scoreboard:
    """
    Scoreboard class used to output formatted scoreboard based on the current gamestate.
    It is used to keep track of the scores in the game and output them in a readable format.   
    """
    
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