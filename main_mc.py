from game_engine import GameState, RolloutSimulator
from belief_model import BeliefModel
from typing import Dict, Set
from collections import defaultdict


# basic reward weighting which gives a maximum reward for equalling bid
# rewards decreases as the difference between the bid and actual score increases
# Slightly favours overestimating the bid compared to unachieving bid
reward_weighting = {
   -1: 0.1,
    0: 1,
    1: 0.15,
    2: 0.2,
    3: 0.25,
    4: 0.4,
    5: 0.5,
    6: 0.65,
    7: 0.8,
    8: 0.95,

}


def run_monte_carlo(root_state: GameState, perspective: str, N_rollouts: int = 100):
    """
    Runs Monte Carlo evaluation for all legal moves of the current leader.
    Only uses card initials (strings). Returns the best move.
    """

    root_state.leader = perspective
    
    def _get_legal_moves(player, state) -> set:
        """Returns a set of legal moves"""
        legal_moves = state.get_legal_moves(player)

        if not legal_moves:
            raise RuntimeError(f"No legal moves for player {player}")
        
        return legal_moves
        
    # Initialize belief model for perspective player
    belief_model = BeliefModel(
        void_suits={p: set() for p in root_state.player_order},
        known_cards=set(),
        unknown_cards=root_state.valid_initials - root_state.hands[perspective],
        hand_sizes={p: len(root_state.hands[p]) for p in root_state.player_order},
        perspective_player=perspective
    )

    # move score, and true percentrage frequency
    total_score = 0
    tp_freq = 0

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
        for i, v in root_state.bids.items():
            if i == perspective:
                perspective_bid = v

        # if perspective wins sames amount as bids, score increases
        bid_spread = result - perspective_bid  
        if bid_spread in reward_weighting:
            total_score += reward_weighting[bid_spread]

        # also generate true percentage
        if result == perspective_bid:
            tp_freq += 1
        
    # calculations

    move_score = round(total_score / N_rollouts, 2) 
    win_percentage = round(tp_freq / N_rollouts, 2) 

    # return context of distribution and expected tricks
    summary_context = {}
    summary_context["move_score"] = move_score 
    summary_context["Win_percentage"] = win_percentage 
    return summary_context

########

# Players
players = ("A", "B", "C", "D")
my_player = "A"

# Hands (sets of card initials)
hands = (
    ("A", set({"AS", "KS", "QS", "JS", "AH", "KH", "AD", "KD"})),  # very strong hand
    ("B", set({"2H", "4H", "6H", "8H", "9H", "JH", "QH", "KH"})),  # single-suit hand
    ("C", set({"3C", "5D", "7S", "9C", "10D", "JC", "QD", "KS"})), # mixed mid-strength
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
    bidding_estimates[player] = run_monte_carlo(
        root_state, N_rollouts=2000, perspective=player)


print(f"Bidding estimation for {my_player}:")

for item in bidding_estimates.items():
    print(item)



# does work for me, it is calculating the wrong thing. 
# it needs to work out who wins the current hand, not the full round


# Write the whole logic flow on paper and see where the issues comes from