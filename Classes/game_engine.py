# Contents of the GameManager class

import random
from enum import Enum
from Classes.game import GameMode

from game_state import GameState
from Classes.round_manager import RoundManager
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
from .step import *
from .player import Player
from .human_player import PerspectivePlayer
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

class GameEngine:

    def __init__(
        self,
        state: GameState,
        mode: GameMode,
        player_map: dict[PlayerStr, Player] = {},
    ):
        self.state = state
        self.round_manager = RoundManager(
             player_map=player_map,
             gamemode=mode)

    def run(self):
        while not self.state.game_over:
            self.run_round()

    def run_round(self):
        self.round_manager.run(self.state)


