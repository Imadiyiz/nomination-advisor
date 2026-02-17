from .StepManager import *
from Classes.BiddingManager import BiddingManager

class BiddingFlow:
    """
    Handles the flow of steps to player bids
    """
    def __init__(self, player_queue: list[Player]):
        
        self.context = {
            "": [],
            }
        
        self.stepManager = StepManager()
        self.player_queue = player_queue
    
    def run(self, round_no: int, max_cards: int,
            players: list[Player], 
            bidding_manager: BiddingManager, trump_suit: str):
        
        print("Bidding Phase Commencing\n")
        
        for player in players:

            self._run_single_player_bid(
                round_no=round_no,
                player=player,
                max_cards=max_cards,
                trump_suit=trump_suit,
                bidding_manager=bidding_manager,
            )    


    def _run_single_player_bid(self,
                              player: Player,
                              round_no: int,
                              max_cards: int, 
                              bidding_manager: BiddingManager,
                              trump_suit: str
                              ):
        # only have forbidden bid if player is last to bid
        if player.handicapped_bid:
            forbidden_bid = bidding_manager.calculate_banned_number(max_cards)
        else:
            forbidden_bid = -1

        while True:
            bid_value = self._prompt_for_bid(
                player=player, 
                forbidden_bid=forbidden_bid,
                bidding_manager=bidding_manager, 
                trump_suit=trump_suit,
                round_no=round_no, 
                max_cards=max_cards,
                )
            
            if not bid_value and bid_value != 0:
                raise ValueError("no bid value received")
            
            if bid_value == "BACK":
                continue

            if bidding_manager.successful_player_bid(
                player=player,
                forbidden_bid=forbidden_bid,
                bid_amount=bid_value
            ):
                
                bidding_manager.update_current_bids(
                    player_queue=self.player_queue)

                print(f"{player.name} bid {bid_value}")
                return bid_value
        
            print("Invalid bid, try again")

    def _prompt_for_bid(self,
                            player: Player,
                            round_no: int,
                            max_cards: int, 
                            bidding_manager: BiddingManager,
                            trump_suit: str,    
                            forbidden_bid: int    
        ):
        """
        Private method which runs the prompt for bid and returns the value of the bid
        

        Returns
            int: Legal bid made by player
        """

        while True:
                clear_screen()
                print(
f"""Round {round_no}: {max_cards} cards per hand""")

                result = self.stepManager.run_step(
                    step = BiddingMenuStep(),
                    prompt_args={
                        "player": player,
                        "trump_suit": trump_suit,
                        "current_bids": bidding_manager.current_bids,
                        "forbidden_bid": forbidden_bid,
                        "max_cards": max_cards},
                    validate_args={"forbidden_bid" : forbidden_bid}
                    )
                
                return result