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
ROLLOUT_TYPE = 'RANDOM'


# PRINT FLAGS

PRINT_EXPECTED_BID = False
PRINT_HANDS = True
PRINT_MONTE_CARLO_ESTIMATE_MOVE = True
PRINT_BOT_ESTIMATE_MOVE = False
PRINT_GAME_SIMULATION = True


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
    local_state = copy.deepcopy(root_state)
    bid_probs = hand_evaluator._calculate_tricks_won_probabilities()
    ES_per_bid = bid_probs['raw_expected_scores']
    predicted_bid = bot_players[0].determine_ES_bid(
        hand=local_state.hands[bot_players[0].name],
        expected_scores=ES_per_bid,
        table_size=len(hands),
        current_bids={}

    )
    print(f"Predicted bid: {predicted_bid}, Mode: {bid_probs['mode']}")


if PRINT_BOT_ESTIMATE_MOVE:
    print("PRINT_MONTE_CARLO_ESTIMATE_MOVE")
    # Generate heuristic bid
    local_state = copy.deepcopy(root_state)
    print(local_state)
    print(local_state.bids)
    print(local_state.player_order)

    local_state.bids = {}
    for i, player in enumerate(bot_players):
        # Changes evaluator based on player
        he = HandEvaluator(
            state=local_state,
            perspective=player.name,
            N_rollouts=N_ROLLOUTS
        )

        bid_probs = he._calculate_tricks_won_probabilities(
            rollout_type=ROLLOUT_TYPE)
        ES_per_bid = bid_probs['raw_expected_scores']

        sim = RolloutSimulator(root_state)
        initial_bids = he._strong_card_bid_initialiser(simulator=sim)

        # bids can not equal total tricks
        assert sum(initial_bids.values()) != HAND_SIZE  # Need to put this in a test

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

        print(id_to_initials(optimal_move)) # Works perfectly with RANDOM
        print("Bid:", local_state.bids[player.name])


if PRINT_MONTE_CARLO_ESTIMATE_MOVE:
    print("PRINT_MONTE_CARLO_ESTIMATE_MOVE")
    # Generate heuristic bid
    local_state = copy.deepcopy(root_state)
    local_state.bids = {}

    for i, player in enumerate(bot_players):


        # Have to iterate order to simulate a round and ensure players comply with restraints
        # e.g a player in second position should not be able to play first
        local_state.player_order = tuple(
        root_state.player_order[i:] + 
                 root_state.player_order[:i])

        # Changes evaluator based on player
        he = HandEvaluator(
            state=root_state,
            perspective=player.name,
            N_rollouts=N_ROLLOUTS
        )

        bid_probs = he._calculate_tricks_won_probabilities(
            rollout_type=ROLLOUT_TYPE)
        ES_per_bid = bid_probs['raw_expected_scores']

        sim = RolloutSimulator(root_state)
        initial_bids = he._strong_card_bid_initialiser(simulator=sim)

        # bids can not equal total tricks
        assert sum(initial_bids.values()) != HAND_SIZE  # Need to put this in a test

        # Update local state
        local_state.bids = initial_bids
        print("Initial Bid", initial_bids)
        he.state = local_state  # Update state
        optimal_move = he.estimate_optimal_move()['optimal_move']

        print(id_to_initials(optimal_move))  # It works, its just corrupted because it expects the order of the tuple to be correct
        # It isn't going to work as the second player in the iteration uses a root state where they shouldn't be going first
        # I could edit the tuple to prove im right
        # I was right
    