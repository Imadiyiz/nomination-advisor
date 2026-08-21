import time

from bot import BotPlayer
from Classes.deck import Deck
from game_engine import GameState
from hand_evaluator import HandEvaluator
from Utils.card_tools import *
from Utils.hand_generators import *

# Test Parameters
#players_tuple = ("strong", "weak", "suited", "random")
players_tuple = ("random1","random2",
                 "random3", "random4")

players = list(players_tuple)
my_player = "random"
current_trick = ()
bot_players = [BotPlayer(name = name) for name in players_tuple]
N_rollouts = 500

# Constants
PRINT_BID_EVAL = False
PRINT_MOVE_EVAL = False
PRINT_NAIVE_BIDS = False
PRINT_NAIVE_BIDS_DIFFERENCE_DISTRIBUTION = True
HAND_SIZE = 8


def convert_into_percentage(decimal: float) -> str:

    # Helper function to convert decimals into formatted percentagess
    if type(decimal) == float:
        return f"{(decimal * 100):.2f}%"

    raise ValueError("Valid decimal must be passed into function")

deck = Deck()

"""# Hands (sets of card initials) These are allowed to have duplicates as these are not the sampled hands in the simulation
test_hand_generators = ( 
    strong_hand(deck),
    weak_hand(deck),
    suited_hand(deck),
    random_hand(deck) 
)"""

hand_generators = (
    random_hand,
    random_hand,
    random_hand,
    random_hand,
    random_hand,
    random_hand
)
if PRINT_NAIVE_BIDS_DIFFERENCE_DISTRIBUTION:
    print("PRINT_NAIVE_BIDS_DIFFERENCE_DISTRIBUTION")
    round_difference_distribution = {}
    for _ in range(N_rollouts):

        naive_bids = {}
        banned = -1
        bid_total = 0

        #reset deck
        deck = Deck()
        hands = [
            (bot_player, generator(deck, HAND_SIZE))
            for bot_player, generator in zip(
                players, 
                [gen for gen in hand_generators]
                )
        ]
        hands = dict(hands)

        # Must check that all the bids do not add up to banned
        for i, bot in enumerate(bot_players):
            if (i == len(bot_players) - 1): 
                banned = HAND_SIZE - bid_total

            bid = bot.determine_baseline_bid(
                hand=hands[bot.name],
                player_amount=len(players),
                trump_suit=format_string("Diamonds"),
                restriction=banned
            )
            naive_bids[bot.name] = bid
            bid_total += bid

        # Distribution forming 
        bid_diff = sum(naive_bids.values()) - HAND_SIZE   
        if bid_diff not in round_difference_distribution:
            round_difference_distribution[bid_diff] = 1
        else:
            round_difference_distribution[bid_diff] += 1

    for i, v in round_difference_distribution.items():
        round_difference_distribution[i] = round(v / N_rollouts, 2)

    round_diff_dist_list = list(round_difference_distribution.items())
    sorted_rddl = sorted(round_diff_dist_list,
                         key = lambda x: x[1],
                         reverse=True)
    for dist in sorted_rddl:
        if dist[1] > 0.01:
            print(dist)

if PRINT_NAIVE_BIDS:
    for bot_bid in naive_bids.items():
        print("Bot hand")
        print([id_to_initials(card) for card in hands[bot_bid[0]]])
        print(bot_bid)

# Generate root state
root_state = GameState(
    hands=dict(hands),                 # Convert tuple pairs to dict
    current_trick=current_trick,                 # (PlayerStr, CardStr)
    trump_suit=format_string("Diamonds"),             # Must be the prose
    player_order=tuple(players),
    round_scores={p: 0 for p in players},
    total_scores={p: 0 for p in players},
    bids=naive_bids,      # Arbitrary example bids
    cards_remaining=HAND_SIZE                  # 8 cards each
)

bidding_estimates = {}
move_estimates = {}

# Start Estimation

strt_time = time.perf_counter()

if PRINT_BID_EVAL:
    for p in players:

        # ensure p is first to play
        players = players[players.index(p):] + players[:players.index(p)]

        # update root state
        root_state.player_order = tuple(players)

        bidding_estimates[p] = HandEvaluator(
            state=root_state,
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

if PRINT_MOVE_EVAL:
    players = list(players_tuple)

    for p in players:

        # ensure p is first to play
        players = players[players.index(p):] + players[:players.index(p)]
        # update root state
        root_state.player_order = tuple(players)

        
        move_estimates[p] = HandEvaluator(
            state=root_state,
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