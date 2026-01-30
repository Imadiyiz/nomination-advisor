# Contents for the Bidding Manager python file

from .PlayerClass import Player
from typing import List
import random
from Utils.tools import clear_screen


class BiddingManager:
    """
    Manages the rules and context of the bidding logic for players
    """

    def __init__(self, UIManager):
        self.current_bids = dict()
        self.current = 0
        self.forbidden_bid = -1
        self.UIManager = UIManager

    def update_current_bids(self, player_queue: List[Player]):
        """
        Function for updating the current bids dictionary based on the turn order
        Ideally meant to be used once before the round commenences

        Args:
            player_queue (list[Player]): The player queue is necessary to preserve the correct order
        """

        self.current_bids = {
            player.name: player.bid if player.bid > -1 else 'X'
            for player in player_queue
        }
    
    # would rather have a ruleset as opposed to multiple functions
    #could this function go inside step?
    def successful_player_bid(self, player: Player, forbidden_bid: int = -1, bid_amount: int = 0) -> bool:
        """
        Validates the player bid and assigns bid values if valid

        Returns:
          bool: True if the bid is successful, False otherwise
        """

        if player.handicapped_bid and bid_amount == forbidden_bid:
            return False
        
        if 0 <= bid_amount < 9:
            player.bid = bid_amount
            self.current_bids[player.name] = bid_amount
            return True
        
        return False

    def reset_bids(self, player_queue: List[Player]):
        for player in player_queue:
            player.reset_bid()
            self.current_bids[player.name] = 'X'
        
    def calculate_banned_number(self, max_cards):
        """
        Function for calculating the banned number the player is unable to bid this round
        """

        total_bids = sum(int(bid) for bid in self.current_bids.values() if bid != 'X')
        banned_number = max_cards - total_bids 
        return banned_number if banned_number > -1 else -1

    def start_bidding(self, trump_suit:str, player_queue: List[Player], round_no:int = 1, max_cards: int = 8):
            """
            Function for the functionality of the bidding round
            """
            clear_screen()
            
            #Bidding output begins
            self.UIManager.display_message(f"""\nBIDDING BEGINS\n""")

            #end bidding information
            clear_screen()

            self.display_round_difference(max_cards=max_cards)

    def display_round_difference(self, max_cards):
                
        """
        Displays the difference between the possible winning hands and the amount bidded by players
        """

        #calculate + or - round
        total_bids = 0

        #loop through bid's are valid numbers
        for bid in self.current_bids.values():
            if type(bid) == int:
                total_bids += bid
        difference = total_bids-max_cards

        print(f"{'+' if total_bids > max_cards else '-'}{abs(difference)} ROUND")

                
    def player_bid(self, player_queue: List[Player], player:Player=None, max_cards: int = 8):
        """
        High level block of player making bid, handles validation of input

        Returns TRUE or FALSE based on whether the bid was valid

        Args:
            player (Player): The player instance which is performing the bidding
        """

        #need to calculate handicapped here
        #reorders the dictionary 
        self.update_current_bids(player_queue)
        
        forbidden_bid = self.calculate_banned_number(max_cards)

        

