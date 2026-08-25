from belief_model import BeliefModel
from game_engine import GameState
from rollout_simulator import RolloutSimulator
from Utils.card_tools import *
from Utils.nom_rule_tools import calculate_correct_bid_score
from Utils.types import *

VALID_CARD_IDS = set(range(52))

class HandEvaluator:
    def __init__(self, state: GameState, perspective: PlayerStr,
                 N_rollouts: int = 100):

        """Monte Carlo hand evaluator class"""
        self.state = state
        self.perspective = perspective
        self.N_rollouts = N_rollouts
        self.belief_model = self._get_belief_model()

    def _get_belief_model(self):

        return BeliefModel(
            void_suits = {p: set() for p in self.state.player_order},
            unknown_cards = VALID_CARD_IDS - self.state.hands[self.perspective],
            hand_sizes={p: len(self.state.hands[p]) for p in self.state.player_order},
            perspective_player=self.perspective            
        )

    def _get_determinised_state(self) -> GameState:
        """
        Samples a possible world consistent with perspective beliefs and returns a determinised state.
        """

        # Sample a possible world consistent with beliefs
        sampled_hands: dict[PlayerStr, set[CardInt]] = self.belief_model.sample_world()
        sampled_hands[self.perspective] = set(self.state.hands[self.perspective])

        # Construct determinised state
        determinised_state = GameState(
            hands=dict(sampled_hands),
            current_trick=tuple(self.state.current_trick),
            trump_suit=str(self.state.trump_suit),
            player_order=tuple(self.state.player_order),
            round_scores=dict(self.state.round_scores),
            total_scores=dict(self.state.total_scores),
            bids=dict(self.state.bids),
            cards_remaining=int(self.state.cards_remaining)
        ) # Adjusted this so that it is not possible to change gamestate for HE instance

        return determinised_state

    def estimate_optimal_move(self, rollout_type:str = 'RANDOM') -> dict:
        """
        Runs a Monte Carlo simulation to evaluate which card the player should play.
        Can only estimate legal moves based on the current hand. Returns summary of context in dictionary form.
        """ 

        # Initialise variables and dictionaries
        perspective_bid = self.state.bids[self.perspective]
        expected_scores = {}

        # Calculate the amount of legal moves the player can make
        true_legal_moves = self.state.get_legal_moves(self.perspective)


        # Generate move win percentage per card
        for card_to_play in true_legal_moves: 
            # Simulates a round where the perspective has played their move
            expected_score = self._simulate_round_for_expected_move(player=self.perspective,
                                                                             move=card_to_play,
                                                                             bid=perspective_bid,
                                                                             rollout_type=rollout_type)
            expected_scores[card_to_play] = expected_score
    
        # Expected score for the card played if the card was played at all

        if not expected_scores:
            return {}

        mode = max(expected_scores.keys(), key=lambda key: expected_scores[key])
        minimum = min(expected_scores.keys(), key=lambda key: expected_scores[key])
        
        return {
            'optimal_move': mode,
            'optimal_move_probability': expected_scores[mode],
            'least_optimal_move': minimum,
            'lowest_move_probability': expected_scores[minimum], 
            'move_expected_scores': expected_scores.items()
        }

    def _calculate_tricks_won_probabilities(self, rollout_type: str = 'RANDOM') -> dict:
        """
        Runs Monte Carlo evaluation for current hand and determines most optimal bid based on hand.
        Only uses card initials (strings). Returns summary of context in dictionary form.

        Returns:
            "mode": int, 
            "expected_scores": dict[int, float],
            "tricks_won_distribution": dict[int, float],
            "mode_probability": float
        """
        # Genrerate score output for each bid amount
        tricks_won_distribution = self._simulate_round_for_expected_bid(rollout_type=rollout_type)
        
        scores_per_bid = self._calculate_scores_per_bid(tricks_won_distribution)

        mode = max(tricks_won_distribution.keys(),
                   key=lambda key: tricks_won_distribution[key])

        # expected_scores doesn't quite make sense at the moment since it does not factor
        # round score or total score
        return {
            "mode": mode,
            "raw_expected_scores": scores_per_bid, 
            "tricks_won_distribution": tricks_won_distribution,
            "mode_probability": tricks_won_distribution[mode],
        }

    def _simulate_round_for_expected_bid(self, rollout_type: str = 'RANDOM') -> dict[int, float]:

        """
        Simulation commences.

        Args:
            simulation_type: (str)
            RANDOM ~ Players make random moves, 
            NAIVE ~ Players make naive moves based on expected outcomes
        Returns distribution of tricks won per bid:
        """

        # Sanitise rollout type
        rollout_type = rollout_type.upper()

        tricks_won_freq = {b: 0 for b in range(9)}
        tricks_won_distribution = {b: 0.0 for b in range(9)}
        tricks_won = 0
        initial_bids = {}

        # simulator instance created with a sampled possible world consistent with perspective beliefs
        sim = RolloutSimulator(self._get_determinised_state())

        # Determine initial/placeholder bid
        if not sim.state.bids:
            initial_bids = self._strong_card_bid_initialiser(simulator=sim)


        for _ in range(self.N_rollouts):

            # Determinised state used for simulation needs updated initial bids
            d_state = self._get_determinised_state()
            if initial_bids:
                d_state.bids = initial_bids

            simulator = RolloutSimulator(d_state)
            # Determine type of rollout
            rollout_map = {
                'RANDOM' : simulator.random_rollout_round,
                'NAIVE' : simulator.naive_rollout_round,
            }

            # Run rollout until perspective is reached
            final_scores = rollout_map[rollout_type]()
            tricks_won = final_scores[self.perspective]
            tricks_won_freq[tricks_won] += 1

        # Calculate distribution
        for b in range(9):
            tricks_won_distribution[b] = round(tricks_won_freq[b] / self.N_rollouts, 2)
     
        return tricks_won_distribution
    
    def _simulate_round_for_expected_move(self,
                                          move: CardInt,
                                          player: PlayerStr,
                                          bid: int,
                                          rollout_type: str = 'RANDOM') -> float:

        """
        Simulation commences.

        Args:
            simulation_type: (str)
            RANDOM, BASELINE
        Returns expected score achieved when playing a move:
        """

        # Sanitise rollout type
        rollout_type = rollout_type.upper()

        total_move_score = 0 
        # determinised state which is derived from root state but can be altered to perform MC
        d_state = self._get_determinised_state().apply_move(
                player=player, card=move) # Applies the intended move to the state before evaluating the remaining moves

        for _ in range(self.N_rollouts):
    
            # simulator instance created with a sampled possible world consistent with perspective beliefs
            simulator = RolloutSimulator(d_state)  

            # Determine type of rollout
            rollout_map = {
                'RANDOM' : simulator.random_rollout_round,
                'NAIVE' : simulator.naive_rollout_round,
            }

            final_scores = rollout_map[rollout_type]()
            tricks_won = final_scores[self.perspective]

            if tricks_won == bid:
                total_move_score += calculate_correct_bid_score(tricks_won)
            else:
                total_move_score += tricks_won

        # Calculate Expected Score

     
        return round(total_move_score / self.N_rollouts, 1)

    def _calculate_scores_per_bid(self, distribution: dict[int, float]) -> dict[int, float]:

        scores_per_bid = {}
        for bid in range(9):
            premium = calculate_correct_bid_score(bid)
            # expected score = P(hit) * premium + sum over misses of P(miss_tricks) * miss_tricks
            expected = distribution[bid] * premium + sum(
                p * tricks for tricks, p in distribution.items() if tricks != bid
            ) # for example if you bid 5 and get 3 you still receive 3 points e.g p(t) * trick value
            scores_per_bid[bid] = round(expected, 1)

        return scores_per_bid

    def _strong_card_bid_initialiser(self, simulator: RolloutSimulator,) -> dict[PlayerStr, int]:
        """Initialises bids based on Strong Cards, while respecting restriction and passes them back as a dict"""

        initial_bids = {}
        bid_total = 0
        banned_bid = -1
        hand_size = len(simulator.state.hands[self.perspective])
        player_amount = len(simulator.bot_players_map.values())

        for i, bot in enumerate(simulator.bot_players_map.values()):
            if i == player_amount - 1:
                banned_bid = hand_size - bid_total
            bid = bot.determine_SC_bid(
                hand=simulator.state.hands[bot.name],
                trump_suit=simulator.state.trump_suit,
                table_size=len(simulator.state.hands),
                restriction=banned_bid
            )
            initial_bids[bot.name] = bid
            bid_total += bid

        return initial_bids