from game_state import GameState
from Utils.types import CardInt, PlayerStr
from Classes.ui_manager import display_hand_str

from .step_manager import *


class LocalCardAssignmentFlow:
    """
    Handles the flow of steps to assign cards to the local player

    Returns context
    """
    def __init__(self, 
                 valid_card_initials: set):
        
        self.stepManager = StepManager()
        self.valid_card_initials = valid_card_initials
    
    def assign_card(self,
                    player_hand: set[CardInt],
                    max_cards: int,
                    perspective: PlayerStr = '',) -> str:
        """
        Logic for prompting the player to assign their card
        Returns choice of initials as string
        """

        player_hand_str = display_hand_str(
            player_hand = player_hand, 
            max_cards = max_cards,
            perspective = perspective,
            )
        
        initials = self.stepManager.run_step(
                    step = IterableLocalAddCardStep(),
                    prompt_args={"player": perspective,
                                 "maximum_cards": max_cards,
                                 "player_card_list": player_hand,
                                 "player_hand": player_hand, 
                                 "player_hand_str": str(player_hand_str)},
                    validate_args={"valid_card_initials": self.valid_card_initials}
                    )

        # clear_screen(0)
        
        return initials
    
    def generate_prompt(self, player: PlayerStr):
        self.stepManager.run_step(
            step = LocalAddCardStep(),
            prompt_args={"player": player,}
        )
        
