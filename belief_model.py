# contents of belief model python file 

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class BeliefModel():


    void_suits: set[str]            #  set(suit)
    known_cards: set[str]           # cards assigned
    unknown_cards: set[str]         # cards not yet assigned
    played_cards: set[str]          # cards that have been played in previous rounds
    hands: set[str]                 # player_id -> cards.initials
    leader: str                     # player in question


    def update_void_suits(self,
                         player_hand: set[str],
                         current_trick: List[str],
                         leader: str):
        
        """
        Updates the void suits dictionary to ensure trick ruling
        
        """

        # single letter of suit 'D', 'H'
        first_card_suit = current_trick[0][-1]
        player_hand_suits = set(
            card[-1] for card in player_hand[leader]
        )

        # if the player doesnt have fcs then they can play anything
        if first_card_suit not in player_hand_suits:
            self.void_suits.add(first_card_suit)

    
    def reset_void_suits(self):

        for player, _ in self.void_suits.items():
            self.void_suits[player] = set()

    def sample_world(self):
        """
        Creates instance of simulationState
        
        :param self: Description
        """