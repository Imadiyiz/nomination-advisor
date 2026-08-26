
import random

import pytest

from bot import BotPlayer
from Classes.deck import Deck
from game_engine import GameState
from Utils.types import *


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
    return [BotPlayer(name=f"BOT{i}") for i in range(player_amount)]

@pytest.fixture
def root_state(default_bots):
    return GameState(
        hands={db.name: set() for db in default_bots},                
        current_trick=(),      
        trump_suit="Diamonds", 
        player_order=tuple(bot.name for bot in default_bots),
        round_scores={p: 0 for p in default_bots},
        total_scores={p: 0 for p in default_bots},
    )



class TestGameState:
    """"Test functionality of GameState class, as it should be responsible for storing
    the state of the core game, and can be duplicated to create new worlds."""


    def test_valid_get_leader(self, root_state):
        """Ensures that the leader returned is the correct leader. Imperative
        for keeping order of the player order tuple"""

        print(root_state._leader)
        assert root_state._leader is None
        assert root_state._get_leader() == root_state.player_order[0]

        # Reset player order for new test
        root_state.player_order = ('BOT', 'BOT1', 'BOT2')
        root_state.current_trick = (('BOT', 41), )
        assert root_state._get_leader() == 'BOT'

    def test_next_player(self, root_state: GameState):
        """Ensures that the next player can correctly be determined. Essential for
        an ordering system using tuples."""

        assert root_state._leader is None
        assert len(root_state.current_trick) == 0
        assert root_state.next_player() == root_state.player_order[0]


        root_state._leader = None
        root_state.current_trick = (('BOT0', 41), )
        assert len(root_state.current_trick) == 1
        assert root_state.next_player() == root_state.player_order[1]

        root_state.current_trick = (('BOT0', 41), ('BOT1', 43) )
        assert root_state.next_player() == root_state.player_order[2]

        # Make player count 3 to verify wrap around logic
        root_state.player_order = root_state.player_order[:3]
        assert len(root_state.player_order) == 3

        root_state.current_trick = (('BOT0', 41), ('BOT1', 43), ('BOT2', 30),  )
        assert root_state.next_player() == root_state.player_order[0]



