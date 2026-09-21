from Classes.ui_manager import player_hand_str_creator
from game_state import GameState
from Utils.types import CardInt, PlayerStr, TrumpStr

from .step_manager import *


class BiddingFlow:
    """
    Handles the flow of steps to player bids. Accepts a state object and returns the updated gamestate truth.
    This includes the new bids
    """
    def __init__(self):
        
        self.stepManager = StepManager()
    
    def run(self, state: GameState):

        max_cards = state.CARDS_PER_ROUND[state.round - 1]
        restriction = - 1
        
        for i, player in enumerate(state.player_order):

            is_handicapped = False
            if i == len(player) - 1:
                is_handicapped = True

            # Restricted bid validation
            if sum(state.bids.values()) > max_cards:
                restriction = -1
            else:
                restriction = max_cards - sum(state.bids.values())
            
            new_state = self._run_single_player_bid(
                player=player,
                state = state,
                is_handicapped = is_handicapped,
                restriction=restriction
            )    

            state = new_state  # Update state for next player

        return state # Post bidding state


    def _run_single_player_bid(self,
                              player: PlayerStr,
                              state: GameState,
                              restriction: int = -1,
                              is_handicapped: bool = False
                              ):

        while True:
            bid_value = self._prompt_for_bid(
                player=player, 
                state = state,
                forbidden_bid=restriction,
                is_handicapped=is_handicapped
                )
            
            if not bid_value and bid_value != 0:
                raise ValueError("no bid value received")
            
            if bid_value == "BACK":
                continue

            # Ensure the bid is valid
            if 0 <= bid_value <= 8 and bid_value != restriction:
                state.bids[player] = bid_value
                print(f"{player} bid {bid_value}")
                return state  # Update state
        
            print("Invalid bid, try again")

    def _prompt_for_bid(self,
                            player: PlayerStr,
                            state: GameState,
                            forbidden_bid: int,
                            is_handicapped: bool = False
        ):
        """
        Private method which runs the prompt for bid and returns the value of the bid
        

        Returns
            int: Legal bid made by player
        """
        player_hand_str = player_hand_str_creator(player, state)

        while True:
                clear_screen()
                print(
f"""Round {state.round}: {state.CARDS_PER_ROUND[state.round - 1]} cards per hand""")

                result = self.stepManager.run_step(
                    step = BiddingMenuStep(),
                    prompt_args={
                        "player": player,
                        "player_hand_str": player_hand_str,
                        "trump_suit": state.trump_suit,
                        "current_bids": state.bids,
                        "forbidden_bid": forbidden_bid,
                        "is_handicapped": is_handicapped},
                    validate_args={"forbidden_bid" : forbidden_bid}
                    )
                
                return result