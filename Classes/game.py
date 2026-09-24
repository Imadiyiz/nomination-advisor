from enum import Enum

from Classes.game_engine_copy import GameEngine


class GameMode(Enum):
    ASSISTANT = 'assistant'
    SINGLE_PLAYER = 'single_player'
    SIMULATION = 'simulation'

class Game:

    def __init__(
        self,
        mode: GameMode,
        engine: GameEngine,
    ):
        self.mode = mode
        self.engine = engine

    def start(self):
        self.engine.run()