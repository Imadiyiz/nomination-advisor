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
    return Scoreboard(players=computer_players)

@pytest.fixture()
def winning_player():
    return Player(name='Winner')

@pytest.fixture()
def wc():
    Card(("Diamond", "♦"),(10, "10"))
    return Scoreboard(players=computer_players)


@pytest.fixture
def players():
    return [
        Player(name="Alice"),
        Player(name="Bob"),
        Player(name="Charlie"),
    ]


@pytest.fixture()
def scoreboard(players):
    return Scoreboard(players)

def make_player(name, bid, round_score):
    p = Player(name=name)
    p.bid = bid
    p.round_score = round_score
    return p


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

    scoreboard.update_total_scoreboard(max_cards=5)

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

@pytest.fixture()
def make_player(name, bid, round_score):
    p = Player(name=name)
    p.bid = bid
    p.round_score = round_score
    return p

def test_update_total_scoreboard_correct_bid(make_player):
    player = make_player("Alice", bid=3, round_score=3)

    scoreboard = Scoreboard()
    scoreboard.players = [player]
    scoreboard.total_scoreboard = {"Alice": 0}

    scoreboard.update_total_scoreboard(max_cards=8)

    # bid == round_score → (bid + 10)
    assert scoreboard.total_scoreboard["Alice"] == 13

def test_update_total_scoreboard_max_bid_multiplier(make_player):
    player = make_player("Bob", bid=8, round_score=8)

    scoreboard = Scoreboard()
    scoreboard.total_scoreboard = {"Bob": 0}

    scoreboard.update_total_scoreboard(max_cards=8)

    # (bid + 10) * 2 = (8 + 10) * 2 = 36
    assert scoreboard.total_scoreboard["Bob"] == 36


def test_update_total_scoreboard_incorrect_bid(make_player):
    player = make_player("Charlie", bid=4, round_score=2)

    scoreboard = Scoreboard()
    scoreboard.total_scoreboard = {"Charlie": 0}

    scoreboard.update_total_scoreboard(max_cards=8)

    # incorrect bid → add round_score only
    assert scoreboard.total_scoreboard["Charlie"] == 2


def test_update_total_scoreboard_multiple_players(make_player):
    p1 = make_player("A", bid=2, round_score=2)
    p2 = make_player("B", bid=3, round_score=1)

    scoreboard = Scoreboard([p1, p2])
    scoreboard.total_scoreboard = {
        "A": 0,
        "B": 0,
    }

    scoreboard.update_total_scoreboard(max_cards=8)

    assert scoreboard.total_scoreboard["A"] == 12  # 2 + 10
    assert scoreboard.total_scoreboard["B"] == 1

