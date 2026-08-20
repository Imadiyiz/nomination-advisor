from bot_player import BotPlayer
from Classes.DeckClass import Deck
from game_engine import GameState
from hand_evaluator import HandEvaluator
from Utils.card_tools import *
from Utils.hand_generators import *
from Utils.types import *

# Test Parameters
#players_tuple = ("strong", "weak", "suited", "random")
players_tuple = ("random1","random2","random3","random4")
players = list(players_tuple)
my_player = "random"
current_trick = ()
bot_players = [BotPlayer(name = name) for name in players_tuple]
N_rollouts = 500
deck = Deck()

# Constants
HAND_SIZE = 6

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
for lst in hand_lists:
    print(id_to_initial_list(list(lst)))

def generate_naive_bids(hands: dict[PlayerStr, set[CardInt]]) -> dict:

    naive_bids = {}
    banned = -1
    bid_total = 0

    # Must check that all the bids do not add up to banned
    for i, bot in enumerate(bot_players):
        if i == len(bot_players) - 1:   
            banned = HAND_SIZE - bid_total

        bid = bot.determine_baseline_bid(
            hand=hands[bot.name],
            trump_suit=format_string("Diamonds"),
            restriction=banned
        )

        naive_bids[bot.name] = bid
        bid_total += bid

    return naive_bids

hands = [
    (bot_player, generator(deck))
    for bot_player, generator in zip(
        players, 
        [gen for gen in hand_generators]
        )
]

# Generate root state
root_state = GameState(
    hands=dict(hands),                 # Convert tuple pairs to dict
    current_trick=current_trick,                 # (PlayerStr, CardStr)
    trump_suit=format_string("Diamonds"),             # Must be the prose
    player_order=tuple(players),
    round_scores={p: 0 for p in players},
    bids=generate_naive_bids(dict(hands)),      # Arbitrary example bids
    cards_remaining=8                  # 8 cards each
)

print(root_state.bids)