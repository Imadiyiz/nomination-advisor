import copy

from belief_model import BeliefModel
from game_engine import GameState
from rollout_simulator import RolloutSimulator

PlayerStr = str

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
            unknown_cards=self.root_state.valid_initials - self.root_state.hands[self.perspective],
            hand_sizes={p: len(self.root_state.hands[p]) for p in self.root_state.player_order},
            perspective_player=self.perspective            
        )

    def _get_determinised_state(self) -> GameState:
        """
        Samples a possible world consistent with perspective beliefs and returns a determinised state.
        """

        # Sample a possible world consistent with beliefs
        sampled_hands: dict[str, set[str]] = self.belief_model.sample_world()
        sampled_hands[self.perspective] = self.root_state.hands[self.perspective]

        # Construct determinised state
        determinised_state = GameState(
            hands=sampled_hands,
            current_trick=self.root_state.current_trick,
            leader=self.root_state.leader,
            trump_suit=self.root_state.trump_suit,
            player_order=self.root_state.player_order,
            round_scores=dict(self.root_state.round_scores),
            bids=dict(self.root_state.bids),
            cards_remaining=self.root_state.cards_remaining
        )

        return determinised_state


    def _won_simulated_card_play(self, determinised_state: GameState, 
                                card_to_play: PlayerStr = '') -> int:
        """
        Simulates a trick where the perspective player plays their card.
        If the perspective player wins the trick, returns 1, else returns 0.
        """
        
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
        summary_context = {}
        true_legal_moves = {}
        perspective_hand = list(self.root_state.hands[self.perspective])
        
        
        # Want to track, per card, how many times it was eligible to be played, and how many times it won
        tricks_won = {card: 0 for card in perspective_hand} 
        attempts_per_card = {card: 0 for card in perspective_hand} 

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
        expected_win_percentage = {
            card: tricks_won[card] / attempts_per_card[card] 
            for card in perspective_hand if attempts_per_card[card] > 0
            }
    
        if not expected_win_percentage:
            return {}
        
        summary_context['win_percentages'] = expected_win_percentage.items()
        max_win_percentage = max(list(expected_win_percentage.values()))
    
        # Determine the optimal card to play based on the highest win percentage
        for i, v in expected_win_percentage.items():
            if v == max_win_percentage:
                optimal_card = i
                summary_context['optimal_move'] = optimal_card
                summary_context['optimal_move_probability'] = v
                summary_context['least_optimal_move'] = min(list(expected_win_percentage.keys()), key=lambda k: expected_win_percentage[k])
                summary_context['lowest_move_probability'] = min(list(expected_win_percentage.values()))
                continue
    
    
        return summary_context

    def estimate_optimal_bid(self):
        """
        Runs Monte Carlo evaluation for current hand and determines most optimal bid based on hand.
        Only uses card initials (strings). Returns summary of context in dictionary form.
        """
        
        summary_context = {}
        score_per_bid = {}
        bid_accuracy_distribution = {}
        mode = 0
        maximum_expected_accuracy = 0

        # Genrerate score output for each bid amount
        # Note that the sim_bid doesn;t affect anything as the cards are played at random and not with heuristics
        for sim_bid in range(9): # Always up to 9 choices (0 - 8)

            simulation_results = self._simulate_round(bid = sim_bid)
            
            bid_successes = simulation_results["bid_successes"]
            total_nom_score = simulation_results["total_nom_score"]
    
            # calculations
    
            # Expected Score
            avg_nom_score = round(total_nom_score / self.N_rollouts, 1) 
            score_per_bid[sim_bid] = avg_nom_score
    
            # Bid Success Distribution
            bid_success_percentage = round(bid_successes / self.N_rollouts, 3) 
            bid_accuracy_distribution[sim_bid] = bid_success_percentage 
            print(bid_accuracy_distribution)
    
            maximum_expected_accuracy = max(list(bid_accuracy_distribution.values()))
        
        # Determine the mode of the bid accuracy distribution
        for i, v in bid_accuracy_distribution.items():
            if maximum_expected_accuracy == v:
                mode = i
                continue
    
        summary_context["mode"] = mode  # Most accurate bid
                
        # return context of ESPB and Bid accuracy
        summary_context["expected_scores"] = score_per_bid
        summary_context["bid_accuracy_distribution"] = bid_accuracy_distribution
        summary_context["mode_probability"] = bid_accuracy_distribution[mode]
        
        return summary_context
    
    def estimate_optimal_bid_baseline(self):
        """
        Runs Monte Carlo simulation for current hand and determines most optimal bid based on the hand playing random moves.
        Only uses card initials (strings). Returns summary of context in dictionary form.
        """
        
        summary_context = {}
        mode = 0

        # Genrerate score output for each bid amount
        # Note that the sim_bid doesn;t affect anything as the cards are played at random and not with heuristics

        simulation_results = self._simulate_round(bid = 3) # This is a future smell as the function will later make perspective play towards their bid,
        # However 9 assumes that they will play aggressive despite not getting the bonus points for 8 tricks won

        bid_accuracy_distribution_list = list(simulation_results["bid_accuracy_distribution"].items())
        bid_accuracy_distribution_list = sorted(bid_accuracy_distribution_list, 
                                           reverse=True,
                                           key=lambda z:z[1])

        mode = bid_accuracy_distribution_list[0][0]
        summary_context["mode"] = mode  # Most accurate bid

        # return context of ES and Bid accuracy
        summary_context["expected_score"] = simulation_results["avg_score"]
        summary_context["bid_accuracy_distribution"] = simulation_results["bid_accuracy_distribution"]
        summary_context["mode_probability"] = bid_accuracy_distribution_list[0][1]
        
        return summary_context

    def _simulate_round(self, bid: int):

        """
        Simulation commences. Currently for Baseline
        Returns simulation_results:
        """
        bid_success_freq = {b: 0 for b in range(9)}
        bid_success_distribution = {b: 0.0 for b in range(9)}
        bid_avg_score = {b: 0.0 for b in range(9)}
        premium_score_for_correct_bid = self._calculate_score(bid)
        tricks_won = 0
        avg_score  = 0

        for _ in range(self.N_rollouts):
    
            # Sample a possible world consistent with beliefs
            # Run rollout until perspective is reached
            simulator = RolloutSimulator(self._get_determinised_state())
            final_scores = simulator.rollout_round()
            tricks_won = final_scores[self.perspective]
            bid_success_freq[tricks_won] += 1

            # determine nom score
            if bid == tricks_won:
                bid_avg_score[tricks_won] += premium_score_for_correct_bid
            else:
                bid_avg_score[tricks_won] += tricks_won

        # Expected Score
        # Calculate distribution
        for b in range(9):
            bid_success_distribution[b] = round(bid_success_freq[b] / self.N_rollouts, 2)
            avg_score = round(sum(bid_avg_score.values()) / self.N_rollouts, 2)

        simulation_results = {
                 "bid_accuracy_distribution": bid_success_distribution,
                 "avg_score": avg_score,
            }

        return simulation_results

    def _calculate_score(self, actual: int) -> int:
        """Based on nomination rules returns score"""

        if actual > 8:
            return actual
        if actual == 8:
            return 36
        return actual + 10