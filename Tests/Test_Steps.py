import pytest
from Classes.StepClass import *
from Classes.PlayerClass import Player
from unittest.mock import MagicMock
from Classes.GameManager import *
from Classes.CardClass import Card
from Classes.DeckClass import Deck

@pytest.fixture
def player():
    p = Player(name="Alice")
    p.hand = ["2C", "4C", "AC"]  # minimal stub
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
    return Scoreboard(player_list=player_queue)

@pytest.fixture()
def vci():
    return Deck().generate_valid_card_initials()

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
        step = BiddingStep()
        args = {"forbidden_bid": 2}
        assert step.validate("3", args) == 3

    def test_bidding_forbidden(self):
        step = BiddingStep()
        args = {"forbidden_bid": 2}
        with pytest.raises(ValueError):
            step.validate("2", args)

    def test_bidding_missing_args(self):
        step = BiddingStep()
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
        assert step.validate("1", args) == "1"

    def test_player_play_card_out_of_range(self, player):
        step = PlayerPlayCardStep()
        args = {"player": player}
        with pytest.raises(ValueError):
            step.validate("5", args)


class TestOpponentPlaysCard():
    def test_opponent_plays_card(self, tb, sb, vci):
        
        opponent = Player(name="CPU", opponent=True)

        playing_flow = PlayingFlow(
            table=tb,
            scoreboard=sb,
            valid_card_initials=vci
        )

        # mock input loop if needed
        result = playing_flow._prompt_for_opponent_play_card(
            player=opponent,
            trump_suit="Spades"
        )

        assert isinstance(result, str)
        assert result in vci or (result == 'BACK')
