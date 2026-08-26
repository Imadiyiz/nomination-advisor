# contents of belief model python file 

import random
from dataclasses import dataclass

from Utils.card_tools import *
from Utils.types import *


# Purposefully decided not to add a score attribute to the belief model as I believe,
# that the score shouldn't be bound to the belief model class as it would need update for each
# instance and it would become coupled with the instance even though the score does affect the belief model
@dataclass
class BeliefModel:
    """
    Player belief model
    Represents what one player believes about the game
    """

    void_suits: dict[PlayerStr, set[str]]  # dict, player id, set(suit)
    unknown_cards: set[CardInt]      # cards not yet assigned
    hand_sizes: dict[PlayerStr, int]  # player -> cards remaining
    perspective_player: PlayerStr

    def observe_play(self,
                         player: PlayerStr,
                         card: CardInt,
                         lead_card: CardInt):
        
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
        Produce a hypothetical assignment of unknown cards
        which are consistent with all the constraints. This is a greedy sampling 
        technique which is adequate for this implementation but does not guarantee that
        there isn't a valid world which would satisfy the constraints.
        
        """
        attempts = 0
        MAX_ATTEMPTS = 25000  # Not happy, but in 6 players it struggles with the sampling. Normally
        # the upper limit is not reached thankfully
        valid = True

        # Attempt sampling until valid world assignments are formed
        while attempts < MAX_ATTEMPTS:

            # Fresh try
            assignments = {p: set() for p in self.hand_sizes}
            hands = dict(self.hand_sizes)  # local copy for altering
            remaining_cards = list(self.unknown_cards)
            random.shuffle(remaining_cards)
            constraints = {p: int() for p in self.hand_sizes}
            valid = True

            for _ in range(len(self.hand_sizes) - 1):  # Do not need to sample for perspective player
                attempts += 1
                constraints = {}

                # Calculate possible card pool size per player
                for player, size in hands.items():

                    if player == self.perspective_player:
                        continue  # already known
                    
                    possible_cards = [
                        c for c in remaining_cards
                        if get_suit_str(c) not in self.void_suits[player]
                        ]

                    constraints[player] = len(possible_cards)
                    
                player_to_sample = min(sorted(constraints, key=constraints.get))  

                possible_cards = [
                            c for c in remaining_cards
                            if get_suit_str(c) 
                            not in self.void_suits[player_to_sample]
                    ]
                
                size = hands[player_to_sample]  # Size of the hand to be played
                if len(possible_cards) < size:
                    valid = False  
                    break

                # assigns cards to player consistent with world constraints
                chosen_cards = random.sample(possible_cards, size)
                assignments[player_to_sample].update(chosen_cards)

                for card in chosen_cards:
                    remaining_cards.remove(card)

                # Remove sampled player from hand dict
                hands.pop(player_to_sample)

            if valid:
                return assignments


        raise ValueError(f'No valid world exists, tried {attempts} times') 