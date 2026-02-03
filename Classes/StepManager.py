# contents of the StepManager.py file
from .StepClass import *

class StepManager:
    """
    StepManager is used to manage the flow of CLI prompts

    """

    def __init__(self):
        """
        Docstring for __init__
        
        :param steps: a list of step names to be followed
        """
        
        # list which stores dictionaries of user inputs
        self.history = []

    def run_step(self, 
                 step: Step,
                 prompt_args: dict = {},
                 validate_args: dict = {},
                 feedback_args: dict = {}): 
            """
            Controls flow of CLI steps taken for player setup phase

            returns nothing if successful
            
            """
        
            #ask current question
            while True:
                    
                    try:
                      value = step.validate(
                            user_input = input(step.prompt(args = prompt_args)),
                            args = validate_args)

                      if value == 'BACK':
                           return 'BACK'
                      
                      if step.feedback(value, feedback_args):
                           print(step.feedback(value, feedback_args))

                      self.history.append(step)
                      return value
                    
                    except ValueError as e:
                         print(f"Error: {e}")




