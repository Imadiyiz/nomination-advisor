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
    assert gm.phase == Phase.HAND_ASSIGNMENT

def test_materialise_played_card_assigns_owner():
    game = Game()
    game.deck = MagicMock()

    player = Player(name="Remote", opponent=True)
    card = Card(suit="Hearts", value="A")

    game.deck.get_card_from_initials.return_value = card

    result = game._materialise_played_card(player, "AH")

    assert result is card
    assert card.owner == player
    game.deck.get_card_from_initials.assert_called_once_with("AH")


def test_materialise_played_card_raises_if_missing():
    game = Game()
    game.deck = MagicMock()
    game.deck.get_card_from_initials.return_value = None

    player = Player(name="Remote", opponent=True)

    with pytest.raises(ValueError):
        game._materialise_played_card(player, "ZZ")

def test_local_play_card_removes_card_from_hand():
    game = Game()
    game.table = MagicMock()

    player = Player(name="Local", opponent=False)
    card = Card(suit="Spades", value="K")
    player.hand = [card]

    game._local_play_card(player, card)

    game.table.play_card_to_table.assert_called_once_with(card, player)
    assert card not in player.hand
    assert game.table.stack

def test_remote_play_card_removes_card_from_deck():
    game = Game()
    game.deck = MagicMock()
    game.table = MagicMock()

    player = Player(name="Remote", opponent=True)
    card = Card(suit="Diamonds", value="10")
    card.owner = player

    game._remote_play_card(player, card)

    game.deck.remove_card.assert_called_once_with(card)
    game.table.play_card_to_table.assert_called_once_with(card, player)
