from .StepManager import *


class InitialTrumpFlow:
    """
    Handles the flow of steps for determining the initial trump
    """
    def __init__(self):
        
        self.context = {'manual_trump_generation' : '',
                        'trump_card_initials': ''}
        
        self.stepManager = StepManager()
    
    def run(self, valid_card_initials):

        validate_args = {'valid_card_initials' : valid_card_initials}
        #step 1: Determine auto or manual trump selection
        while True:
            print(f"""Determine Initial Trump""")

            result = self.stepManager.run_step(TrumpSelectionStep())

            if result.lower() in ('y', ''):
                self.context['manual_trump_generation'] = True
            else:
                self.context['manual_trump_generation'] = False
                return self.context  # can return here to avoid rest of script

            clear_screen(1)

        #step 2: Handle initial manual trump card selection
            trump_card_initials = self.stepManager.run_step(step = ManualTrumpStep(),
                                                  validate_args=validate_args)

            # removes the bid value if back is selected
            if trump_card_initials == 'BACK':
                if self.context["trump_card_initials"]:
                    self.context["trump_card_initials"].pop()
                continue
            else:
                self.context['trump_card_initials'] = trump_card_initials
                return self.context
            
        
    


         