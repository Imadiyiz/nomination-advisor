# contents of the game loop

from Classes.game import Game
from Utils.enums import GameMode

game = Game(mode=GameMode.ASSISTANT)
game.start()
