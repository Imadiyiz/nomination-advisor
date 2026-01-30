
class GameState():
    """
    Class for storing the attributes of the current game
    """

    def __init__(self):
        self.known_cards = []
        self.unknown_cards = []
        self.current_trick = []
        self.hand_sizes = {}
        self.trump = ''
        self.starting_card = ''
        self.winning_card = ''
        self.trumped = False
        