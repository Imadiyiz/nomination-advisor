from game_engine import GameState, RolloutSimulator
from belief_model import BeliefModel
from typing import Dict, Set
import random
from collections import defaultdict


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


    total_score = 0

    for _ in range(N_rollouts):

        distributions = defaultdict(int)


        # Sample a possible world consistent with beliefs
        sampled_hands: Dict[str, Set[str]] = belief_model.sample_world()

        # Freeze hands as frozensets for GameState
        determinized_hands = {
            p: frozenset(cards) for p, cards in sampled_hands.items()
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

        #determine move 
        legal_moves = _get_legal_moves(perspective, determinized_state)
        move = random.choice(list(legal_moves))

        final_scores = simulator.rollout()
        result = final_scores[perspective]

        total_score += result
        distributions[result] += 1


    # calculations

    bidding_estimation = total_score / N_rollouts

    probabilities = {
        tricks: count / N_rollouts
        for tricks, count in distributions.items()
    }

    # return context of distribution and expected tricks
    summary_context = {}
    summary_context["distribution"] = probabilities
    summary_context["expected_tricks"] = bidding_estimation 
    return summary_context

########

# Players
players = ("A", "B", "C", "D")

# Hands (frozensets of card initials)
hands = (
    ("A", frozenset({"AS", "KS", "QS", "JS", "AH", "KH", "AD", "KD"})),  # very strong hand
    ("B", frozenset({"2H", "4H", "6H", "8H", "9H", "JH", "QH", "KH"})),  # single-suit hand
    ("C", frozenset({"3C", "5D", "7S", "9C", "10D", "JC", "QD", "KS"})), # mixed mid-strength
    ("D", frozenset({"2C", "3D", "4S", "5C", "6D", "7C", "8D", "9S"})),  # very weak spread
)

root_state = GameState(
    hands=dict(hands),                 # Convert tuple pairs to dict
    current_trick=(),                  # No cards played yet
    leader="C",                        # A leads
    trump_suit="H",                    # Hearts are trump
    player_order=players,
    round_scores={p: 0 for p in players},
    bids={p: 1 for p in players},      # Arbitrary example bids
    cards_remaining=8                  # 8 cards each
)

#########

bidding_estimates = {}

for player in players:
    bidding_estimates[player] = run_monte_carlo(
        root_state, N_rollouts=2500, perspective=player)


print(f"Bidding estimation for {root_state.leader}:")
print(f"{bidding_estimates.items()}")



# does work for me, it is calculating the wrong thing. 
# it needs to work out who wins the current hand, not the full round


"""

"""