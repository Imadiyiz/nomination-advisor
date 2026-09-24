from Utils.card_serialization import get_suit_from_initial
from Utils.types import PlayerStr

from .step_manager import *


class ManualTrumpSelectionFlow:
    """
    Initial_trump_suit is validated. Can print in this flow as it is only
    used in assist mode or single player. 
    """
    def __init__(self):

        
        self.stepManager = StepManager()
    
    def run(self, player_name: PlayerStr):

        validate_args = {'player': player_name}
        
        # Results are already sanitised
        result = self.stepManager.run_step(
            step = ManualTrumpStep(),
            validate_args=validate_args)

        return get_suit_from_initial(result)
