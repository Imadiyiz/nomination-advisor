from Utils.enums import GameMode

from Classes.game_engine_copy import GameEngine
from game_state import GameState


class Game:

    def __init__(self, mode: GameMode):
        player_names = ('Mike', 'John', 'Harun', 'Abhi')
        self.engine = GameEngine(
            state=GameState(player_order=player_names),
            mode=mode)

    def start(self):
        self.engine.run()