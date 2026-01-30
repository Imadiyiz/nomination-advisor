# Contents of the Trump Manager Class
import random
from .PlayerClass import Player

class TrumpManager:
    """
    Handles the trump selection

    Args:
        UIManager (UIManager): Required to output visuals for the user
    """

    def __init__(self, UIManager):
        self.UIManager = UIManager

    def decide_trump(self, player_set: set[Player], current_trump:str):
        """
        Determines which player is choosing trump for the next round

        If the player is a human, they get to choose 
        If the player is a computer, the trump suit remains the same

        Args:
            player_set (set[Player]): The player set is necessary to iterate through the players
            current_trump (str): Ensures that the trump value does not change if the computer decides on the trump

        Returns:
            str: The trump suit - either newly selected by a human or the existing one if chosen by a computer.
        """
        #find top scorers
        scores = dict()
        top_players = list()
        for player in player_set:
            scores[player] = player.round_score
        top_score = max(scores.values())
        
        for player in player_set:
            if scores[player] == top_score:
                top_players.append(player)

        chosen_player = random.choice(top_players)
        if chosen_player is None:
            raise Exception("Unable to find Trump Decider")
        
        #if player, let them choose trump
        if not chosen_player.computer:
            return self.player_picks_trump(chosen_player)
        
        self.UIManager.display_message(f"{chosen_player.name} SELECTED {current_trump}")
        return current_trump
    
    def player_picks_trump(self, player:Player):
        """
        Human players pick their trump values

        Args:
            player (Player): The player object who chooses the trump suit
        
        Returns:
            str: Trump suit which has been chosen by the player
        """

        suit_map = {'C': 'club', 'S': 'spade', 'H': 'heart', 'D': 'diamond'}
        while True:
            choice = self.UIManager.get_player_input("[C] Club,\n [S] Spade,\n [H] Heart,\n [D] Diamond\n").strip().upper()
            if choice in suit_map:
                trump = suit_map[choice]
                self.UIManager.display_message(f"{player.name} selected {trump}")
                return trump
            else:
                self.UIManager.display_message("Invalid choice. Try again.")