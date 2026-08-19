import time

from Classes.DeckClass import Deck
from game_engine import GameState
from hand_evaluator import HandEvaluator
from Utils.card_tools import *

# Test Parameters
players_tuple = ("random", "weak", "single_suit", "strong")
players = list(players_tuple)
my_player = "random"
hand_size = 8
current_trick = ()

def convert_into_percentage(decimal: float) -> str:

    # Helper function to convert decimals into formatted percentagess
    if type(decimal) == float:
        return f"{(decimal * 100):.2f}%"

    raise ValueError("Valid decimal must be passed into function")

deck = Deck()
player_dict = {}
hands = ()

# Hands (sets of card initials) These are allowed to have duplicates as these are not the sampled hands in the simulation
hands = (
    ("strong", strong_hand()),
    ("weak", weak_hand()),
    ("single_suit", suited_hand()),
    ("random", random_hand()) 
)
 
# Generate root state
root_state = GameState(
    hands=dict(hands),                 # Convert tuple pairs to dict
    current_trick=current_trick,                 # (PlayerStr, CardStr)
    trump_suit="D",
    player_order=tuple(players),
    round_scores={p: 0 for p in players},
    bids={p: 2 for p in players},      # Arbitrary example bids
    cards_remaining=8                  # 8 cards each
)

bidding_estimates = {}
move_estimates = {}

# Start Estimation

strt_time = time.perf_counter()

for p in players:

    # ensure p is first to play
    players = players[players.index(p):] + players[:players.index(p)]

    # update root state
    root_state.player_order = tuple(players)

    bidding_estimates[p] = HandEvaluator(
        root_state=root_state,
        perspective=p,
        N_rollouts=500
    ).estimate_optimal_bid()

counter = 0
for i, v in bidding_estimates.items():

    print(f"Bidding estimation for {players_tuple[counter]}:")
    print("Expected Score")
    for i, value in v["expected_scores"].items():
        print(f"{i}: {value}")

    print("\nBid Accuracy Distribution")
    for i, value in v["bid_accuracy_distribution"].items():
        print(f"{i}: {value}")

    print("Highest Expected Score", max(v["expected_scores"].values()), '\n') # 
    print(f"Mode: {v["mode"]} ~ {convert_into_percentage(v["mode_probability"])}")

    counter += 1
###
players = list(players_tuple)
for p in players:

    # ensure p is first to play
    players = players[players.index(p):] + players[:players.index(p)]
    # update root state
    root_state.player_order = tuple(players)

    
    move_estimates[p] = HandEvaluator(
        root_state=root_state,
        perspective=p,
        N_rollouts=5000
    ).estimate_optimal_move()


for i, v in move_estimates.items():
    win_distribution_list = list(v["move_win_distribution"].items())
    sorted_win_percentage_list = sorted(win_distribution_list,
                                        key=lambda x:x[1],
                                        reverse=True)

    print(" ")
    print(" ")
    print(f"{i}'s hand ", root_state.hands[my_player])
    print("Win Percentage per Card:\n\n", "".join(f"{r}\n " for r in sorted_win_percentage_list))
    print(f"Most Optimal Card: {v["optimal_move"]} ~ {convert_into_percentage(v["optimal_move_probability"])}")
    print(f"Least Optimal Card: {v["least_optimal_move"]} ~ {convert_into_percentage(v["lowest_move_probability"])}")

# End time
end_time = time.perf_counter()
print(f"Execution time: {end_time - strt_time:.2f} seconds")