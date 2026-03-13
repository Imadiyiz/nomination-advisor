



import pytest
from Classes.CardClass import Card
from game_engine import GameState, SimulationState  # adjust import


@pytest.fixture
def base_state():
    """
    Creates a minimal valid GameState for testing get_legal_moves
    """

    state = GameState(
        hands={},
        played_cards={},
        current_trick=["9H"],  # first card sets lead suit
        leader="P1",
        trump_suit="S",
        player_order=["P1", "P2", "P3", "P4"],
        bids={"P1": 0},
        cards_remaining=4,
    )

    return state

@pytest.fixture
def sim_state(base_state):

    base_state.current_trick = ["9H", "10C", "AC", "9C"]
    state = SimulationState(base_state)

    return state


def test_follow_suit_required(base_state):
    """
    Player must follow suit if possible.
    Lead suit = Hearts.
    Hearts in unknown_cards = 10H, 2H
    """
    moves = base_state.get_legal_moves("P1", base_state)

    assert "10H" in moves
    assert "2H" in moves
    assert "KD" not in moves


def test_trump_always_allowed(base_state):
    """
    Trump suit = Spades.
    AS should always be legal.
    """
    moves = base_state.get_legal_moves("P1", base_state)

    assert "AS" in moves


def test_valid_winning_player(sim_state):

    """
    Determines whether the correct player is selected
    """

    assert sim_state._verify_winner() == 'P1'
