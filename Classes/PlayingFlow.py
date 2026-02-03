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
                 player_queue: list[Player],
                 table: Table,
                 scoreboard: Scoreboard,
                 valid_card_initials: set):
        
        self.context = {
            "player_results": [],
            }
        
        self.stepManager = StepManager()
        self.player_queue = player_queue
        self.table = table
        self.scoreboard = scoreboard
        self.valid_card_initials = valid_card_initials
    
    def run(self, players: list[Player], trump_suit: str):
        
        i = 0 

        while i < len(players):
                player = players[i]
                
                if player.opponent:
                    user_choice = self._prompt_for_opponent_play_card(
                         player=player,
                         trump_suit=trump_suit)
                    
                else:
                    user_choice = self._prompt_for_local_play_card(
                        player=player, trump_suit=trump_suit)
                
                if user_choice == "BACK":
                    if self.context["player_results"]:
                        self.context["player_results"].pop()
                    i -=1
                    continue

                self.context['players'].append({player: user_choice})
                i += 1

        return self.context   

                
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
        while True:
               
            result = self.stepManager.run_step(
                        step = PlayerPlayCard(),
                        prompt_args={
                            "player": player,
                            "trump_suit": trump_suit,
                            "scoreboard": self.scoreboard,
                            "stack": self.table.stack},
                        validate_args={"player": player}
                        )

            clear_screen(0)

            if result != 'BACK':
                return 'BACK'
            
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
        while True:
                
            result = self.stepManager.run_step(
                        step = OpponentPlayCard(),
                        prompt_args={
                            "opponent": player,
                            "trump_suit": trump_suit,
                            "scoreboard": self.scoreboard,
                            "stack": self.table.stack},

                        validate_args={"valid_card_initials": self.valid_card_initials},
                        feedback_args={
                            "opponent": player}
                        )

            clear_screen(0)

            if result != 'BACK':
                return 'BACK'
            
            return result