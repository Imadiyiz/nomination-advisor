from Classes.game_engine import GameEngine
from enum import Enum

class GameMode(Enum):
    ASSISTANT = 'assistant'
    SINGLE_PLAYER = 'single_player'

class Game:

    def __init__(
        self,
        mode: GameMode,
        engine: GameEngine,
    ):
        self.mode = mode
        self.engine = engine(mode)

    def start(self):
        self.engine.run()