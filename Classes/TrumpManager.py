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

    def decide_trump(self, players: list[Player]) -> Player:
        """
        Determines which player is choosing trump for the next round

        Args:
            players (list[Player]): The players list is necessary to iterate through the players

        Returns:
            Player: The player who decides trump
        """

        #find top scorers
        scores = dict()
        top_players = list()
        for player in players:
            scores[player] = player.round_score
        top_score = max(scores.values())
        
        for player in players:
            if scores[player] == top_score:
                top_players.append(player)

        chosen_player = random.choice(top_players)
        if chosen_player is None:
            raise Exception("Unable to find Trump Decider")
        
        return chosen_player
    
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