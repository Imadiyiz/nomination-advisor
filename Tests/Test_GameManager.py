import pytest
from unittest.mock import MagicMock

from Classes.GameManager import *
from Classes.GameManager import Game


@pytest.fixture
def gm():
    gm = Game.__new__(Game)  # bypass __init__

    gm.player_queue = []
    gm.phase = None

    gm.playerSetupFlow = MagicMock()

    gm.playerSetupFlow.run.return_value = {
        "player_names": [
            {"name": "Alice", "opponent": False},
            {"name": "Bob", "opponent": True},
            {"name": "Alice", "opponent": False},  # duplicate
        ]
    }

    gm.playerSetupFlow.remove_duplicates.return_value = [
        "Alice",
        "Bob"
    ]

    return gm



def test_handle_player_selection_creates_players_and_sets_phase(gm):
    gm.handle_player_selection()

    # 1. Correct number of players
    assert len(gm.player_queue) == 2

    # 2. Players are Player instances
    assert all(isinstance(p, Player) for p in gm.player_queue)

    # 3. Names are correct
    assert gm.player_queue[0].name == "Alice"
    assert gm.player_queue[1].name == "Bob"

    # 4. Opponent flags preserved in order
    assert gm.player_queue[0].opponent is False
    assert gm.player_queue[1].opponent is True

    # 5. Phase transition happened
    assert gm.phase == Phase.TRUMP_SELECTION
