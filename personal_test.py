from bot import BotPlayer
from Classes.deck import Deck
from game_engine import GameState
from hand_evaluator import HandEvaluator
from Utils.card_tools import *
from Utils.hand_generators import *
from Utils.types import *
from rollout_simulator import RolloutSimulator
import copy

# Test Parameters
#players_tuple = ("strong", "weak", "suited", "random")
players_tuple = ("random1","random2","random3","random4")
players = list(players_tuple)
my_player = "random"
current_trick = ()
bot_players = [BotPlayer(name = name) for name in players_tuple]
deck = Deck()
my_player = players_tuple[0]

# Constants
HAND_SIZE = 8
N_ROLLOUTS = 100


# PRINT FLAGS

PRINT_EXPECTED_BID = False
PRINT_HANDS = True
PRINT_NAIVE_MONTE_CARLO_ESTIMATE_MOVE = True
ROLLOUT_TYPE = 'RANDOM'

hand_generators = (
    random_hand,
    random_hand,
    random_hand,
    random_hand
)

hands = (
            (bot_player, generator(deck, HAND_SIZE))
            for bot_player, generator in zip(
                players, 
                [gen for gen in hand_generators]
                )
        )

hands = dict(hands)
deck = Deck() # Reset deck
hand_lists = [card[1] for card in hands.items()]




def generate_educated_bids(hands: dict[PlayerStr, set[CardInt]]) -> dict:

    educated_bids = {}
    banned = -1
    bid_total = 0

    # Must check that all the bids do not add up to banned
    for i, bot in enumerate(bot_players):
        if i == len(bot_players) - 1:   
            banned = HAND_SIZE - bid_total

        hand_evaluator

        bid = bot.determine_ES_bid(
            hand_size=len(hands),
            table_size=len(hands[bot.name]),
            expected_scores=dict(),
            current_bids={},
            restriction=banned
        )

        educated_bids[bot.name] = bid
        bid_total += bid

    return educated_bids

# Generate root state
root_state = GameState(
    hands=dict(hands),                 # Convert tuple pairs to dict
    current_trick=current_trick,                 # (PlayerStr, CardStr)
    trump_suit=format_string("Diamonds"),             # Must be the prose
    player_order=tuple(players),
    round_scores={p: 0 for p in players},
    total_scores={p: 0 for p in players},
    cards_remaining=8                  # 8 cards each
)

hand_evaluator = HandEvaluator(
    state=root_state,  # will need to change accordingly with the updated state
    perspective=my_player,
    N_rollouts=N_ROLLOUTS
)


####

if PRINT_HANDS:
    print("PRINT HANDS")
    for lst in hand_lists:
        print(id_to_initial_list(list(lst)))

if PRINT_EXPECTED_BID:
    print("PRINT_EXPECTED+BID")
    bid_probs = hand_evaluator.generate_tricks_won_probabilities()
    ES_per_bid = bid_probs['expected_scores']
    predicted_bid = bot_players[0].determine_ES_bid(
        expected_scores=ES_per_bid,
        table_size=len(hands),
        hand_size=HAND_SIZE,
        current_bids={}

    )
    print(f"Predicted bid: {predicted_bid}, Mode: {bid_probs['mode']}")


if PRINT_NAIVE_MONTE_CARLO_ESTIMATE_MOVE:
    print("PRINT_MONTE_CARLO_ESTIMATE_MOVE")
    # Generate heuristic bid
    local_state = copy.copy(root_state)
    local_state.bids = {}
    for i, player in enumerate(bot_players):
        he = HandEvaluator(
            state=root_state,
            perspective=player.name,
            N_rollouts=N_ROLLOUTS
        )

        bid_probs = he.generate_tricks_won_probabilities(
            rollout_type=ROLLOUT_TYPE)
        ES_per_bid = bid_probs['expected_scores']

        sim = RolloutSimulator(root_state)
        initial_bids = he._bid_initialiser(simulator=sim)

        # Update local state
        local_state.bids = initial_bids

        # Predict move now
        optimal_move = player.determine_naive_move(
            current_trick=local_state.current_trick,
            trump_suit='Diamonds',
            legal_moves=local_state.get_legal_moves(player.name),
            bids = local_state.bids,
            round_score={p.name: 0 for p in bot_players}
        )


        print(id_to_initials(optimal_move)) # Works perfectly