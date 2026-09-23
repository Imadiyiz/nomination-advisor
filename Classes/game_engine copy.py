# Contents of the GameManager class

import random
from enum import Enum
from game import GameMode

from game_state import GameState
from round_manager import RoundManager
from Utils.card_serialization import (
        SUITS,
        SUITS_TO_SYMBOL,
        get_suit_str,
        id_to_initials,
        id_to_prose,
        initials_to_id,
)
from Utils.cli_tools import clear_screen
from Utils.types import CardInt, PlayerStr, TrumpStr

from .bidding_flow import BiddingFlow
from .deck import Deck
from .human_player import HumanPlayer
from .iterative_trump_flow import IterativeTrumpFlow
from .local_card_assignment_flow import LocalCardAssignmentFlow
from .manual_trump_selection_flow import ManualTrumpSelectionFlow
from .player_setup_flow import PlayerSetupFlow
from .playing_flow import PlayingFlow
from .step import *
from .trump_manager import TrumpManager
from .trump_selection_type_flow import TrumpSelectionTypeFlow
from .ui_manager import UIManager
from .player import Player
from Utils.constants import VALID_CARD_INITIALS

class Phase(Enum):
        PLAYER_SELECTION = "player_selection"
        HAND_ASSIGNMENT = 'hand_assignment'
        INITIAL_TRUMP_SELECTION = "initial_trump_selection"
        TRUMP_REDECIDING = "trump_redeciding"
        BIDDING = "bidding"
        PLAYING = "playing"
        SCORING = "scoring"
        GAME_OVER = "game_over"

class GameEngine():

    def __init__(
        self,
        state: GameState,
        player_map: dict[PlayerStr, Player],
        round_manager: RoundManager,
        mode: GameMode,
    ):
        self.state = state
        self.player_map = player_map
        self.round_manager = round_manager

    def run(self):
        while not self.state.game_over:
            self.run_round()

    def run_round(self):
        self.round_manager.run(self.state)


