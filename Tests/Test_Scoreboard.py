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
