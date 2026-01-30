# little tools useful through the project

import os
import time

def clear_screen(delay: float = 1):
    """
    Function for clearing the cmd screen of its content
    """
    time.sleep(delay)
    os.system('cls' if os.name == 'nt' else 'clear')