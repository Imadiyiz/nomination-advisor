from .step_manager import *
from Utils.card_serialization import get_suit_from_initial


class TrumpSelectionTypeFlow:
    """
    Handles the flow of deciding which trump selection type is chosen.
    Initial_trump_suit is validated. Can print in this flow.
    """
    def __init__(self):
        
        self.context = {'manual_trump_generation' : None,
                        'initial_trump_suit': ''}
        
        self.stepManager = StepManager()
    
    def run(self) -> bool:
        """Manual is true, automatic is false"""
        validate_args = {}
        

        print("Determine Initial Trump Suit")

        result = self.stepManager.run_step(TrumpSelectionStep())
        clear_screen() #1

        return result.lower() in {'y', ''}

        
            
        
    


         