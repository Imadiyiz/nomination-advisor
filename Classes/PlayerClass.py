# Contents of the Player class python file

from .CardClass import Card
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Player:
    """
    Handles the hand functionality of players.
    Players are able to collect hands and play cards.
    
    """
    name: str = "AI"
    hand: List[Card] = field(default_factory=list) #each player gets their own hand list
    total_score: int = 0
    round_score: int = 0
    bid: int = -1 # must be -1 because 0 is a valid bid
    trump_decider:bool = False
    computer: bool = False,
    opponent: bool = True,
    handicapped_bid:bool = False

    def collect_hand(self, hand: List[Card]):
        """
        Ensures that the cards in the hand are assigned to the player
        """
        for card in hand:
            card.owner = self
        self.hand = hand

    def remove_card(self, card: Card):
        """
        Discards card from player's hand
        """
        for _card in self.hand:
            if card == _card:
                self.hand.remove(_card)
                return

    def find_card(self, selected_suit: str, selected_value: str) -> bool:
        """Determies whether the selectd card is present in player's hand"""
        for card in self.hand:
            if card.suit[0].lower() == selected_suit.lower() and card.value[0].lower() == selected_value.lower():
                return True
        return False
    
    def display_hand_str(self, max_cards: int = 8): # currently the hands are empty
        """
        Displays the user's hand depending on whether the player is an opponent
        
        Args:
            max_cards(int): Maximum amount of cards possible for current round
        """

        if not self.hand:
            return ['X' for _ in range(max_cards)]

        # Keeps opponent's hands hidden
        if self.opponent == False:
            return [str(card) for card in self.hand]
        else:
            return ['X' for _ in self.hand]


    def set_trump_decider(self, boolean: bool):
        self.trump_decider = boolean

    def reset(self):
        self.bid = -1
        self.trump_decider = False
        self.handicapped_bid = False    
        self.hand = []    

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