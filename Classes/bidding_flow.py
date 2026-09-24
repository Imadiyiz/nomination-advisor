from Classes.ui_manager import player_hand_str_creator
from game_state import GameState
from Utils.types import CardInt, PlayerStr, TrumpStr

from .step_manager import *
from Utils.constants import CARDS_PER_ROUND


class BiddingFlow:
    """
    Handles the flow of steps to player bids. Accepts a state object and returns the updated gamestate truth.
    This includes the new bids
    """
    def __init__(self):
        
        self.stepManager = StepManager()
    
    def run(self, max_cards: int, players_to_bid: set[PlayerStr], bids_total: int) -> GameState:
        """Runs the bidding flow for players who need to use the CLI to place their bids.

        Args:
            max_cards (int): Maximum number of cards that can be bid in this round.
            players_to_bid (set[PlayerStr]): Set of players who need to place bids.

        Returns:
            GameState: Updated game state after all players have placed their bids.
        """

        restriction = - 1

        print("Bidding Phase Commencing\n")
        
        for i, player in enumerate(players_to_bid):

            is_handicapped = False
            if i == len(players_to_bid) - 1:
                is_handicapped = True

            # Restricted bid validation
            if bids_total > max_cards:
                restriction = -1
            else:
                restriction = max_cards - bids_total
            
            bid = self._run_single_player_bid(
                player=player,
                state = state,
                is_handicapped = is_handicapped,
                restriction=restriction
            )    


            bids_total += bid

        return bid 


    def _run_single_player_bid(self,
                              player: PlayerStr,
                              state: GameState,
                              restriction: int = -1,
                              is_handicapped: bool = False
                              ) -> int:

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
                return bid_value  # Return the bid value instead of the state
        
            print("Invalid bid, try again")

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