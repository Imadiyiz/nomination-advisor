from belief_model import BeliefModel
from game_engine import GameState, RolloutSimulator


def simulate_round(root_state: GameState, N_rollouts: int, perspective: str, belief_model: BeliefModel, bid: int):

        """
        Simulation commences.
        Returns simulation_results: dict[bid_successes: value, total_nom_score: value]
        """

        # Initialise totals
        bid_successes = 0
        total_nom_score = 0

        for _ in range(N_rollouts):
        
                    # Sample a possible world consistent with beliefs
                    sampled_hands: dict[str, set[str]] = belief_model.sample_world()
                    sampled_hands[perspective] = root_state.hands[perspective]
        
                    # Construct determinized state
                    determinized_state = GameState(
                        hands=sampled_hands,
                        current_trick=root_state.current_trick,
                        leader=root_state.leader,
                        trump_suit=root_state.trump_suit,
                        player_order=root_state.player_order,
                        round_scores=dict(root_state.round_scores),
                        bids=dict(root_state.bids),
                        cards_remaining=root_state.cards_remaining
                    )
        
                    # Run rollout until perspective is reached
                    simulator = RolloutSimulator(determinized_state)
        
                    final_scores = simulator.rollout_round()
                    result = final_scores[perspective]
        
                    # generate perspective bid
                    perspective_bid = bid
        
                    # determine nom score
                    nom_score = calculate_score(result, perspective_bid)
        
                    total_nom_score += nom_score
        
                    # also generate true percentage
                    if result == perspective_bid:
                        bid_successes += 1

        simulation_results = {
                 "bid_successes": bid_successes,
                 "total_nom_score": total_nom_score,
            }

        return simulation_results



def simulate_trick(root_state: GameState, N_rollouts: int,
                    perspective: str, belief_model: BeliefModel,
                    card_to_play: str):

        """
        Simulation commences.
        Returns tricks_won
        """

        # Initialise totals
        tricks_won = 0

        for _ in range(N_rollouts):
        
                    # Sample a possible world consistent with beliefs
                    sampled_hands: dict[str, set[str]] = belief_model.sample_world()
                    sampled_hands[perspective] = root_state.hands[perspective]
        
                    # Construct determinized state
                    determinized_state = GameState(
                        hands=sampled_hands,
                        current_trick=root_state.current_trick,
                        leader=root_state.leader,
                        trump_suit=root_state.trump_suit,
                        player_order=root_state.player_order,
                        round_scores=dict(root_state.round_scores),
                        bids=dict(root_state.bids),
                        cards_remaining=root_state.cards_remaining
                    )
        
                    # Run rollout until perspective is reached
                    simulator = RolloutSimulator(determinized_state)
        
                    winner = simulator.rollout_trick(
                         perspective=perspective,
                         chosen_card=card_to_play
                    )
                    if winner == perspective:
                         tricks_won += 1


        return tricks_won

def calculate_score(actual:int , bid:int) -> int:
    """Based on nomination rules returns score"""

    if actual != bid:
        return actual

    if actual == 8:
        return 36

    return actual + 10


def estimate_optimal_move(root_state: GameState, perspective: str, N_rollouts: int = 100) -> dict:
    """
    Runs a Monte Carlo simulation to evaluate which card the player should play
    Returns summary of context in dictinionary form.
    """ 

    # Initialise variables and dictionaries
    root_state.leader = perspective
    summary_context = {}
    optimal_card = ''
    perspective_win_percentages = {}
    current_hand_size = len(root_state.hands[perspective])

    perspective_hand = list(root_state.hands[perspective])

    # Initialise original belief for perspective player
    belief_model = BeliefModel(
        void_suits = {p: set() for p in root_state.player_order}, 
        unknown_cards=root_state.valid_initials - root_state.hands[perspective],
        hand_sizes={p: len(root_state.hands[perspective]) for p in root_state.player_order},
        perspective_player=perspective)

    # Generate move win percentage per card

    for move_index in range(current_hand_size): 
        win_percentage = 0.0
        # Sample a possible world consistent with current beliefs
        sampled_hands: dict[str, set[str]] = belief_model.sample_world()
        sampled_hands[perspective] = root_state.hands[perspective]
        card_to_play = perspective_hand[move_index]

        tricks_won = simulate_trick(root_state=root_state,
                                        N_rollouts=N_rollouts,
                                        perspective=perspective,
                                        belief_model=belief_model,
                                        card_to_play=card_to_play)

        win_percentage = round(tricks_won / N_rollouts, 2)

        perspective_win_percentages[perspective_hand[move_index]] = win_percentage

    summary_context['win_percentages'] = perspective_win_percentages.items()


    for i, v in perspective_win_percentages.items():
        if v == max(list(perspective_win_percentages.values())):
            optimal_card = perspective_hand[perspective_hand.index(i)]
            summary_context['optimal_move'] = optimal_card
            summary_context['optimal_move_probability'] = v
            continue


    return summary_context

