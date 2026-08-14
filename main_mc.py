import copy

from belief_model import BeliefModel
from game_engine import GameState, RolloutSimulator


def get_true_legal_moves(determinised_state: GameState, perspective: str) -> set[str]:
    """
    Advances the gamnestate until it is the perspective player's turn to play, 
    then returns the legal moves for that player."""


    determinised_state_copy = copy.deepcopy(determinised_state)
    simulator = RolloutSimulator(determinised_state_copy)

    # Advance the game state until it is the perspective player's turn and return the legal moves for that player
    legal_moves = simulator.rollout_trick_until_perspective(perspective=perspective)

    print(f"Legal cards to play for {perspective}: {legal_moves} GTLM")  # Debugging statement

    return legal_moves   # Still inaccurate

def get_determinised_state(root_state: GameState, belief_model: BeliefModel, perspective: str) -> GameState:
    """
    Samples a possible world consistent with beliefs and returns a determinised state.
    """

    # Sample a possible world consistent with beliefs
    sampled_hands: dict[str, set[str]] = belief_model.sample_world()
    sampled_hands[perspective] = root_state.hands[perspective]

    # Construct determinised state
    determinised_state = GameState(
        hands=sampled_hands,
        current_trick=root_state.current_trick,
        leader=root_state.leader,
        trump_suit=root_state.trump_suit,
        player_order=root_state.player_order,
        round_scores=dict(root_state.round_scores),
        bids=dict(root_state.bids),
        cards_remaining=root_state.cards_remaining
    )

    return determinised_state

def simulate_round(root_state: GameState, N_rollouts: int, perspective: str, belief_model: BeliefModel, bid: int):

        """
        Simulation commences.
        Returns simulation_results: dict[bid_successes: value, total_nom_score: value]
        """
        bid_successes = 0
        total_nom_score = 0

        for _ in range(N_rollouts):
    
            # Sample a possible world consistent with beliefs
            determinised_state = get_determinised_state(root_state, belief_model, perspective)

            # Run rollout until perspective is reached
            simulator = RolloutSimulator(determinised_state)
            final_scores = simulator.rollout_round()
            result = final_scores[perspective]

            # determine nom score
            nom_score = calculate_score(result, bid)
            total_nom_score += nom_score

            # also generate true percentage
            if result == bid:
                bid_successes += 1

        simulation_results = {
                 "bid_successes": bid_successes,
                 "total_nom_score": total_nom_score,
            }

        return simulation_results



def simulate_card_play(determinised_state: GameState,
                    perspective: str, card_to_play: str = '') -> int:

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
                perspective=perspective,
                chosen_card=card_to_play
        )
        return 1 if winner == perspective else 0


def calculate_score(actual: int , bid: int) -> int:
    """Based on nomination rules returns score"""

    if actual != bid:
        return actual
    if actual == 8:
        return 36
    return actual + 10


def estimate_optimal_move(root_state: GameState, perspective: str, N_rollouts: int = 100) -> dict:
    """
    Runs a Monte Carlo simulation to evaluate which card the player should play.
    Can only estimate legal moves based on the current hand. Returns summary of context in dictionary form.
    """ 

    # Initialise variables and dictionaries
    summary_context = {}
    true_legal_moves = {}
    perspective_hand = list(root_state.hands[perspective])
    tricks_won = {card: 0 for card in perspective_hand}  # Dictionary to store the number of tricks won for each card played


    # Want to track, per card, how man  times it was eligible to be played, and how many times it won

    attempts_per_card = {card: 0 for card in perspective_hand}  # Dictionary to store the number of attempts for each card played    


    # Initialise original belief for perspective player
    belief_model = BeliefModel(
        void_suits = {p: set() for p in root_state.player_order}, 
        unknown_cards=root_state.valid_initials - root_state.hands[perspective],
        hand_sizes={p: len(root_state.hands[p]) for p in root_state.player_order},
        perspective_player=perspective
        )

    for _ in range(N_rollouts):
        # This is to ensure that the belief model is updated with the current trick and the void suits are updated accordingly.
        determinised_state = get_determinised_state(root_state, belief_model, perspective) 

        # Calculate the amount of legal moves the player can make
        true_legal_moves = get_true_legal_moves(determinised_state, perspective) # inaccurate, truth is within the simulator instance
        print(f"Legal cards to play for {perspective}: {true_legal_moves} TLM")  # Debugging statement

        # Generate move win percentage per card

        for card_to_play in true_legal_moves:
            print("LOOP")
            print("True Legal Moves", true_legal_moves)
            print("Card to play", card_to_play)
            print(f"Current trick: {determinised_state.current_trick}, Leader: {determinised_state.leader}, Next Player: {determinised_state._next_player()}")  # Debugging statement
            print(f"Simulating play for {perspective} playing {card_to_play}...")  # Debugging statement     #
            attempts_per_card[card_to_play] += 1  # Increment the count of attempts for the card played
            if simulate_card_play(determinised_state = determinised_state,
                                            perspective=perspective,
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
            optimal_card = perspective_hand.index(i)
            summary_context['optimal_move'] = optimal_card
            summary_context['optimal_move_probability'] = v
            summary_context['least_optimal_move'] = min(list(expected_win_percentage.keys()), key=lambda k: expected_win_percentage[k])
            summary_context['lowest_move_probability'] = min(list(expected_win_percentage.values()))
            continue


    return summary_context

def estimate_optimal_bid(root_state: GameState, perspective: str, N_rollouts: int = 100) -> dict:
    """
    Runs Monte Carlo evaluation for current hand and determines most optimal bid based on hand.
    Only uses card initials (strings). Returns summary of context in dictionary form.
    """

    summary_context = {}
    score_per_bid = {}
    bid_accuracy_distribution = {}
    mode = 0
    maximum_expected_accuracy = 0
    
    # Initialize belief model for perspective player
    belief_model = BeliefModel(
        void_suits={p: set() for p in root_state.player_order},
        unknown_cards=root_state.valid_initials - root_state.hands[perspective],
        hand_sizes={p: len(root_state.hands[p]) for p in root_state.player_order},
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

########

# Players
players = ("A", "B", "C", "F")
my_player = "A"

# Hands (sets of card initials)
hands = (
    # Very strong hand: Top-tier high cards (Ace, King, Queen, Jack, 10 of Spades + Ace of Clubs)
    ("A", set({"AS", "KS", "QS", "JS", "10S", "AC"})),  
    
    # Single-suit hand: A complete 6-card flush consisting entirely of Hearts
    ("B", set({"KH", "QH", "JH", "10H", "9H", "8H"})),  
    
    # Mixed mid-strength: Mid-tier connected cards split evenly between Clubs and Diamonds
    ("C", set({"9C", "8C", "7C", "9D", "8D", "7D"})), 
    
    # Very weak spread: Unconnected low ranks across random suits with zero synergy
    ("F", set({ "3S", "2H", "3D", "2C", "4C"})),  
)


root_state = GameState(
    hands=dict(hands),                 # Convert tuple pairs to dict
    current_trick=(('F', '2S'),),                 # (PlayerStr, CardStr)
    leader="F",                        # A leads (must always be the first player in the trick)
    trump_suit="S",                    # Clubs are trump
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