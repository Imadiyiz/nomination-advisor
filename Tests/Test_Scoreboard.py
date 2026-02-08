from Classes.CardClass import Card
from Classes.PlayerClass import Player
from Classes.ScoreboardClass import Scoreboard
import pytest


@pytest.fixture()
def computer_players():
    player_list = [Player(name=f"Player{i}") for i in range(5)]
    return player_list

@pytest.fixture()
def sb(computer_players):
    return Scoreboard(player_list=computer_players)

@pytest.fixture()
def winning_player():
    return Player(name='Winner')

@pytest.fixture()
def wc():
    Card(("Diamond", "♦"),(10, "10"))
    return Scoreboard(player_list=computer_players)


@pytest.fixture
def players():
    return [
        Player(name="Alice"),
        Player(name="Bob"),
        Player(name="Charlie"),
    ]


@pytest.fixture
def scoreboard(players):
    return Scoreboard(players)

class Test_Scoreboard():

    def test_scoreboard_init(self, computer_players, sb):
        
        #all players are added to scoreboards
        assert len(sb.round_scoreboard) == 5
        assert len(sb.total_scoreboard) == 5

        #values are 0
        for value in sb.round_scoreboard.values():
            assert value == 0 

        #values are 0
        for value in sb.total_scoreboard.values():
            assert value == 0 

    def test_update_round_scoreboard(self, sb, computer_players):

        computer_players[0]

def test_scoreboard_initialisation(scoreboard, players):
    for player in players:
        assert scoreboard.round_scoreboard[player.name] == 0
        assert scoreboard.total_scoreboard[player.name] == 0

def test_display_round_scoreboard_sorted(scoreboard):
    scoreboard.round_scoreboard["Alice"] = 1
    scoreboard.round_scoreboard["Bob"] = 3
    scoreboard.round_scoreboard["Charlie"] = 2

    result = scoreboard.display(round=True)

    assert result == 'Bob 3 | Charlie 2 | Alice 1'


def test_display_total_scoreboard(scoreboard):
    scoreboard.total_scoreboard["Alice"] = 5
    scoreboard.total_scoreboard["Bob"] = 15

    result = scoreboard.display(round=False)

    assert result[0] == ("Bob", 15)

def test_update_round_scoreboard_increments_winner(players, scoreboard):
    winner = players[1]
    card = Card(suit="Hearts", value="A")
    card.owner = winner

    scoreboard.update_round_scoreboard(players, card)

    assert winner.round_score == 1
    assert scoreboard.round_scoreboard[winner.name] == 1

def test_update_total_scoreboard_correct_bid(players, scoreboard):
    player = players[0]
    player.bid = 2
    player.round_score = 2

    scoreboard.update_total_scoreboard(players, max_cards=5)

    assert scoreboard.total_scoreboard[player.name] == 12  # 2 + 10

def test_update_total_scoreboard_correct_bid_max_cards(players, scoreboard):
    player = players[0]
    player.bid = 5
    player.round_score = 5

    scoreboard.update_total_scoreboard(players, max_cards=5)

    assert scoreboard.total_scoreboard[player.name] == 30  # (5 + 10) * 2

def test_update_total_scoreboard_incorrect_bid(players, scoreboard):
    player = players[0]
    player.bid = 3
    player.round_score = 1

    scoreboard.update_total_scoreboard(players)

    assert scoreboard.total_scoreboard[player.name] == 1

def test_reorder_round_scoreboard(players, scoreboard):
    players[0].round_score = 2
    players[1].round_score = 1
    players[2].round_score = 3

    scoreboard.reorder_round_scoreboard(players)

    assert list(scoreboard.round_scoreboard.keys()) == [
        "Alice",
        "Bob",
        "Charlie",
    ]
    assert scoreboard.round_scoreboard["Charlie"] == 3
