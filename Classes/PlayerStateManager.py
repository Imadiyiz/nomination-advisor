# Contents for the PlayerStateManager python file

from .PlayerClass import Player
from .CardClass import Card

class PlayerStateManager:
    """
    Manages player-related state during the game

    *Responibilities:
    - Tracks current turn
    ~ Manages player order (dealer/winner logic)
    ~ Updates player scores
    ~ Resets player handicap states
    """

    def __init__(self, players:list[Player]):
        """
        Initialises the PlayerStateManager with a set of players.

        Args:
            players (set[Player]): A set of Player instances
        """
        self.players = players # list of player objects

    def add_score(self, player:Player, points: int):
        """
        Adds points to a player's total score.

        Args:
            player (Player): The player to update.
            points (int): Number of points to add
        """
        if points >= 0:
            player.total_score += points
            
    def update_dealer_order(self, player_queue: list[Player]) -> list[Player]:
        """
        Rotates the player queue to simulate dealer rotation (clockwise).

        Args:
            player_queue (list(Player)): Current order of the players

        Returns:
            list[Player]: The new queue with a new dealer
        """
        if player_queue:
            player_queue.append(player_queue.pop(0))
        return player_queue

    def update_winner_order(self, winner:Player, player_queue:list) -> list[Player]:
        """
        Rotates the player queue to ensure the player,
        who won the previous hand, ends up playing first in the 
        next hand
        
        Args:
            winner (Player): The player who won the previous hand
            player_queue (List(Player)): The current order of players

        Returns:
            list[Player]: The new order of players starting with the winner
        """

        while player_queue[0] != winner:
            player_queue.append(player_queue.pop(0))
        return player_queue


    def reset_players_handicap(self):
        """
        Resets all players' handicap values
        """

        for player in self.players:
            player.reset_handicap()
