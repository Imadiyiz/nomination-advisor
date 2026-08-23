# Bot player who will make decisions during simulation
import math
import random

from belief_model import BeliefModel
from heuristics import Heuristics
from Utils.card_tools import SUIT_FROM_INITIAL
from Utils.types import CardInt, TrumpStr


class BotPlayer:

    """
    Bot player within the Monte Carlo Simulation. Able to reason during the sim in order
    tp make the simuation more realistic. Fed the truth via Gamestate, and makes decision based on personality and
    belief_model (brain)
    """

    def __init__(self,
                 heuristics: Heuristics | None = None,
                 name = 'AI',
                 belief_model: BeliefModel | None = None):
        
        """Originally only has a name, personality and optionally a brain.
        Pass in 'belief_model': BeliefModel(), to incorporate a simulation brain for the bot"""
        self.heuristics = heuristics if heuristics is not None else Heuristics()  # default Heuristic instance with all 0.5 attributes
        self.name = name
        self.belief_model = belief_model

    def determine_bid(self, expected_scores: dict[int, float],
                      position: int,
                      table_size: int,
                      points_margin: int,
                      current_bids: list[int],
                      hand_size: int,
                      restriction:int = -1) -> int:
        """Determines a bid based on the distribution of their ES 
        (Expected Score). Also accounts for their position at the
        table, the table size and the points margin from the leader
        whiile making use of heuristics. Caller of the function must impose the restriction
        of bid amount if necessary.
        Returns: bid"""

        curr_bid_sum = sum(current_bids)
        core_avg_bid = (
            table_size / hand_size
        )

        # Determine whether the previous players are overbidding or underbidding
        CURRENT_BID_MARGIN = curr_bid_sum - (core_avg_bid) * len(current_bids)  
        
        decision_risk = self.heuristics.risk_tolerance
        print("Original decision_risk", decision_risk)
        BIOI = self.heuristics.belief_in_open_information

        # idk if this the correct way to do things
        # alter heuristics based on the information at hand
        if CURRENT_BID_MARGIN > 1 or CURRENT_BID_MARGIN < -1:  # Reduce decision_risk if the margin swings
            decision_risk = min(1, decision_risk * BIOI)  # Reduces less if belief is high

        print("B Margin decision_risk", decision_risk)
        # Decides whether the bot will ignore points margin
        if points_margin < -(15 * decision_risk):  # Reduce decision_risk if the margin swings
            decision_risk = min(1, decision_risk * BIOI * 1.2) 
        elif points_margin > (15 * decision_risk):
            decision_risk = min(1, decision_risk * BIOI * 0.8) 

        print("P Margin decision_risk", decision_risk)
        # Decides whether the bot will ignore the position at table
        if position == 0:
            decision_risk = min(1, decision_risk * BIOI * 1.5) # Take more risk knowing bot dictates play
        elif position == table_size - 1:
            decision_risk = min(1, decision_risk * BIOI * 0.5) # Take less risk knowing bot can't dictate play

        print("Pos Margin decision_risk", decision_risk)
        # Clean distribution dict from null values
        expected_scores_list = [(i, dist) for i, dist in expected_scores.items() if dist > 0.0]
        print(expected_scores_list)


        # if restriction then cleanse and normalise distribution
        if -1 < restriction < 9:
            expected_scores_list = [s for s in expected_scores_list if s[0] != restriction]


        # how to normalise new distribuitons

        # Generate top moves to choose from
        top_moves = sorted(expected_scores_list,
                           key = lambda es: es[1],
                           reverse=True)[:3]  # List of the top 3 probable moves, sodecision_risked by points gained

        top_moves_in_order = sorted(
            top_moves,
            key=lambda tm: tm[0],
            reverse=True
        )  # Sort again to allow risky moves to be made to maximise score

        if decision_risk > 0.7:  # Favour the greater returns
            bid, _ = random.choices(top_moves_in_order,
                       weights=[exp[1] for exp in top_moves_in_order],
                       k=1)[0]
        else:
            bid, _ = top_moves[0] # Move with the highest ES

        return bid
    
        # Distribution should not have restricted bid within it


    def determine_baseline_bid(self, hand: set[CardInt], 
                               trump_suit: TrumpStr,
                               player_amount: int,
                               restriction: int = -1) -> int:
        """Naively determines bid solely based on hand strength
           Accepts a hand parameter instead of using actual hand as.
           If the bot has a restriction on bid, they must alter their bid towards the average"""

        
        hand_size = len(hand)

        if self.belief_model is not None:  # Ensure belief model exists before attempting to calculate hand sizes
            player_amount = len(self.belief_model.hand_sizes)

        if player_amount and not (3 <= player_amount <= 6):
            raise ValueError("Incorrect amount of players submitted, must be between 3-6")

        trump_id = SUIT_FROM_INITIAL[trump_suit[0].upper()]
        strong_cards = [card for card in hand 
                        if self._is_strong_card(card,
                                                trump_id, 
                                                player_amount,
                                                hand_size)]

        # Expects to win with each strong card
        bid_to_confirm = len(strong_cards) 

        if bid_to_confirm == restriction:
            if restriction == 0:  # Can only play 1 as -1 is not allowed
                return 1
            else:
                return random.choice(
                    (restriction + 1, restriction - 1))  # has a dramatic effect on the distribution
        else:
            return bid_to_confirm


    def _is_strong_card(self, card: CardInt,
                        trump_id: int,
                        player_amount: int,
                        hand_size: int) -> bool:

        """Trump cards over X amount and high cards over Y amount are strong (assumes 4 players). 
        Threshold aims for expected strong cards in play to be the number of cards per hand.
        Returns: True if strong"""

        if card is None:
            return False

        # Ensures that the strong card pool is at least the minimum required
        # to make the expected strong cards in play the number of cards per hand.
        strong_cards_target = self._generate_strong_card_target(
            hand_size, player_amount)  

        strong_cards = []
        trump_threshold = 12
        high_threshold = 12

        while len(strong_cards) < strong_cards_target:
        
            strong_cards = [card for card in range(52) if (
                    (card // 13 == trump_id and card % 13 > (trump_threshold))
                    or card % 13 > (high_threshold))
            ]
            margin = strong_cards_target - len(strong_cards)

            if margin > 3:
                high_threshold -=1
            elif margin > 0:
                trump_threshold -=1

        return card in strong_cards

    def _generate_strong_card_target(self, 
                                     hand_size:int,
                                     player_amount: int):
        """Based off hand_size and player_amount generates smallest strong card pool target which makes the
        expected strong cards within play greater than hand size."""

        PC = hand_size * player_amount
        TC = 52
        HS = hand_size
        return int(round((TC*HS) / PC, 0))


    def determine_move(self, possible_moves: set[CardInt], calculation_limit = 10) -> CardInt:
        """ Evaluates possible moves based on heuristics and belief model. Outputs
        chosen move"""

        chosen_move = None  
        attempts = 0

        while attempts < calculation_limit:

            attempts += 1
            move = random.choice

        return int()