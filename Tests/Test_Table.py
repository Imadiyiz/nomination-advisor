from Classes.CardClass import Card
from Classes.TableClass import Table
import pytest
from Classes.UIManager import UIManager

@pytest.fixture
def ui():
    return UIManager()

@pytest.fixture
def tb(ui):
    return Table(ui)

@pytest.fixture
def c():
    return Card(suit=("Diamond", "♦"), value=("10", 10))


class Test_Table():

    def test_add_to_stack(self, tb, c):
        tb.add_to_stack(card = c)
        assert c in tb.stack

    @pytest.mark.parametrize(
    "cards, trump_suit, expected_winning_card",
    [
        (
            [
                Card(suit=("Diamond", "♦"), value=("10", 10)),
                Card(suit=("Heart", "♥"), value=("3", 3)),
                Card(suit=("Club", "♣"), value=("10", 10)),
                Card(suit=("Heart", "♥"), value=("10", 10)),
            ],
            'Spade',
            Card(suit=("Diamond", "♦"), value=("10", 10))
        ),
        (
            [
                Card(suit=("Diamond", "♦"), value=("10", 10)),
                Card(suit=("Diamond", "♦"), value=("5", 5)),
                Card(suit=("Diamond", "♦"), value=("2", 2)),
                Card(suit=("Diamond", "♦"), value=("4", 4)),
            ],
            'Diamond',
            Card(suit=("Diamond", "♦"), value=("10", 10))
        ),
        (
            [
                Card(suit=("Diamond", "♦"), value=("10", 10)),
                Card(suit=("Spade", "♠"), value=("10", 10)),
                Card(suit=("Club", "♣"), value=("10", 10)),
                Card(suit=("Heart", "♥"), value=("10", 10)),
            ],
            'Heart',
            Card(suit=("Heart", "♥"), value=("10", 10))
        ),
        (
            [
                Card(suit=("Diamond", "♦"), value=("Ace", 14)),
                Card(suit=("Spade", "♠"), value=("10", 10)),
                Card(suit=("Club", "♣"), value=("10", 10)),
                Card(suit=("Heart", "♥"), value=("10", 10)),
            ],
            'Diamond',
            Card(suit=("Diamond", "♦"), value=("Ace", 14))
        ),

        (
            [
                Card(suit=("Club", "♣"), value=("Ace", 14)),
                Card(suit=("Spade", "♠"), value=("10", 10)),
                Card(suit=("Club", "♣"), value=("5", 5)),
                Card(suit=("Heart", "♥"), value=("10", 10)),
            ],
            'Diamond',
            Card(suit=("Club", "♣"), value=("Ace", 14))
        ),

        (
            [
                Card(suit=("Club", "♣"), value=("5", 5)),
                Card(suit=("Spade", "♠"), value=("10", 10)),
                Card(suit=("Club", "♣"), value=("Ace", 14)),
                Card(suit=("Heart", "♥"), value=("10", 10)),
            ],
            'Diamond',
            Card(suit=("Club", "♣"), value=("Ace", 14))
        ),
        (
            [],
            'Heart',
            None
        )
    ]
)

    def test_verify_winner(self, tb, cards, 
                            trump_suit, expected_winning_card):
        tb.stack = cards
        winning_card = tb.verify_winner(trump_suit = trump_suit)
        assert expected_winning_card == winning_card


    @pytest.mark.parametrize(
            "stack, card, player_hand, expected_bool", 

            [
                (
                    [
                        Card(suit=("Diamond", "♦"), value=("8", 8)),
                        Card(suit=("Heart", "♥"), value=("7", 7)),
                        Card(suit=("Club", "♣"), value=("Jack", 11)),
                        Card(suit=("Heart", "♥"), value=("Queen", 12)),
                    ],
                        Card(suit=("Heart", "♥"), value=("3", 3)),
                    [

                        Card(suit=("Diamond", "♦"), value=("10", 10)),
                        Card(suit=("Heart", "♥"), value=("3", 3)),
                        Card(suit=("Club", "♣"), value=("10", 10)),
                        Card(suit=("Heart", "♥"), value=("10", 10)),
                        Card(suit=("Diamond", "♦"), value=("5", 5)),
                        Card(suit=("Heart", "♥"), value=("2", 2)),
                        Card(suit=("Club", "♣"), value=("Ace", 14)),
                        Card(suit=("Heart", "♥"), value=("King", 13)),

                    ],
                        False # Must play a diamond, diamond led
                ),

                (
                    [
                        Card(suit=("Diamond", "♦"), value=("10", 10)),
                        Card(suit=("Diamond", "♦"), value=("3", 3)),
                        Card(suit=("Diamond", "♦"), value=("9", 9)),
                        Card(suit=("Diamond", "♦"), value=("5", 5)),
                    ],
                        Card(suit=("Heart", "♥"), value=("10", 10)),
                    [

                        Card(suit=("Heart", "♥"), value=("8", 8)),
                        Card(suit=("Heart", "♥"), value=("3", 3)),
                        Card(suit=("Club", "♣"), value=("10", 10)),
                        Card(suit=("Heart", "♥"), value=("10", 10)),
                        Card(suit=("Heart", "♥"), value=("Jack", 11)),
                        Card(suit=("Heart", "♥"), value=("2", 2)),
                        Card(suit=("Club", "♣"), value=("Ace", 14)),
                        Card(suit=("Heart", "♥"), value=("King", 13)),

                    ],
                        True # Can play a heart, no diamond in hand
                ),

                (
                    [
                        Card(suit=("Diamond", "♦"), value=("Ace", 14)),
                        Card(suit=("Heart", "♥"), value=("3", 3)),
                        Card(suit=("Club", "♣"), value=("10", 10)),
                        Card(suit=("Heart", "♥"), value=("10", 10)),
                    ],
                        Card(suit=("Diamond", "♦"), value=("Jack", 11)), 

                    [   
                        Card(suit=("Diamond", "♦"), value=("Jack", 11)),
                        Card(suit=("Heart", "♥"), value=("8", 8)),
                        Card(suit=("Heart", "♥"), value=("5", 5)),
                        Card(suit=("Club", "♣"), value=("10", 10)),
                        Card(suit=("Heart", "♥"), value=("4", 4)),
                        Card(suit=("Heart", "♥"), value=("Jack", 11)),
                        Card(suit=("Heart", "♥"), value=("2", 2)),
                        Card(suit=("Club", "♣"), value=("Ace", 14)),
                        Card(suit=("Heart", "♥"), value=("King", 13))
                    
                    ],
            
                        True # Can play a diamond, it was first
                ),

                (
                    [],
                        Card(suit=("Diamond", "♦"), value=("Jack", 11)), 

                    [   
                        Card(suit=("Diamond", "♦"), value=("Jack", 11)),
                        Card(suit=("Heart", "♥"), value=("8", 8)),
                        Card(suit=("Heart", "♥"), value=("5", 5)),
                        Card(suit=("Club", "♣"), value=("10", 10)),
                        Card(suit=("Heart", "♥"), value=("4", 4)),
                        Card(suit=("Heart", "♥"), value=("Jack", 11)),
                        Card(suit=("Heart", "♥"), value=("2", 2)),
                        Card(suit=("Club", "♣"), value=("Ace", 14)),
                        Card(suit=("Heart", "♥"), value=("King", 13))
                    
                    ],
            
                        True # Empty stack so anything can be played
                ),
            
            ]
    )

    def test_valid_add_to_stack(self, tb, stack,
                                card, player_hand, expected_bool ):
        
        tb.stack = stack
        valid = tb.valid_add_to_stack(card=card, player_hand = player_hand)

        assert valid == expected_bool

    def test_reset_table(self, tb, c):
        
        tb.stack = [c]
        tb.reset()
        assert not tb.stack