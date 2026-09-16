
import random
from copy import deepcopy

import pytest

from bot import BotPlayer
from Classes.deck import Deck
from game_state import GameState
from Utils.types import *


@pytest.fixture
def hand_size(request) -> int:
    return getattr(request, 'param', 6) # default if param not found

@pytest.fixture
def player_amount(request) -> int:
    return getattr(request, 'param', 6) 

@pytest.fixture
def default_hand(hand_size) -> set:
    return set(random.sample(range(52), k=hand_size))

@pytest.fixture
def default_bots(player_amount) -> list:
    return [BotPlayer(name=f"BOT{i}") for i in range(player_amount)]

@pytest.fixture
def root_state(default_bots):
    return GameState(
        hands={db.name: set() for db in default_bots},                
        current_trick=(),      
        trump_suit="Diamonds", 
        player_order=tuple(bot.name for bot in default_bots),
        round_scores={p.name: 0 for p in default_bots},
        total_scores={p.name: 0 for p in default_bots},
    )

@pytest.fixture
def bot_name(default_bots):
    return default_bots[0].name

class TestGameState:
    """"Test functionality of GameState class, as it should be responsible for storing
    the state of the core game, and can be duplicated to create new worlds."""


    def test_valid_get_leader(self, root_state):
        """Ensures that the leader returned is the correct leader. Imperative
        for keeping order of the player order tuple"""

        print(root_state._leader)
        assert root_state._leader is None
        assert root_state._get_leader() == root_state.player_order[0]

        # Reset player order for new test
        root_state.player_order = ('BOT', 'BOT1', 'BOT2')
        root_state.current_trick = (('BOT', 41), )
        assert root_state._get_leader() == 'BOT'

    def test_next_player(self, root_state: GameState):
        """Ensures that the next player can correctly be determined. Essential for
        an ordering system using tuples."""

        assert root_state._leader is None
        assert len(root_state.current_trick) == 0
        assert root_state.next_player() == root_state.player_order[0]


        root_state._leader = None
        root_state.current_trick = (('BOT0', 41), )
        assert len(root_state.current_trick) == 1
        assert root_state.next_player() == root_state.player_order[1]

        root_state.current_trick = (('BOT0', 41), ('BOT1', 43) )
        assert root_state.next_player() == root_state.player_order[2]

        # Make player count 3 to verify wrap around logic
        root_state.player_order = root_state.player_order[:3]
        assert len(root_state.player_order) == 3

        root_state.current_trick = (('BOT0', 41), ('BOT1', 43), ('BOT2', 30),  )
        assert root_state.next_player() == root_state.player_order[0]

    def test_get_legal_moves(self, root_state: GameState, bot_name: PlayerStr):
        """Ensures that the correct legal moves are returned to the user. Imperative
        that the correct legal moves are returned to avoid invalid worlds being
        geberated in the MC sim"""

        # Check ValueError occurs with an empty hand
        assert len(root_state.hands[bot_name]) == 0
        with pytest.raises(ValueError):
            root_state.get_legal_moves(bot_name)

        root_state.hands[bot_name] = {1, 2, 3, 4, 5, 33}  # Set literal

        # Check empty trick, therefore any move is available
        assert len(root_state.current_trick) == 0
        assert root_state.get_legal_moves(bot_name) == {1, 2, 3, 4, 5, 33}

        # Check follow suit compliance
        root_state.current_trick = (('BOT3', 35), )
        assert root_state.get_legal_moves(bot_name) == {33}

        # Check player can discard any card if their hand does not contain
        # Lead suit
        root_state.current_trick = (('BOT3', 50), )
        assert root_state.get_legal_moves(bot_name) == {1, 2, 3, 4, 5, 33}

    def test_apply_move(self, root_state: GameState, bot_name: PlayerStr):
        """Ensures the action of a player making a move has a clean logical flow
        and returns a GameState object reflecting how the move affected the game"""

        rs = deepcopy(root_state)
        rs.hands[bot_name] = {1, 2, 3, 4, 5, 33}

        # Checks invalid moves are rejected
        with pytest.raises(ValueError):
            rs.apply_move(bot_name, 40)

        # Check new hand has removed card played by player
        # But remains in original state
        new_s = rs.apply_move(bot_name, 5)
        assert 5 not in new_s.hands[bot_name]
        assert 5 in rs.hands[bot_name]
        assert len(new_s.hands[bot_name]) < len(rs.hands[bot_name])
        rs = deepcopy(root_state)  # Reset

        # Check round score and winner updates correctly when there
        # is a winner
        assert sum(rs.round_scores.values()) == 0
        assert bot_name in rs.round_scores
        rs.player_order = (rs.player_order[0],)
        rs.hands[bot_name] = {4}
        new_state = rs.apply_move(bot_name, 4)

        assert rs.round_scores[bot_name] == 0
        assert new_state.round_scores[bot_name] == 1

        # Check winner is declared if trick complete
        assert new_state.winner == bot_name  

        # Check leader changes with win
        assert sum(score for score in rs.total_scores.values()) == 0
        assert sum(score for score in new_state.round_scores.values()) == 1
        # Check trick updates correctly
        # Check leader stays the same without win
        # Check original state has not been corrupted

    def test_update_total_score(self, root_state: GameState):
        """Ensure that the total score is updated when the conditions are right to do 
        so"""

        # Reset
        rs = deepcopy(root_state)

        # Ensure that players have cards in their hands
        for i, player in enumerate(rs.player_order):
            rs.hands[player] = {1 + i}

        # Check that total score is not updated if round is not complete
        assert sum(score for score in rs.total_scores.values()) == 0 

        # Check that total score is not updated if there are no bids
        assert sum(bid for bid in rs.bids.values()) == 0
        for player in rs.player_order:
            legal_moves = rs.get_legal_moves(player)
            if legal_moves:
                rs = rs.apply_move(player, legal_moves.pop())
                assert sum(score for score in rs.total_scores.values()) == 0

        # Reset
        rs = deepcopy(root_state)

        # Ensure that players have cards in their hands
        for i, player in enumerate(rs.player_order[:-1]):
            rs.hands[player] = {1 + i}
            rs.bids[player] = 1  # Set bids to ensure total score is updated when round is complete 

        rs.hands[rs.player_order[-1]] = {51}
        rs.bids[rs.player_order[-1]] = 0  # Ensures that the bids are not equal to the total tricks played

        # Check that total score is updated if round is complete and there are bids
        assert sum(score for score in rs.total_scores.values()) == 0

        # generate a complete round by having each player play a card until the round is complete
        for player in rs.player_order:
            legal_moves = rs.get_legal_moves(player)
            if legal_moves:
                rs = rs.apply_move(player, legal_moves.pop())

            if player != rs.player_order[-1]:  # Don't check last player to play
                assert sum(score for score in rs.total_scores.values()) == 0

        # Doesnt update
        assert sum(score for score in rs.total_scores.values()) != 0

        # Check that total score is not updated if round is not complete
        rs = deepcopy(root_state)

        # Ensure that players have cards in their hands
        for i, player in enumerate(rs.player_order[:-1]):
            rs.hands[player] = {1 + i, 12 + i, 22 + i}
            rs.bids[player] = 1

        rs.hands[rs.player_order[-1]] = {51}
        rs.bids[rs.player_order[-1]] = 0  # Ensures that the bids are not equal to the total tricks played

        assert sum(score for score in rs.total_scores.values()) == 0
        for player in rs.player_order:
            legal_moves = rs.get_legal_moves(player)
            if legal_moves:
                rs = rs.apply_move(player, legal_moves.pop())
            assert sum(score for score in rs.total_scores.values()) == 0
    
    def test_resolve_trick(self, root_state: GameState):
        """Ensure that the player who has played the winning card in the trick
        is declared."""

        # Trump is Diamonds by default
        trumped_first_state = deepcopy(root_state)  
        trumped_first_state.current_trick = (
        ('BOT0', 15), ('BOT1', 12), ('BOT2', 50),)
        assert trumped_first_state._resolve_trick(
            trumped_first_state.current_trick) == 'BOT0'

        trumped_last_state = deepcopy(root_state)  
        trumped_last_state.current_trick = (
        ('BOT0', 50), ('BOT1', 34), ('BOT2', 15),)
        assert trumped_last_state._resolve_trick(
            trumped_last_state.current_trick) == 'BOT2'
        
        high_card_state = deepcopy(root_state)  
        high_card_state.current_trick = (
                ('BOT0', 1), ('BOT1', 2), ('BOT2', 4),)
        assert high_card_state._resolve_trick(
        high_card_state.current_trick) == 'BOT2'  
        
        no_order_state = deepcopy(root_state)  
        no_order_state.current_trick = (
                ('BOT0', 1), ('BOT1', 50), ('BOT2', 30),)
        assert no_order_state._resolve_trick(
        no_order_state.current_trick) == 'BOT0' 

        # Checks that error occurs when the trick is empty
        with pytest.raises(ValueError):
            root_state._resolve_trick(root_state.current_trick)