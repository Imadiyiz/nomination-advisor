
import random
from collections import defaultdict

import pytest

from belief_model import BeliefModel
from bot import BotPlayer
from Classes.deck import Deck
from Utils.types import TrumpStr

N_ROLLOUTS = 1000
SUITS = ('Clubs', 'Diamonds', 'Hearts', 'Spades')

@pytest.fixture
def default_bot() -> BotPlayer:
    return BotPlayer(name='Default')

@pytest.fixture
def random_suit() -> TrumpStr:
    return random.choice(SUITS)

@pytest.fixture
def hand_size(request) -> int:
    return getattr(request, 'param', 6) # default if param not 

@pytest.fixture
def default_hand(hand_size) -> set:
    return set(random.sample(range(52), k=hand_size))

@pytest.fixture
def player_amount(request) -> int:
    return getattr(request, 'param', 6) 

@pytest.fixture
def default_belief_model(default_bot, hand_size, 
                         default_hand, player_amount) -> BeliefModel:
    return BeliefModel(void_suits={f'AI {i}': set() 
                                   for i in range(player_amount - 1)},
                       unknown_cards= set(range(52)) - default_hand,
                       hand_sizes={f'AI {i}' : hand_size 
                                   for i in range(player_amount - 1)},
                       perspective_player=default_bot)  # -1 prevents extra player being counted since default is not in hand sizes
                       
@pytest.fixture
def constrained_belief_model(default_bot, hand_size, 
                         default_hand, player_amount) -> BeliefModel:
    return BeliefModel(void_suits={f'AI {i}': set(random.choices(
                                    SUITS, k=2)) # Maximum two void suits for the test
                                    for i in range(player_amount - 1)},
                       unknown_cards= set(range(52)) - default_hand,
                       hand_sizes={f'AI {i}' : hand_size 
                                   for i in range(player_amount - 1)},
                       perspective_player=default_bot)  # -1 prevents extra player being counted since default is not in hand sizes

class Test_belief_model:

    @pytest.mark.parametrize('hand_size', range(6,9), indirect=True) # Dont pass it straight into the function
    @pytest.mark.parametrize('player_amount', range(3,7), indirect=True) # Dont pass it straight into the function
    def test_determine_unbiased_baseline_sampling(self, default_belief_model: BeliefModel):
        """Checks the expected proabilites of being assigned a card when there are no contraints"""
        # Sample cards randomly and check whether each card has an equal probability of being chosen

        card_counts = {player: defaultdict(int) for player in default_belief_model.hand_sizes.keys()}
        seen_cards = set()
        total_cards = sum(default_belief_model.hand_sizes.values())

        for _ in range(N_ROLLOUTS):
            assignments_sample = default_belief_model.sample_world()

            for player, assignment in assignments_sample.items():
                for card in assignment:
                    card_counts[player][card] += 1
                    seen_cards.add(card)

            assert len(seen_cards) == total_cards, (
                    f"Seen cards {len(seen_cards)} is not equal to total cards {total_cards}")  # Checks no duplicates are found

            seen_cards = set()  # Reset

        for player, counts in card_counts.items():

            # Calculate expected probabilities based on hand size and player amount
            expected_probability = default_belief_model.hand_sizes[player] / total_cards
            standard_error = (expected_probability * (1 - expected_probability) ** 0.5)  # SE = (P * (1-P)**0.5)
            for card, freq in counts.items():
                observed_probability = round(freq / N_ROLLOUTS, 2)
                assert abs(expected_probability - observed_probability) < 3 * standard_error, ( 
                f"{player} holds {card} with p={observed_probability:.3f}, "
                f"expected {expected_probability:.3f}" )

    @pytest.mark.parametrize('hand_size', range(6,9), indirect=True) # Dont pass it straight into the function
    @pytest.mark.parametrize('player_amount', range(3,7), indirect=True)
    def test_determine_unbiased_constrained_sampling(self, constrained_belief_model: BeliefModel):
        """Checks the expected proabilites of being assigned a card when there are no contraints"""
        # Sample cards randomly and check whether each card has an equal probability of being chosen

        card_counts = {player: defaultdict(int) for player in constrained_belief_model.hand_sizes.keys()}
        seen_cards = set()
        total_cards = sum(constrained_belief_model.hand_sizes.values())
        print(constrained_belief_model.void_suits.items(), "OUTPUTt")

        for _ in range(N_ROLLOUTS):
            assignments_sample = constrained_belief_model.sample_world()

            for player, assignment in assignments_sample.items():
                for card in assignment:
                    card_counts[player][card] += 1
                    seen_cards.add(card)

            assert len(seen_cards) == total_cards  # Checks no duplicates are found
            seen_cards = set()  # Reset

        for player, counts in card_counts.items():

            # Calculate expected probabilities based on hand size and player amount
            expected_probability = constrained_belief_model.hand_sizes[player] / total_cards
            standard_error = (expected_probability * (1 - expected_probability) ** 0.5)  # SE = (P * (1-P)**0.5)
            for card, freq in counts.items():
                observed_probability = round(freq / N_ROLLOUTS, 2)
                assert abs(expected_probability - observed_probability) < 3 * standard_error, ( 
                f"{player} holds {card} with p={observed_probability:.3f}, "
                f"expected {expected_probability:.3f}" )

        

        
