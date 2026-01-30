
from Classes.PlayerClass import Player
import pytest
from Classes.UIManager import UIManager
from Classes.BiddingManager import BiddingManager
import random

@pytest.fixture
def computer_players():
    players = []
    for i in range(5):
        players.append(Player(name=f"Player{i}"))
    return players

@pytest.fixture
def bm():
    return BiddingManager(UIManager())

@pytest.fixture
def human_player():
    return Player(name="Human") 
    
class TestBiddingManager():
    
    """
    def test_successful_computer_bid(self, bm, computer_players):

        #Not allowed works
        computer_players[-1].handicapped = True
        for player in computer_players:
            bm.computer_bid(player=player,player_queue = computer_players, max_cards = 8)

        for player in computer_players:
            assert player.bid > -1
        
    """

    def test_successful_player_bid(self, bm, human_player):

        #no handicap
        assert bm.successful_player_bid(human_player, forbidden_bid=2, bid_amount=2) # not handicapped
        assert human_player.bid == 2

        #handicap
        human_player.handicapped_bid = True
        human_player.bid = -1

        #Invalid bid: bid equals not allowed
        assert not bm.successful_player_bid(human_player, forbidden_bid=2, bid_amount=2)  # handicapped
        assert human_player.bid != 2

        #Invalid bid: bid is too high
        assert not bm.successful_player_bid(human_player, forbidden_bid=3, bid_amount=10) 
        assert human_player.bid != 10

        #confirm bid is unchanged
        assert human_player.bid == -1

        #valid bid for handicapped player
        assert bm.successful_player_bid(human_player, forbidden_bid=3, bid_amount=2) 
        assert human_player.bid == 2

    def test_reset_bids(self, bm, computer_players):
        
        #set random bids
        for player in computer_players:
            player.bid = random.randint(1,5)
            assert player.bid > 0 #sanity check

        #reset bids
        bm.reset_bids(player_queue = computer_players)

        # Assert all bids are reset
        assert all(player.bid == -1 for player in computer_players)


    @pytest.mark.parametrize(
        "bids, max_cards, expected_banned",
        [
            ([1,1,2,2], 8, 2), # 8-6 = 2
            ([1,1,2,2], 7, 1), # 7-6 = 1
            ([1,1,2,2], 6, 0), # 6-6 = 0
            ([1,1,2,3], 6, -1), # 6-7 = -1
            ([1,1,4,4], 6, -1), # -1
            ([1,1,4,4], 7, -1), # -1
            ([1,4,4,1], 8, -1), # -1
            ([1,1,2], 8, 4),  #8-4 - 4
        ]
    )

    def test_calculate_banned_numbers(self, bm, computer_players, bids, max_cards, expected_banned):
        
        for player, bid in zip(computer_players, bids):
            player.bid = bid

        bm.update_current_bids(computer_players)
        result = bm.calculate_banned_number(max_cards=max_cards)

        if expected_banned == -1:
            # if no banned number expected, make sure its not in bids
            assert result not in bids
        else:
            assert result == expected_banned
    