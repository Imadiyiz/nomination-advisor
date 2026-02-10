# Contents of the Scoreboard class which keeps track of the scores in the game
from Classes.PlayerClass import Player
from Classes.CardClass import Card

class Scoreboard:
    """
    Scoreboard class used to monitor and update the scores of multiple players.
    """

    def __init__(self):
        self.round_scoreboard = {}
        self.total_scoreboard = {}
        
        
    def display(self, round: bool = True) -> list:
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
            f"{name} {score}" 
            for name, score in formatted_scoreboard
        ]

        )
    
    def update_round_scoreboard(self, player_list:list[Player], winner_card: Card):
        """
        Updates the round scoreboard using the player bids and the player score from the round

        Args:
            player_list (list[Player]): List of players used to update the round scoreboard
            winner_card (Card): The winner card is used to determine the who won the round
        """
        #update round score winner 
        for _player in player_list:
            if _player == winner_card.owner:
                _player.round_score +=1 
            self.round_scoreboard[_player.name] = _player.round_score
    
    def update_total_scoreboard(self, player_list:list[Player], max_cards: int = 8):
        """
        Updates the total scoreboard using the player bids and the player score from the round

        Args:
            player_list(list[Player]): Required to iterate throught every player
            max_cards (int): Enables function to caluculate the new scores
        """

        # initialise total_scoreboard if it does not exist
        if not self.total_scoreboard:
            for _player in player_list:
                self.total_scoreboard[_player.name] = 0

        for _player in player_list:
            #check if they got their score correct
            multiplier = 2 if _player.bid == max_cards else 1

            if _player.bid == _player.round_score:
                self.total_scoreboard[_player.name] += (_player.bid + 10) * multiplier  
            else:
                self.total_scoreboard[_player.name] += _player.round_score

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