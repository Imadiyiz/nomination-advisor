from Classes.CardClass import Card
from Classes.PlayerClass import Player
from Classes.ScoreboardClass import Scoreboard
from Classes.DeckClass import Deck
import pytest


class Test_Scoreboard():

    def test_scoreboard_init(self):
        
        self.deck = Deck()
        assert self.deck.generate_valid_card_initials()
        
