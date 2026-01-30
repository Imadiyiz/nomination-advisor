from .StepManager import *


class BiddingFlow:
    """
    Handles the flow of steps to player bids
    """
    def __init__(self, player_queue):
        
        self.context = {
            "bid_amounts": [],
            }
        
        self.stepManager = StepManager()
        self.player_queue = player_queue
    
    def run(self, round_no: int, max_cards: int, player: Player, forbidden_bid: int):

        prompt_args = {'forbidden_bid': forbidden_bid}
        validate_args = {'forbidden_bid': forbidden_bid,
                         'player': player}

        #step 1: Bidding menu confirmation
        while True:
            print(f"""\nBIDDING BEGINS\n
                  ROUND {round_no}: {max_cards} CARDS PER HAND\n
                  {player} is bidding now""")

            result = self.stepManager.run_step(BiddingMenuStep())
            if result != 'BACK':
                break

        #step 2: Make Bid
        while not is_valid and len(self.context['bid_amounts'] < len(self.player_queue)): # When is it ok to stop bidding
            clear_screen(0)

            # runs the bidding step and returns an integer
            bid_value = self.stepManager.run_step(step = BiddingStep(),
                                                  prompt_args=prompt_args,
                                                  validate_args=validate_args)

            # removes the bid value if back is selected
            if bid_value == 'BACK':
                if self.context["bid_amount"]:
                    self.context["bid_amount"].pop()
                continue

            # determine whether the bid was acceptable
            is_valid = self.successful_player_bid(
                player, forbidden_bid=forbidden_bid, bid_amount=bid_value
            )
            if is_valid:
                self.context['bid_amount'].append({player.name : bid_value})
                print(f"{player.name} bid {bid_value} Card" + ("s" if bid_value != 1 else ""))
            else:
                raise ValueError("Unable to bid that amount.")
            
        return self.context
    


         