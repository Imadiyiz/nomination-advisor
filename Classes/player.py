from Classes.game_engine import GameEngine
from Utils.types import TrumpStr, CardInt
from game_state import GameState
from abc import ABC, abstractmethod
from belief_model import BeliefModel

class Player(ABC):

    def __init__(self,name: str, belief_model: BeliefModel):
        """Initialize the player with a belief model.

        Args:
            name (str): The name of the player.
            belief_model (BeliefModel): The belief model associated with the player.
        """
        super().__init__()
        self.name = name
        self.belief_model = belief_model

    @abstractmethod
    def choose_card(self) -> CardInt:
        ...
    
    @abstractmethod
    def choose_bid(self) -> int:
        ...

    @abstractmethod
    def choose_trump_suit(self) -> TrumpStr:
        ...