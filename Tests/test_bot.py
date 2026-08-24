
import random
import statistics

import pytest

from bot import BotPlayer
from Classes.deck import Deck

N_ROLLOUTS = 100

@pytest.fixture
def default_bot_player() -> BotPlayer:
    return BotPlayer(name="Default") 

@pytest.fixture
def hand_size(request) -> int:
    return getattr(request, 'param', 6) # default if param not found

@pytest.fixture
def player_amount(request) -> int:
    return getattr(request, 'param', 6) 

@pytest.fixture
def default_hand(hand_size) -> set:
    return set(random.sample(range(52), k=hand_size))

@pytest.fixture
def default_bots(player_amount) -> list:
    return [BotPlayer(name=f"Default Bot {i}") for i in range(player_amount)]





class TestBotPlayer:

    @pytest.mark.parametrize('hand_size', range(6,9), indirect=True) # Dont pass it straight into the function
    def test_determine_baseline_bid_respects_restriction(self,
                                                          default_bot_player: BotPlayer,
                                                          default_hand: set[int]):

        bot = default_bot_player


        # Randomise restricted bid and ensure that it is respected
        for _ in range(N_ROLLOUTS):
            restriction = random.choice(range(-1, 8))

            bid = bot.determine_baseline_bid(
            hand=default_hand,
            trump_suit='Diamonds',
            player_amount=4,
            restriction = restriction
        )
            assert bid != restriction

    @pytest.mark.parametrize('hand_size', range(6,9))
    @pytest.mark.parametrize('player_amount', range(3,7), indirect=True)
    def test_determine_baseline_distribution_player_bias(self,
                                                         default_bots: list[BotPlayer],
                                                         hand_size: int):

        """ Random variables are player_amount and bot_hands"""

        bid_diff_frequency = {}
        player_amount = len(default_bots)
            
        # Randomise player count and ensure that the distribution of bids are similar

        # I feel like this could be its own function
        for _ in range(N_ROLLOUTS):

            # Start here for functino
            bid_total = 0
            banned= -1

            # Reset deck and cards
            deck = Deck()
            random_hands = [{deck.draw_random().id for _ in range(hand_size)}
                        for i in range(len(default_bots))]
            
            # need last players order
            for i, bot in enumerate(default_bots):

                if i == len(default_bots) - 1:
                    banned = hand_size - bid_total

                bid = bot.determine_baseline_bid(
                    hand=random_hands[i],
                    trump_suit='Diamonds',
                    player_amount = player_amount,
                    restriction = banned
                )  # Implement restricted bid logic

                assert bid in range(0, hand_size + 1)  # Bid must be within valid range

                bid_total += bid

            bid_diff = bid_total - hand_size
            if bid_diff not in bid_diff_frequency:
                bid_diff_frequency[bid_diff] = 1
            else:
                bid_diff_frequency[bid_diff] += 1
                

        # End here for function

        bid_diff_distribution = [( bid, round(freq / N_ROLLOUTS, 2)) 
                            for bid, freq in bid_diff_frequency.items()]

        # Ascending bids
        sorted_bid_distribution = sorted(
            bid_diff_distribution,
            key=lambda d: d[0]
        )

        print(sorted_bid_distribution)

        # Strip bids from distribution
        bare_distribution = [dist[1] for dist in sorted_bid_distribution]

        # Must be more than one type of bid chosen
        assert len(bare_distribution) >= 2

        # Distributions equal 1
        assert sum(bare_distribution)

        assert statistics.stdev(bare_distribution) < 1  # Not a particularly strict enforcement


    @pytest.mark.parametrize('hand_size', range(6, 9), indirect=True)
    @pytest.mark.parametrize('player_amount', range(3, 7), indirect=True)
    def test_determine_bid_returns_valid_bid(self,
        default_bot_player: BotPlayer,
        hand_size: int,
        player_amount: int
    ):
        """Bid must always be a valid bid and must respect the restriction."""

        bot = default_bot_player

        expected_scores = {
            0: 0.10,
            1: 0.25,
            2: 0.40,
            3: 0.20,
            4: 0.05,
        }

        for _ in range(N_ROLLOUTS):

            restriction = random.choice(range(-1, hand_size + 1))

            bid = bot.determine_bid(
                expected_scores=expected_scores,
                position=random.randrange(player_amount),
                table_size=player_amount,
                points_margin=random.randint(-30, 30),
                current_bids={f"Bot {i}": random.randint(0, hand_size) for i in range(
                    random.randint(0, player_amount - 1)
                )},
                hand_size=hand_size,
                restriction=restriction
            )

            assert 0 <= bid <= hand_size
            assert bid != restriction

    def test_determine_bid_prefers_best_expected_score(self,
    default_bot_player: BotPlayer):
        """Deterministic test where the bot should bid the bid with the greatest expected score"""

        for _ in range(N_ROLLOUTS):
            bot = default_bot_player

            expected_scores = {
                0: 0.10,
                1: 0.20,
                2: 0.70,
                3: 0.15,
                4: 0.05,
            }

            bid = bot.determine_bid(
                expected_scores=expected_scores,
                position=1,
                table_size=4,
                points_margin=0,
                current_bids={'Player 1':1,},
                hand_size=8,
                restriction=-1
            )

            assert bid == 2


    def test_determine_bid_high_risk_allows_variation(
    self, default_bot_player: BotPlayer):
        bot = default_bot_player
        bot.heuristics.risk_tolerance = 1.0

        expected_scores = {
            1: 0.30,
            2: 0.40,
            3: 0.30,
        }

        bids = []

        for _ in range(N_ROLLOUTS):
            bid = bot.determine_bid(
                expected_scores=expected_scores,
                position=1,
                table_size=4,
                points_margin=0,
                current_bids={},
                hand_size=8,
                restriction=-1
            )

            bids.append(bid)

        assert 1 in bids
        assert 2 in bids
        assert 3 in bids