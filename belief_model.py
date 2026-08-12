# contents of belief model python file 

import random
from dataclasses import dataclass


@dataclass
class BeliefModel:
    """
    Player belief model
    Represents what one player believes about the game
    """

    void_suits: dict[str, set[str]] # dict, player id, set(suit)
    unknown_cards: set[str]         # cards not yet assigned
    hand_sizes: dict[str, int]      # player -> cards remaining
    perspective_player: str

    def observe_play(self,
                         player: str,
                         card: str,
                         lead_suit: str, 
                         trump_suit: str):
        
        """
        Updates beliefs after watching a play
        """

        # removes card from unknown pool
        self.unknown_cards.discard(card)
        self.hand_sizes[player] -= 1

        card_suit = card[-1]

        # infer void
        if card_suit != lead_suit:
            self.void_suits[player].add(lead_suit)

    def sample_world(self) -> dict[str, set[str]]:
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
                if c[-1] not in self.void_suits[player]
            ]

            if len(possible_cards) < size:
                raise ValueError('No valid world exists')

            # assigns cards to player consistent with world constraints
            chosen_cards = random.sample(possible_cards, size)
            assignments[player].update(chosen_cards)

            for card in chosen_cards:
                remaining_cards.remove(card)

        return assignments