def estimate_optimal_bid(root_state: GameState, perspective: str, N_rollouts: int = 100) -> dict:
    """
    Runs Monte Carlo evaluation for current hand and determines most optimal bid based on hand.
    Only uses card initials (strings). Returns summary of context in dictionary form.
    """

    root_state.leader = perspective
    summary_context = {}
    score_per_bid = {}
    bid_accuracy_distribution = {}
    mode = 0
    
    # Initialize belief model for perspective player
    belief_model = BeliefModel(
        void_suits={p: set() for p in root_state.player_order},
        unknown_cards=root_state.valid_initials - root_state.hands[perspective],
        hand_sizes={p: len(root_state.hands[perspective]) for p in root_state.player_order},
        perspective_player=perspective
    )

    # Generate score output for each bid amount

    for _bid in range(9): # Always up to 9 choices (0 - 8)

        simulation_results = simulate_round(root_state=root_state,
                                      N_rollouts=N_rollouts,
                                      perspective=perspective,
                                      belief_model=belief_model,
                                      bid = _bid)
        bid_successes = simulation_results["bid_successes"]
        total_nom_score = simulation_results["total_nom_score"]

        # calculations

        # Expected Score
        avg_nom_score = round(total_nom_score / N_rollouts, 1) 
        score_per_bid[_bid] = avg_nom_score

        # Bid Success Distribution
        bid_success_percentage = round(bid_successes / N_rollouts, 3) 
        bid_accuracy_distribution[_bid] = bid_success_percentage 

    for i, v in bid_accuracy_distribution.items():
        if max(list(bid_accuracy_distribution.values())) == v:
            mode = i
            continue

    summary_context["mode"] = mode  # Most accurate bid
            
    # return context of ESPB and Bid accuracy
    summary_context["expected_scores"] = score_per_bid
    summary_context["bid_accuracy_distribution"] = bid_accuracy_distribution
    summary_context["mode_probability"] = bid_accuracy_distribution[mode]
    
    return summary_context

########

# Players
players = ("A", "B", "C", "D")
my_player = "A"

# Hands (sets of card initials)
hands = (
    ("A", set({"AS", "KS", "QC", "JC", "10D", "9D", "8D", "7H"})),  # very strong hand
    ("B", set({})),  # single-suit hand
    ("C", set({})), # mixed mid-strength
    ("F", set({})),  # very weak spread
)

root_state = GameState(
    hands=dict(hands),                 # Convert tuple pairs to dict
    current_trick=( ),                 # (PlayerStr, CardStr)
    leader="C",                        # A leads
    trump_suit="D",                    # Hearts are trump
    player_order=players,
    round_scores={p: 0 for p in players},
    bids={p: 2 for p in players},      # Arbitrary example bids
    cards_remaining=8                  # 8 cards each
)

#########

bidding_estimates = {}

"""# Start Estimation

bidding_estimates[my_player] = estimate_optimal_bid(
   root_state, N_rollouts=100, perspective=my_player)



print(f"Bidding estimation for {my_player}:")

for i, v in bidding_estimates.items():
    print("\nPlayer", i)
    print("Expected Scores", v["expected_scores"])
    print("Highest Expected Score", max(v["expected_scores"].values()), '\n')
    print("Mode", v["mode"])
    print("Mode Probability", v["mode_probability"])
    print("\n")"""