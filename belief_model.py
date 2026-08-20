# contents of belief model python file 

import random
from dataclasses import dataclass
from Utils.card_tools import *


from Utils.types import *
# Purposefully decided not to add a score attribute to the belief model as I believe,
# that the score shouldn;t be bound to the belief model class as it would need update for each
# instance and it would become coupled with the instance even though the score does affect the belief model
@dataclass
class BeliefModel:
    """
    Player belief model
    Represents what one player believes about the game
    """

    void_suits: dict[str, set[str]] # dict, player id, set(suit)
    unknown_cards: set[CardInt]         # cards not yet assigned
    hand_sizes: dict[PlayerStr, int]      # player -> cards remaining
    perspective_player: PlayerStr

    def observe_play(self,
                         player: PlayerStr,
                         card: CardInt,
                         lead_card: CardInt, 
                         trump_suit: CardInt):
        
        """
        Updates beliefs after watching a play
        """

        # removes card from unknown pool
        self.unknown_cards.discard(card)
        self.hand_sizes[player] -= 1

        card_suit = get_suit_str(card)
        lead_suit = get_suit_str(lead_card)

        # infer void
        if card_suit != lead_suit:
            self.void_suits[player].add(lead_suit)

    def sample_world(self) -> dict[PlayerStr, set[CardInt]]:
        """
        Produce a concrete assignment of unknown cards
        which are consistent with all the constraints
        
        """

        assignments = {p: set() for p in self.hand_sizes}

        remaining_cards = list(self.unknown_cards)
        random.shuffle(remaining_cards)

        for player, size in self.hand_sizes.items():
            if player == self.perspective_player:
                continue  # already known

            possible_cards = [
                c for c in remaining_cards
                if get_suit_str(c) not in self.void_suits[player]
            ]

            if len(possible_cards) < size:
                raise ValueError('No valid world exists')

            # assigns cards to player consistent with world constraints
            chosen_cards = random.sample(possible_cards, size)
            assignments[player].update(chosen_cards)

            for card in chosen_cards:
                remaining_cards.remove(card)

        return assignments