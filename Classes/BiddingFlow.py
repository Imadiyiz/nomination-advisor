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

        self._show_bidding_menu(
                              player = player,
                              round_no = round_no,
                              max_cards = max_cards, 
                              bidding_manager = bidding_manager,
                              trump_suit = trump_suit
            
        )

        while True:
            bid_value = self._prompt_for_bid(
                player=player, forbidden_bid=forbidden_bid)
            
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
                return 
        
            print("Invalid bid, try again")

    def _show_bidding_menu(self,
                            player: Player,
                            round_no: int,
                            max_cards: int, 
                            bidding_manager: BiddingManager,
                            trump_suit: str       
        ):

        while True:
                print(
                    f"\nBIDDING BEGINS\n"
                    f"ROUND {round_no}: {max_cards} CARDS PER HAND\n"
                    f"{player} is bidding now"
                    )

                result = self.stepManager.run_step(
                    step = BiddingMenuStep(),
                    prompt_args={
                        "player": player,
                        "trump_suit": trump_suit,
                        "current_bids": bidding_manager.current_bids,
                        "max_cards": max_cards}
                    )
                    
                if result != 'BACK':
                    return
                
    def _prompt_for_bid(self, player: Player, forbidden_bid:int) -> int:
        """
        Private method which runs the prompt for bid and returns the value of the bid
        
        Args:
            player(Player): The player object which is performing the bid
            forbidden_bid(int): Invalid bid amount due to rules
        

        Returns
            int: Legal bid made by player
        """

        # runs the bidding step and returns an integer
        clear_screen(0)
        return self.stepManager.run_step(
            step = BiddingStep(),
            prompt_args={
                "player": player,
                "forbidden_bid": forbidden_bid
            },
            validate_args={
                "forbidden_bid": forbidden_bid},
        )
