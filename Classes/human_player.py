# Contents of the Player class python file

from dataclasses import dataclass


@dataclass
class HumanPlayer:
    """
    Handles the hand functionality of players.
    Players are able to collect hands and play cards.
    
    """
    name: str = "AI"

    def __str__(self):
        return self.name
    
    # ensures that each player object is unique by name
    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return id(self)