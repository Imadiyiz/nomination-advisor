import time

from game_engine import GameState
from hand_evaluator import HandEvaluator

players = ["A", "F", "B", "C"]
my_player = "A"
current_trick = ()

def convert_into_percentage(decimal: float) -> str:

    # Helper function to convert decimals into formatted percentagess
    if type(decimal) == float:
        return f"{(decimal * 100):.2f}%"

    raise ValueError("Valid decimal must be passed into function")

# Hands (sets of card initials) These are allowed to have duplicates as these are not the sampled hands in the simulation
hands = (
    # Very strong hand: Top-tier high cards (Ace, King, Queen, Jack, 10 of Spades + Ace of Clubs)
    ("A", set({"AS", "KS", "QS", "JS", "10S", "AC", "2D", "5C"})),  
    
    ("B", set({"KH", "QH", "JH", "10H", "9H", "8H", "AC", "KC"})),  
    
    # Mixed mid-strength: Mid-tier connected cards split evenly between Clubs and Diamonds
    ("C", set({"9C", "8C", "7C", "9D", "8D", "7D", "10D", "10C"})), 

    # Very weak spread: Unconnected low ranks across random suits with zero synergy
    ("F", set({ "2S", "3S", "2H", "3D", "2C", "4C", "AD", "AH"})),  
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
        N_rollouts=50
    ).estimate_optimal_bid()

print(f"Bidding estimation for {my_player}:")

for i, v in bidding_estimates.items():

    print("Expected Score")
    for i, value in v["expected_scores"].items():
        print(f"{i}: {value}")

    print("\nBid Accuracy Distribution")
    for i, value in v["bid_accuracy_distribution"].items():
        print(f"{i}: {value}")

    print("Highest Expected Score", max(v["expected_scores"].values()), '\n') # 
    print(f"Mode: {v["mode"]} ~ {convert_into_percentage(v["mode_probability"])}")

###
players = ["A", "F", "B", "C"]
for p in players:

    # ensure p is first to play
    players = players[players.index(p):] + players[:players.index(p)]
    # update root state
    root_state.player_order = tuple(players)

    
    move_estimates[p] = HandEvaluator(
        root_state=root_state,
        perspective=p,
        N_rollouts=500
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