# Bot player who will make decisions during simulation
import random

from heuristics import Heuristics
from belief_model import BeliefModel

class BotPlayer:

    """
    Bot player within the Monte Carlo Simulation. Able to reason during the sim in order
    tp make the simuation more realistic
    """

    def __init__(self, heuristics: Heuristics, belief_model: BeliefModel):
        """Originally only has a personality and a brain"""
        self.heuristics = heuristics
        self.belief_model = belief_model

    def evaluate_moves(self, possible_moves: set[int], calculation_limit = 10) -> int:
        """ Evaluates possible moves based on heuristics and belief model. Outputs
        chosen move"""

        chosen_move = None  
        attempts = 0

        while attempts < calculation_limit:

            attempts += 1
            move = random.choice