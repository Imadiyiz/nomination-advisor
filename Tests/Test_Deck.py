from Classes.CardClass import Card
from Classes.PlayerClass import Player
from Classes.ScoreboardClass import Scoreboard
from Classes.DeckClass import Deck
import pytest


class Test_Scoreboard():

    def test_scoreboard_init(self):
        
        self.deck = Deck()
        assert self.deck.generate_valid_card_initials()

    def test_card_initial_lookup(self):
        self.deck = Deck()
        self.deck.generate_deck()

        assert str(self.deck.draw_card_from_initials("10D")) == "10 ♦"
        assert str(self.deck.draw_card_from_initials("AD")) == "A ♦"
        assert str(self.deck.draw_card_from_initials("JD")) == "J ♦"
        assert str(self.deck.draw_card_from_initials("2S")) == "2 ♠"

    def test_card_initals_length_match(self):
        self.deck = Deck()
        deck = self.deck.generate_deck()
        assert len(deck) == len(self.deck.generate_valid_card_initials())
        

        
