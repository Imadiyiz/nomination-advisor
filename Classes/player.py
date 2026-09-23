from Classes.game_engine import GameEngine
from game_state import GameState

class Player(ABC):

    @abstractmethod
    def choose_card(self, state: GameState) -> CardInt:
        ...
    
    @abstractmethod
    def choose_bid(self, state: GameState) -> int:
        ...