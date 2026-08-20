# Bot player who will make decisions during simulation
import random

from belief_model import BeliefModel
from heuristics import Heuristics
from Utils.card_tools import SUIT_FROM_INITIAL
from Utils.types import CardInt, TrumpStr


class BotPlayer:

    """
    Bot player within the Monte Carlo Simulation. Able to reason during the sim in order
    tp make the simuation more realistic
    """

    def __init__(self,
                 heuristics: Heuristics | None = None,
                 name = 'AI',
                 belief_model: BeliefModel | None = None):
        
        """Originally only has a name, personality and optionally a brain.
        Pass in 'belief_model': BeliefModel(), to incorporate a simulation brain for the bot"""
        self.heuristics = heuristics if heuristics else Heuristics()  # default Heuristic instance with all 0.5 attributes
        self.name = name
        self.belief_model = belief_model

    def determine_baseline_bid(self, hand: set[CardInt], 
                               trump_suit: TrumpStr,
                               restriction: int = -1) -> int:
        """Naively determines bid solely based on hand strength
           Accepts a hand parameter instead of using actual hand as.
           If the bot has a restriction on bid, they must alter their bid towards the average"""

        LOW_HAND_BID_WEIGHTS = (4,3,2)
        player_amount = 4 # default player_amount in case its not set in belief_model

        if self.belief_model is not None:  # Ensure belief model exists before attempting to calculate hand sizes
            player_amount = len(self.belief_model.hand_sizes)

        if player_amount and not (3 <= player_amount <= 6):
            raise ValueError("Incorrect amount of players submitted, must be between 3-6")

        trump_id = SUIT_FROM_INITIAL[trump_suit[0].upper()]
        strong_cards = [card for card in hand 
                        if self._is_strong_card(card,
                                                trump_id, 
                                                player_amount)]

        # Plays negatively if bot has less than 3 strong cards
        bid_to_confirm = (
            len(strong_cards) 
            if len(strong_cards) > 2 
            else random.choices(
                (0,1,2),
                weights=LOW_HAND_BID_WEIGHTS,
                k=1)
            [0]
         ) # more biased towards 0

        if bid_to_confirm == restriction:
            if bid_to_confirm == 0:  # Can only play 1 as -1 is not allowed
                return 1
            else:
                return random.choice((bid_to_confirm+1, bid_to_confirm-1))

        else:
            return bid_to_confirm


    def _is_strong_card(self, card: CardInt, trump_id: int, player_amount: int = 4) -> bool:

        """Trump cards over X amount and high cards over Y amount are strong (assumes 4 players). 
        Returns: True if strong"""

        strong = (card // 13 == trump_id 
                 and card % 13 > (1 + player_amount)
                 or card % 13 > (5 + player_amount))
        return strong




    def determine_move(self, possible_moves: set[CardInt], calculation_limit = 10) -> CardInt:
        """ Evaluates possible moves based on heuristics and belief model. Outputs
        chosen move"""

        chosen_move = None  
        attempts = 0

        while attempts < calculation_limit:

            attempts += 1
            move = random.choice

        return int()