class Heuristics:

    def __init__(self, 
                 aggression: float = 0.0,
                 belief_in_open_info: float = 0.0,
                 risk_tolerance: float = 0.0,
                 adaptability: float = 0.0):

        """Contains the attributes which alter the player's move evaluation"""

        self.aggression = aggression                         # 0 = Passive, 1 = Attacking
        self.belief_in_open_information = belief_in_open_info # 0 = Paranoid, 1 = Trusting
        
        # The 3 new parameters
        self.risk_tolerance = risk_tolerance                 # 0 = Safe, 1 = Gambler
        self.adaptability = adaptability                     # 0 = Rigid, 1 = Quick to adjust


    