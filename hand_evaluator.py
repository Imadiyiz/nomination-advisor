import copy

from belief_model import BeliefModel
from game_engine import GameState
from rollout_simulator import RolloutSimulator
from Utils.card_tools import *
from Utils.types import *

VALID_CARD_IDS = set(range(52))

class HandEvaluator:
    def __init__(self, root_state: GameState, perspective: PlayerStr,
                 N_rollouts: int = 100):
        self.root_state = root_state
        self.perspective = perspective
        self.N_rollouts = N_rollouts
        self.belief_model = self._get_belief_model()

    def _get_belief_model(self):

        return BeliefModel(
            void_suits = {p: set() for p in self.root_state.player_order},
            unknown_cards = VALID_CARD_IDS - self.root_state.hands[self.perspective],
            hand_sizes={p: len(self.root_state.hands[p]) for p in self.root_state.player_order},
            perspective_player=self.perspective            
        )

    def _get_determinised_state(self) -> GameState:
        """
        Samples a possible world consistent with perspective beliefs and returns a determinised state.
        """

        # Sample a possible world consistent with beliefs
        sampled_hands: dict[PlayerStr, set[CardInt]] = self.belief_model.sample_world()
        sampled_hands[self.perspective] = self.root_state.hands[self.perspective]

        # Construct determinised state
        determinised_state = GameState(
            hands=sampled_hands,
            current_trick=self.root_state.current_trick,
            trump_suit=self.root_state.trump_suit,
            player_order=self.root_state.player_order,
            round_scores=dict(self.root_state.round_scores),
            bids=dict(self.root_state.bids),
            cards_remaining=self.root_state.cards_remaining
        )

        return determinised_state


    def _won_simulated_card_play(self, determinised_state: GameState, 
                                card_to_play: CardInt) -> int:
        """
        Simulates a trick where the perspective player plays their card.
        If the perspective player wins the trick, returns 1, else returns 0.
        """

        if not card_to_play:
            raise ValueError("No card to play")
        
        if 0 > card_to_play or 51 < card_to_play:
            raise ValueError("Invalid Card Chosen, must be with 0-51")
        
        # Create a deep copy of the determinised state to avoid modifying the original
        determinised_state_copy = copy.deepcopy(determinised_state)

        # Run rollout until perspective is reached
        simulator = RolloutSimulator(determinised_state_copy)

        # Play the specified card and evaluate the winner of the trick
        winner = simulator.rollout_trick(
                perspective=self.perspective,
                chosen_card=card_to_play
        )
        return 1 if winner == self.perspective else 0

    def estimate_optimal_move(self) -> dict:
        """
        Runs a Monte Carlo simulation to evaluate which card the player should play.
        Can only estimate legal moves based on the current hand. Returns summary of context in dictionary form.
        """ 

        # Initialise variables and dictionaries
        perspective_hand = list(self.root_state.hands[self.perspective])
        
        # Want to track, per card, how many times it was eligible to be played, and how many times it won
        tricks_won = {card: 0 for card in perspective_hand} 
        attempts_per_card = {card: 0.0 for card in perspective_hand} 

        for _ in range(self.N_rollouts):
            # This is to ensure that the belief model is updated with the current trick and the void suits are updated accordingly.
            determinised_state = self._get_determinised_state() 
    
            # Calculate the amount of legal moves the player can make
            true_legal_moves = determinised_state.get_legal_moves(self.perspective)
            
            # Generate move win percentage per card
            for card_to_play in true_legal_moves: 
                attempts_per_card[card_to_play] += 1 
                if self._won_simulated_card_play(determinised_state = determinised_state,
                                                card_to_play=card_to_play):
                    tricks_won[card_to_play] += 1  # Increment the count of tricks won for the card played
    
        # Expected win percentage for the card played if the card was played at all
        move_win_distribution = {
            id_to_initials(card): tricks_won[card] / attempts_per_card[card] 
            for card in perspective_hand if attempts_per_card[card] > 0
            }
    
        if not move_win_distribution:
            return {}

        mode = max(move_win_distribution.keys(), key=lambda key: move_win_distribution[key])
        minimum = min(move_win_distribution.keys(), key=lambda key: move_win_distribution[key])
        
        return {
            'optimal_move': mode,
            'optimal_move_probability': move_win_distribution[mode],
            'least_optimal_move': minimum,
            'lowest_move_probability': move_win_distribution[minimum], 
            'move_win_distribution': move_win_distribution
        }

    def estimate_optimal_bid(self) -> dict:
        """
        Runs Monte Carlo evaluation for current hand and determines most optimal bid based on hand.
        Only uses card initials (strings). Returns summary of context in dictionary form.
        """
        # Genrerate score output for each bid amoun
        distribution = self._simulate_round()
        
        scores_per_bid = self._calculate_scores_per_bid(distribution)

        mode = max(distribution.keys(), key=lambda key: distribution[key])

        return {
            "mode": mode,
            "expected_scores": scores_per_bid,
            "bid_accuracy_distribution": distribution,
            "mode_probability": distribution[mode],
        }
    
    def estimate_optimal_bid_baseline(self):
        """
        Runs Monte Carlo simulation for current hand and determines most optimal bid based on the hand playing random moves.
        Only uses card initials (strings). Returns summary of context in dictionary form.
        """

        distribution = self._simulate_round()
        scores_per_bid = self._calculate_scores_per_bid(distribution=distribution)

        mode = max(distribution.keys(), key=lambda key: distribution[key])

        return {
            "mode": mode,
            "expected_scores": scores_per_bid,
            "bid_accuracy_distribution": distribution,
            "mode_probability": distribution[mode],
    }

    def _simulate_round(self, bid: int = 9) -> dict[int, float]:

        """
        Simulation commences.
        Returns distribution of tricks won per bid:
        """
        bid_success_freq = {b: 0 for b in range(9)}
        bid_success_distribution = {b: 0.0 for b in range(9)}
        tricks_won = 0

        for _ in range(self.N_rollouts):
    
            # Sample a possible world consistent with beliefs
            # Run rollout until perspective is reached
            simulator = RolloutSimulator(self._get_determinised_state())
            final_scores = simulator.rollout_round()
            tricks_won = final_scores[self.perspective]
            bid_success_freq[tricks_won] += 1

        # Expected Score
        # Calculate distribution
        for b in range(9):
            bid_success_distribution[b] = round(bid_success_freq[b] / self.N_rollouts, 2)
     
        return bid_success_distribution

    def _calculate_score(self, tricks_won: int) -> int:
        """Based on nomination rules returns score"""

        if tricks_won > 8:
            return tricks_won
        if tricks_won == 8:
            return 36
        return tricks_won + 10

    def _calculate_scores_per_bid(self, distribution: dict[int, float]) -> dict[int, float]:

        scores_per_bid = {}
        for bid in range(9):
            premium = self._calculate_score(bid)
            # expected score = P(hit) * premium + sum over misses of P(miss_tricks) * miss_tricks
            expected = distribution[bid] * premium + sum(
                p * tricks for tricks, p in distribution.items() if tricks != bid
            ) # for example if you bid 5 and get 3 you still receive 3 points e.g p(t) * trick value
            scores_per_bid[bid] = round(expected, 1)

        return scores_per_bid