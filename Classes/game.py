from Utils.enums import GameMode

from Classes.game_engine import GameEngine
from game_state import GameState


class Game:

    def __init__(self, mode: GameMode):
        player_names = ('Mike', 'John', 'Harun', 'Abhi')

        # If perspective is not assigned, it is blank
        self.engine = GameEngine(
            state=GameState(player_order=player_names, perspective='Mike'),
            mode=mode)

    def start(self):
        self.engine.run()