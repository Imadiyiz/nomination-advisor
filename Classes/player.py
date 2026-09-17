# Contents of the Player class python file

from dataclasses import dataclass, field
from Utils.types import CardInt, PlayerStr
from Utils.card_tools import id_to_prose


@dataclass
class Player:
    """
    Handles the hand functionality of players.
    Players are able to collect hands and play cards.
    
    """
    name: str = "AI"
    hand: list[CardInt] = field(default_factory=list) #each player gets their own hand list
    total_score: int = 0
    round_score: int = 0
    bid: int = -1 # must be -1 because 0 is a valid bid
    trump_decider:bool = False
    computer: bool = False
    opponent: bool = True
    
        
    def choose_card(self):
        return self.hand[0]


    def set_trump_decider(self, boolean: bool):
        self.trump_decider = boolean

    def reset(self):
        self.bid = -1
        self.trump_decider = False
        self.handicapped_bid = False    
        self.hand = []    
        self.round_score = 0

    def reset_bid(self):
        self.bid = -1

    def reset_handicap(self):
        self.handicapped_bid = False

    def __str__(self):
        return self.name
    
    # ensures that each player object is unique by name
    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return id(self)