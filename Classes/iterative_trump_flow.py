from Utils.types import PlayerStr

from .step_manager import *


class IterativeTrumpFlow:
    """
    Handles the flow of steps for determining the trump after round 1
    """
    def __init__(self):
        
        self.context = {'trump_suit': ''}
        
        self.stepManager = StepManager()
    
    def run(self, player: PlayerStr):

        suits_map = {'C': 'Clubs',
                      'S': 'Spades',
                        'H': 'Hearts',
                          'D': 'Diamonds'}
        
        prompt_args = {'suits_map' : suits_map,
                       'player': player}
        validate_args = {'suits_map' : suits_map}
        feedback_args = {'suits_map' : suits_map,
                         'player': player}

        while True:

            result = self.stepManager.run_step(
                IterativeTrumpSelectionStep(),
                prompt_args=prompt_args,
                validate_args=validate_args,
                feedback_args=feedback_args,
            )

            for char, trump in suits_map.items():
                if char == result.upper():
                    self.context['trump_suit'] = trump
                    return self.context  # can return here to avoid rest of script


    
        
    


         