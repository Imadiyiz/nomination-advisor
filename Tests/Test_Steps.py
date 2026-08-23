import pytest

from Classes.deck import Deck
from Classes.game_manager import *
from Classes.player import Player
from Classes.step import *


@pytest.fixture
def player():
    p = Player(name="Alice")
    p.hand = [4, 44, 10]  # minimal stub
    p.opponent = False
    return p

@pytest.fixture
def player_queue(player):
    player_queue = [player for i in range(4)]
    return player_queue

@pytest.fixture
def ui():
    return UIManager()

@pytest.fixture
def tb(ui):
    return Table(ui)

@pytest.fixture()
def sb(player_queue):
    return Scoreboard(players=player_queue)


class Test_NumPlayerStep():

    def test_num_player_valid(self):
        step = NumPlayerStep()
        assert step.validate("4") == 4

    def test_num_player_invalid_range(self):
        step = NumPlayerStep()
        with pytest.raises(ValueError):
            step.validate("2")

    def test_num_player_not_digit(self):
        step = NumPlayerStep()
        with pytest.raises(ValueError):
            step.validate("abc")

    def test_num_player_back(self):
        step = NumPlayerStep()
        assert step.validate("b") == "BACK"

class Test_PlayerNameStep():

    def test_player_name_valid(self):
        step = PlayerNameStep()
        assert step.validate("Alice") == "Alice"

    def test_player_name_invalid_chars(self):
        step = PlayerNameStep()
        with pytest.raises(ValueError):
            step.validate("Al1ce")

    def test_player_name_too_short(self):
        step = PlayerNameStep()
        with pytest.raises(ValueError):
            step.validate("A")

    def test_player_name_back(self):
        step = PlayerNameStep()
        assert step.validate("b") == "BACK"

class OpponentBooleanStep():
    def test_opponent_boolean_yes(self):
        step = OpponentBooleanStep()
        assert step.validate("y") == ""

    def test_opponent_boolean_no(self):
        step = OpponentBooleanStep()
        assert step.validate("n") == ""

    def test_opponent_boolean_invalid(self):
        step = OpponentBooleanStep()
        with pytest.raises(ValueError):
            step.validate("x")

class Test_BiddingStep():
    def test_bidding_valid(self):
        step = BiddingMenuStep()
        args = {"forbidden_bid": 2}
        assert step.validate("3", args) == 3

    def test_bidding_forbidden(self):
        step = BiddingMenuStep()
        args = {"forbidden_bid": 2}
        with pytest.raises(ValueError):
            step.validate("2", args)

    def test_bidding_missing_args(self):
        step = BiddingMenuStep()
        with pytest.raises(RuntimeError):
            step.validate("3", {})

class Test_TrumpSelectionStep():
    def test_trump_selection_yes(self):
        step = TrumpSelectionStep()
        assert step.validate("y", {}) == "y"

    def test_trump_selection_invalid(self):
        step = TrumpSelectionStep()
        with pytest.raises(ValueError):
            step.validate( "x", {})

class Test_ManualTrumpStep():
    def test_manual_trump_valid(self):
        step = ManualTrumpStep()
        args = {"valid_card_initials": {"10D", "KS"}}
        assert step.validate("10D", args) == "10D"

    def test_manual_trump_invalid_card(self):
        step = ManualTrumpStep()
        args = {"valid_card_initials": {"10D"}}
        with pytest.raises(ValueError):
            step.validate("9H", args)


class Test_PlayerPlayCardStep():

    def test_player_play_card_valid(self, player):
        step = PlayerPlayCardStep()
        args = {"player": player}
        assert step.validate("1", args) == 1

    def test_player_play_card_out_of_range(self, player):
        step = PlayerPlayCardStep()
        args = {"player": player}
        with pytest.raises(ValueError):
            step.validate("5", args)


