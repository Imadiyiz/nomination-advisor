from .StepManager import *


class IterativeTrumpFlow:
    """
    Handles the flow of steps for determining the trump after round 1
    """
    def __init__(self):
        
        self.context = {'trump_suit': ''}
        
        self.stepManager = StepManager()
    
    def run(self, player):

        suits_map = {'C': 'Clubs',
                      'S': 'Spades',
                        'H': 'Hearts',
                          'D': 'Diamonds'}
        prompt_args = {'suits_map' : suits_map,
                       'player': player}
        validate_args = {'suits_map' : suits_map}
        feedback_args = {'suits_map' : suits_map,
                         'player': player}

        #step 1: Determine auto or manual trump selection
        while True:
            print(f"""{player} determines trump for next round""")

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


    
        
    


         