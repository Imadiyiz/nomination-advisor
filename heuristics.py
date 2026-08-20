class Heuristics:

    def __init__(self, 
                 aggression: float = 0.5,
                 belief_in_open_info: float = 0.5,
                 risk_tolerance: float = 0.5,
                 adaptability: float = 0.5):

        """Contains the attributes which alter the player's move evaluation"""

        # Move parameter
        self.aggression = aggression                         # 0 = Passive, 1 = Attacking
      
        
        # Bidding parameters
        self.risk_tolerance = risk_tolerance                 # 0 = Safe, 1 = Gambler
        # Decide whether to believe that others will secure their bids
        self.belief_in_open_information = belief_in_open_info # 0 = Paranoid, 1 = Trusting 

        # Rewards multiplier
        self.adaptability = adaptability                     # 0 = Rigid, 1 = Quick to adjust (Reward)

        # Rewards
        self.bid_reward = 0.0         # reward between -1.0 and 1.0
        self.move_reward = 0.0         # reward between -1.0 and 1.0

    