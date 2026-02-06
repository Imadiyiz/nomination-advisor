from .StepManager import *
from Classes.BiddingManager import BiddingManager
from Classes.TableClass import Table
from Classes.ScoreboardClass import Scoreboard
from Classes.CardClass import Card

class PlayingFlow:
    """
    Handles the flow of steps to play cards

    Returns context
    """
    def __init__(self, 
                 table: Table,
                 scoreboard: Scoreboard,
                 valid_card_initials: set):
        
        self.context = {
            "player_results": [],
            }
        
        self.stepManager = StepManager()
        self.table = table
        self.scoreboard = scoreboard
        self.valid_card_initials = valid_card_initials
    
    def play_turn(self, player: Player, trump_suit: str):
        """
        Logic for prompting the player to play their cards

        Returns context object as
        {"players" : {"player" : "2"}, {"opponent" : "10D"}}
        """
                
        if player.opponent:
            return self._prompt_for_opponent_play_card(player, trump_suit)
        else:
            return self._prompt_for_local_play_card(player, trump_suit)

                
    def _prompt_for_local_play_card(self,
                                    player: Player,
                                    trump_suit: str) -> int:
        """
        Private method which runs the prompt for local play card and returns index of selected card
        
        Args:
            player(Player): The player object which is playing the card
        

        Returns
            int: index of legal card played in hand
        """

        suit_to_symbol = {
            "clubs" : "♣",
            "diamonds" : "♦",
            "hearts" : "♥",
            "spades" : "♠",
        }

        trump_suit_symbol = suit_to_symbol[trump_suit.lower()]
               
        result = self.stepManager.run_step(
                    step = PlayerPlayCardStep(),
                    prompt_args={
                        "player": player,
                        "trump_suit_symbol": trump_suit,
                        "scoreboard": self.scoreboard,
                        "table": self.table},
                    validate_args={"player": player}
                    )

        # clear_screen(0)
        
        return result

    def _prompt_for_opponent_play_card(self,
                                       player:Player,
                                       trump_suit: str):
        
        """
        Private method which runs the prompt for opponent play card 
        and returns initiials of selected card
        
        Args:
            player(Player): The player object which is playing the card
        

        Returns
            int: initials of selected card
        """

        suit_to_symbol = {
            "clubs" : "♣",
            "diamonds" : "♦",
            "hearts" : "♥",
            "spades" : "♠",
        }

        trump_suit_symbol = suit_to_symbol[trump_suit.lower()]
        
        while True:
                
            result = self.stepManager.run_step(
                        step = OpponentPlayCardStep(),
                        prompt_args={
                            "opponent": player,
                            "trump_suit_symbol": trump_suit,
                            "scoreboard": self.scoreboard,
                            "table": self.table},

                        validate_args={"valid_card_initials": self.valid_card_initials},
                        feedback_args={
                            "opponent": player}
                        )

            #clear_screen(0)
            
            return result
        
