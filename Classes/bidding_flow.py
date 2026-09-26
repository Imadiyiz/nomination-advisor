from Classes.ui_manager import player_hand_str_creator
from game_state import GameState
from Utils.types import CardInt, PlayerStr, TrumpStr

from .step_manager import *
from Utils.constants import CARDS_PER_ROUND


class ManualBiddingFlow:
    """
    Handles the flow of steps to player bids. Accepts a state object and returns the updated gamestate truth.
    This includes the new bids
    """
    def __init__(self):
        
        self.stepManager = StepManager()
    
    def run(self,
            player: PlayerStr,
            state: GameState,
            restricted_bid: int) -> int:
        """Runs the bidding flow for players who need to use the CLI to place their bids.
        Assumes that the restricted bid has been set correctly if applicable.

        Args:
            player (PlayerStr): The player who needs to place a bid.
            state (GameState): The current state of the game.
            restricted_bid (int): The restricted bid value, if any.

        Returns:
            int: The bid placed by the player.
        """

        # Determine if the player is handicapped based on the restricted bid.
        is_handicapped = restricted_bid != -1

        # Prompt the player for their bid until a valid bid is received.
        while True:
                bid_value = self._prompt_for_bid(
                    player=player, 
                    state = state,
                    forbidden_bid=restricted_bid,
                    is_handicapped=is_handicapped
                    )
                
                if not bid_value and bid_value != 0:
                    raise ValueError("no bid value received")
                
                if bid_value == "BACK":
                    continue

                # Ensure the bid is valid
                if 0 <= bid_value <= 8 and bid_value != restricted_bid:
                    return bid_value  # Return the bid value instead of the state
            
                print("Invalid bid, try again // PRINT STATEMENT")

    def _prompt_for_bid(self,
                            player: PlayerStr,
                            state: GameState,
                            forbidden_bid: int,
                            is_handicapped: bool = False
        ) -> int:
        """
        Private method which runs the prompt for bid and returns the value of the bid made by the player.
        

        Returns:
            int: Legal bid made by player
        """
        player_hand_str = player_hand_str_creator(player, state)

        while True:
                clear_screen()
                print(
f"""Round {state.round}: {CARDS_PER_ROUND[state.round - 1]} cards per hand""")

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