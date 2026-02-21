# Contents of the Test_TrumpManager.py file

from Classes.TrumpManager import TrumpManager
from Classes.UIManager import UIManager
import pytest
from Classes.PlayerClass import Player
import random

@pytest.fixture
def computer_player_set():
    players = list()
    for i in range(5):
        players.append(Player(name=f"Player{i}"))
    return players

@pytest.fixture
def human_player():
    return Player(name=f"Human", round_score=5, computer = False)

@pytest.fixture
def trump_manager():
    ui = UIManager()
    return TrumpManager(UIManager=ui)

class Test_Decide_Trump():
    
    def test_player_can_choose_trump(self, monkeypatch, computer_player_set, 
                            trump_manager,
                            human_player):
        
        players = computer_player_set
        players.append(human_player)

        # Monkeypatch random.choice to always return the human
        monkeypatch.setattr(random, "choice", lambda x: human_player)

        monkeypatch.setattr(trump_manager.UIManager, "get_player_input", lambda msg: 'D')

        # Monkeypatch UIManager.display_message to suppress output
        monkeypatch.setattr(trump_manager.UIManager, "display_message", lambda msg: None)

        initial_trump = 'spade'
        new_trump = trump_manager.decide_trump(
            players=players,
        )
       
        assert new_trump == 'diamond'
        #if all players are computers then pass the test
    
    
