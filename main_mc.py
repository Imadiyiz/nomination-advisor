from game_engine import GameState
from hand_evaluator import HandEvaluator

########


players = ["A", "F", "B", "C"]
my_player = "A"
current_trick = ()

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
    leader=players[len(current_trick)],                    # Diamonds are trump
    player_order=tuple(players),
    round_scores={p: 0 for p in players},
    bids={p: 2 for p in players},      # Arbitrary example bids
    cards_remaining=8                  # 8 cards each
)

bidding_estimates = {}

# Start Estimation

for p in players:

    # ensure p is first to play

    players = players[players.index(p):] + players[:players.index(p)]

    # update root state
    root_state.player_order = tuple(players)

    bidding_estimates[p] = HandEvaluator(
        root_state=root_state,
        perspective=p,
        N_rollouts=5000
    ).estimate_optimal_bid_baseline()

print(f"Bidding estimation for {my_player}:")

for i, v in bidding_estimates.items():
    print("\nPlayer", i)

    #print("Expected Score")
    #for i, value in v["expected_score"].items():
    #    print(f"{i}: {value}") this isn't wrong but doesn quite work for baseline
    # Wouldn't it make sense for the baseline considering its random that you splits N_rollout equally and then assining the bid
    # accordingly so that everything is randomly sampled.

    print("Bid Accuracy Distribution")
    for i, value in v["bid_accuracy_distribution"].items():
        print(f"{i}: {value}")

    print("Highest Expected Score", v["expected_score"], '\n')
    print(f"Mode: {v["mode"]} ~ {v["mode_probability"] * 100}%")