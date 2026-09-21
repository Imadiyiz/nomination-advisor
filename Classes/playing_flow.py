from Classes.scoreboard import Scoreboard
from Classes.ui_manager import (
    CLI_format_hand,
    player_hand_str_creator,
    table_str_creator,
)
from game_state import GameState
from Utils.types import PlayerStr

from .step_manager import *


class PlayingFlow:
    """
    Handles the flow of steps to play cards

    Returns context
    """
    def __init__(self, 
                 scoreboard: Scoreboard,
                 valid_card_initials: set):
        
        self.context = {
            "player_results": [],
            }
        
        self.stepManager = StepManager()
        self.scoreboard = scoreboard
        self.valid_card_initials = valid_card_initials
    
    def play_turn(self, player: PlayerStr, state: GameState):
        """
        Logic for prompting the player to play their cards

        Returns context object as
        {"players" : {"player" : "2"}, {"opponent" : "10D"}}
        """

        if player != state.perspective:
            return self._prompt_for_opponent_play_card(player, state)
        else:
            return self._prompt_for_local_play_card(player, state)

                
    def _prompt_for_local_play_card(self,
                                    player: PlayerStr,
                                    state: GameState) -> int:
        """
        Private method which runs the prompt for local play card and returns index of selected card
        
        Args:
            player(Player): The player object which is playing the card
        
        Returns
            int: index of legal card played in hand
        """
        table_str = table_str_creator(state)
        expanded_player_hand_str = CLI_format_hand(state.hands[player])

        result = self.stepManager.run_step(
                    step = PlayerPlayCardStep(),
                    prompt_args={
                        "player_name": player,
                        "player_hand": state.hands[player],
                        "expanded_player_hand_str": expanded_player_hand_str,
                        "trump_suit": state.trump_suit,
                        "scoreboard": self.scoreboard, 
                        "table_str": table_str},
                    validate_args={"player": player}
                    )

        # clear_screen(0)
        return result

    def _prompt_for_opponent_play_card(self,
                                       player:PlayerStr,
                                       state: GameState) -> str:
        
        """
        Private method which runs the prompt for opponent play card 
        and returns initiials of selected card
        
        Args:
            player(Player): The player object which is playing the card
        

        Returns
            str: initials of selected card
        """

        table_str = table_str_creator(state)

        while True:
            
            table_str = table_str_creator(state)
            opponent_hand_str = player_hand_str_creator(player, state)
            
            result = self.stepManager.run_step(
                    step = OpponentPlayCardStep(),
                    prompt_args={
                        "opponent_name": player,
                        "opponent_hand_str": opponent_hand_str,
                        "trump_suit": state.trump_suit,
                        "scoreboard": self.scoreboard, 
                        "table_str": table_str},
                    validate_args={"player": player}
                    )
            
            if result != 'BACK':
                return result
            #clear_screen(0)