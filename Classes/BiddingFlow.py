from .StepManager import *
from Classes.BiddingManager import BiddingManager

class BiddingFlow:
    """
    Handles the flow of steps to player bids
    """
    def __init__(self, player_queue):
        
        self.context = {
            "": [],
            }
        
        self.stepManager = StepManager()
        self.player_queue = player_queue
    
    def run(self, round_no: int, max_cards: int,
            players: list[Player], 
            bidding_manager: BiddingManager, trump_suit: str,
            player_queue:list[Player]):

        for player in players:

            #calculate forbidden bid
            forbidden_bid = bidding_manager.calculate_banned_number(max_cards)

            # must assign every iteration to update the players
            bid_prompt_args = {'forbidden_bid': forbidden_bid, 'player': player}
            bid_validate_args = {'forbidden_bid': forbidden_bid}
            
            menu_prompt_args = {
                'trump_suit': trump_suit,
                'player': player,
                'current_bids': bidding_manager.current_bids
            }

            #reset every iteration
            is_valid = False
        
            #step 1: Bidding menu confirmation
            while True:
                print(f"""\nBIDDING BEGINS\n
                    ROUND {round_no}: {max_cards} CARDS PER HAND\n
                    {player} is bidding now""")

                result = self.stepManager.run_step(
                    step = BiddingMenuStep(),
                    prompt_args=menu_prompt_args)
                if result != 'BACK':
                    break

            #step 2: Make Bid
            while not is_valid: # When is it ok to stop bidding
                clear_screen(0)

                # runs the bidding step and returns an integer
                bid_value = self.stepManager.run_step(step = BiddingStep(),
                                                    prompt_args=bid_prompt_args,
                                                    validate_args=bid_validate_args)

                # removes the bid value if back is selected
                if bid_value == 'BACK':
                    continue

                # determine whether the bid was acceptable
                if not bidding_manager.successful_player_bid(
                    player, forbidden_bid=forbidden_bid, bid_amount=bid_value
                ):
                    raise ValueError("Unable to bid that amount.")
                
                print(f"{player.name} bid {bid_value} Card" + ("s" if bid_value != 1 else ""))
                    
                #update bids every iteration
                bidding_manager.update_current_bids(player_queue=player_queue)
                is_valid = True
            
        return self.context
    


         