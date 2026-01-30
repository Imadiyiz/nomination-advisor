# Contents of the PlayerState test python file


from Classes.PlayerClass import Player
from Classes.PlayerStateManager import PlayerStateManager
import pytest
import random

    
@pytest.fixture 
def players():
    players_list = []
    for i in range(5):
        players_list.append(Player(name = f"{i+1}"))
    return players_list

@pytest.fixture
def ps(players):
    return PlayerStateManager(players)

class Test_PlayerState():
    """
    Tests the functions in the PlayerStateManager class
    """
    def test_add_score(self, ps):
        _player = random.choice(list(ps.players))
        ps.add_score(_player, points = 8)
        assert _player.total_score == 8

    @pytest.mark.parametrize(
            "player_queue, expected_order, winner",

            [
                (
                    [
                        Player(name="1"),
                        Player(name="2"),
                        Player(name="3"),
                        Player(name="4"),
                        Player(name="5"),
                    ], 

                    [
                        Player(name="5"),
                        Player(name="1"),
                        Player(name="2"),
                        Player(name="3"),
                        Player(name="4"),
                    ], # winner is player 5
                    Player(name="5")
                    
                ), 

                (
                    [
                        Player(name="1"),
                        Player(name="2"),
                        Player(name="3"),
                        Player(name="4"),
                        Player(name="5"),
                    ], 

                    [   
                        Player(name="2"),
                        Player(name="3"),
                        Player(name="4"),
                        Player(name="5"),
                        Player(name="1"),
                        
                    ], # winner is player 2
                    Player(name="2")
                ),

                (   

                    [
                        Player(name="1"),
                        Player(name="2"),
                        Player(name="3"),
                        Player(name="4"),
                        Player(name="5"),
                    
                    ],

                    [
                        Player(name="1"),
                        Player(name="2"),
                        Player(name="3"),
                        Player(name="4"),
                        Player(name="5"),
                    
                    ],
                     Player(name="1") # Player 1 wins so order stays the same
                )

            ]

    )

    def test_update_winning_order(self, ps,
                                player_queue, expected_order, winner):
        """
        Determines whether the order is correctly changed should a player win the hand
        """
        
        test_player_queue = ps.update_winner_order(winner=winner, player_queue=player_queue)
        assert test_player_queue == expected_order


    @pytest.mark.parametrize(
            "player_queue, expected_order",

            [
                (
                    [
                        
                        Player(name="4"),
                        Player(name="5"),
                        Player(name="1"),
                        Player(name="2"),
                        Player(name="3"),
                    ], 

                    [
                        Player(name="5"),
                        Player(name="1"),
                        Player(name="2"),
                        Player(name="3"),
                        Player(name="4"),

                    ], # dealer is player 5
                    
                ), 

                (
                    [
                        Player(name="1"),
                        Player(name="2"),
                        Player(name="3"),
                        Player(name="4"),
                        Player(name="5"),
                    ], 

                    [   
                        Player(name="2"),
                        Player(name="3"),
                        Player(name="4"),
                        Player(name="5"),
                        Player(name="1"),
                        
                    ], # dealer is player 2
                ),

                (   

                    [
                        Player(name="3"),
                        Player(name="4"),
                        Player(name="5"),
                        Player(name="1"),
                        Player(name="2"),
                    
                    ], 

                    [
                        Player(name="4"),
                        Player(name="5"),
                        Player(name="1"),
                        Player(name="2"),
                        Player(name="3"),
                    
                    ], #dealer is player 4
                )

            ]

    )

    def test_update_dealer_order(self,ps, player_queue, expected_order):
        """
        Determines whether the dealer shifts one position every round
        """

        order = ps.update_dealer_order(player_queue)
        assert order == expected_order

