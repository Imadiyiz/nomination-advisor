from .StepManager import *

class LocalCardAssignmentFlow:
    """
    Handles the flow of steps to assign cards to the local player

    Returns context
    """
    def __init__(self, 
                 valid_card_initials: set):
        
        self.stepManager = StepManager()
        self.valid_card_initials = valid_card_initials
    
    def assign_card(self, player: Player) -> str:
        """
        Logic for prompting the player to assign their card

        Returns choice of initials as string
        """
            
        initials = self.stepManager.run_step(
                    step = LocalAddCardStep(),
                    prompt_args={"player": player},
                    validate_args={"valid_card_initials": self.valid_card_initials}
                    )

        # clear_screen(0)
        
        return initials
        
