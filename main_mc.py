from game_engine import GameState, RolloutSimulator
from belief_model import BeliefModel
from typing import Dict, Set

def estimate_optimal_bid(root_state: GameState, perspective: str, N_rollouts: int = 100) -> dict:
    """
    Runs Monte Carlo evaluation for current hand and determines most optimal bid based on hand.
    Only uses card initials (strings). Returns summary of context in dictionary form.
    """

    

    root_state.leader = perspective
    summary_context = {}
    score_per_bid = {}
    bid_accuracy = {}
    
    # Initialize belief model for perspective player
    belief_model = BeliefModel(
        void_suits={p: set() for p in root_state.player_order},
        known_cards=set(),
        unknown_cards=root_state.valid_initials - root_state.hands[perspective],
        hand_sizes={p: len(root_state.hands[p]) for p in root_state.player_order},
        perspective_player=perspective
    )

    for _bid in range(9):

        bid_successes = 0
        total_nom_score = 0


        for _ in range(N_rollouts):

            # Sample a possible world consistent with beliefs
            sampled_hands: Dict[str, Set[str]] = belief_model.sample_world()

            # Freeze hands as sets for GameState
            determinized_hands = {
                p: set(cards) for p, cards in sampled_hands.items()
            }

            # Overwrite perspective player's hand with truth
            determinized_hands[perspective] = root_state.hands[perspective]

            # Construct determinized state
            determinized_state = GameState(
                hands=determinized_hands,
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

            final_scores = simulator.rollout()
            result = final_scores[perspective]

            # generate perspective bid
            perspective_bid = _bid

            # if perspective wins sames amount as bids, score increases
            bid_spread = result - perspective_bid  

            # determine nom score
            if bid_spread == 0:
                total_nom_score += (result + 10) if result != 8 else (result + 10) * 2
            else:
                total_nom_score += result

            # also generate true percentage
            if result == perspective_bid:
                bid_successes += 1
        
            # calculations

            avg_nom_score = round(total_nom_score / N_rollouts, 2) 
            bid_success_percentage = round(bid_successes / N_rollouts, 2) 
            score_per_bid[_bid] = avg_nom_score
            bid_accuracy[_bid] = bid_success_percentage 

    # return context of ESPB and Bid accuracy
    summary_context["Estimated Score Per Bid"] = score_per_bid
    summary_context["Estimated Bid accuracy"] = bid_accuracy
    
    
    return summary_context

########

# Players
players = ("A", "B", "C", "D")
my_player = "A"

# Hands (sets of card initials)
hands = (
    ("A", set({"AS", "KS", "QS", "JS", "AH", "KH", "AD", "KD"})),  # very strong hand
    ("B", set({"2H", "4H", "6H", "8H", "9H", "JH", "QH", "3H"})),  # single-suit hand
    ("C", set({"3C", "5D", "7S", "9C", "10D", "JC", "QD", "2S"})), # mixed mid-strength
    ("D", set({"2C", "3D", "4S", "5C", "6D", "7C", "8D", "9S"})),  # very weak spread
)

root_state = GameState(
    hands=dict(hands),                 # Convert tuple pairs to dict
    current_trick=(),                  # No cards played yet
    leader=my_player,                  # A leads
    trump_suit="S",                    # Spades are trump
    player_order=players,
    round_scores={p: 0 for p in players},
    bids={p: 2 for p in players},      # Arbitrary example bids
    cards_remaining=8                  # 8 cards each
)

#########

bidding_estimates = {}

for player in players:
    bidding_estimates[player] = estimate_optimal_bid(
        root_state, N_rollouts=100, perspective=player)


print(f"Bidding estimation for {my_player}:")

for item in bidding_estimates.items():
    print(item)



# does work for me, it is calculating the wrong thing. 
# it needs to work out who wins the current hand, not the full round


# Write the whole logic flow on paper and see where the issues comes from