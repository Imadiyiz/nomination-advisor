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
deck = Deck()
my_player = players_tuple[0]

# Constants
HAND_SIZE = 8
N_ROLLOUTS = 100

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

def generate_educated_bids(hands: dict[PlayerStr, set[CardInt]]) -> dict:

    educated_bids = {}
    banned = -1
    bid_total = 0




    # Must check that all the bids do not add up to banned
    for i, bot in enumerate(bot_players):
        if i == len(bot_players) - 1:   
            banned = HAND_SIZE - bid_total

        bid = bot.determine_baseline_bid(
            hand=hands[bot.name],
            trump_suit=format_string("Diamonds"),
            player_amount=len(hands),
            restriction=banned
        )

        educated_bids[bot.name] = bid
        bid_total += bid

    return educated_bids

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
    total_scores={p: 0 for p in players},
    cards_remaining=8                  # 8 cards each
)

hand_evaluator = HandEvaluator(
    state=root_state,  # will need to change accordingly with the updated state
    perspective=my_player,
    N_rollouts=N_ROLLOUTS
)

bid_probs = hand_evaluator.generate_bid_probabilities()
ES_per_bid = bid_probs['expected_scores']
predicted_bid = bot_players[0].determine_bid(
    expected_scores=ES_per_bid,
    position=0,
    table_size=len(hands),
    hand_size=HAND_SIZE,
    points_margin=0,
    current_bids=[] # Naive to use a list as you won't know if the leader is before you

)
print(f"Predicted bid: {predicted_bid}, Mode: {bid_probs['mode']}")