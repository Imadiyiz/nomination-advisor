from Classes.ui_manager import (
    CLI_format_hand,
    player_hand_str_creator,
    scoreboard_display,
    table_str_creator,
)
from game_state import GameState
from Utils.card_serialization import initials_to_id
from Utils.types import CardInt, PlayerStr

from .step_manager import *


class PlayingFlow:
    """
    Handles the flow of steps to play cards

    Returns context
    """
    def __init__(self):
        
        self.stepManager = StepManager()

    def play_turn(self, player: PlayerStr, state: GameState) -> CardInt:
        """
        Logic for prompting the player to play their cards, loops until
        valid move has been performed.

        Returns Cardint e.g 50, 13
        """

        if player == state.perspective:
            return self._prompt_for_local_play_card(player, state)
        else:
            return self._prompt_for_opponent_play_card(player, state)
            
                
    def _prompt_for_local_play_card(self,
                                    player: PlayerStr,
                                    state: GameState) -> CardInt:
        """
        Private method which runs the prompt for local play card and returns index of selected card
        
        Args:
            player(Player): The player object which is playing the card
        
        Returns:
            card(CardInt): The card the player has decided to play
            
        """
        table_str = table_str_creator(state)
        expanded_player_hand_str = CLI_format_hand(
            state.hands[player])
        round_scoreboard = scoreboard_display(
            state=state, round=False)

        result = self.stepManager.run_step(
                    step = PlayerPlayCardStep(),
                    prompt_args={
                        "player_name": player,
                        "player_hand": state.hands[player],
                        "expanded_player_hand_str": expanded_player_hand_str,
                        "trump_suit": state.trump_suit,
                        "table_str": table_str,
                        "round_scoreboard": round_scoreboard},
                    validate_args={"player": player}
                    )

        # clear_screen(0)

        # Get CardInt from the result
        player_hand_list = list(state.hands[player])
        return player_hand_list[int(result)]

    def _prompt_for_opponent_play_card(self,
                                       player:PlayerStr,
                                       state: GameState) -> CardInt:
        
        """
        Private method which runs the prompt for opponent play card 
        and returns initiials of selected card
        
        Args:
            player(Player): The player object which is playing the card
        

        Returns
            str: initials of selected card
        """

        table_str = table_str_creator(state)
        round_scoreboard = scoreboard_display(state=state, 
                                              round=False)

        while True:
            
            table_str = table_str_creator(state)
            opponent_hand_str = player_hand_str_creator(player, state)
            
            result = self.stepManager.run_step(
                    step = OpponentPlayCardStep(),
                    prompt_args={
                        "opponent_name": player,
                        "opponent_hand_str": opponent_hand_str,
                        "trump_suit": state.trump_suit,
                        "table_str": table_str,
                        "round_scoreboard": round_scoreboard},
                    validate_args={"player": player}
                    )

            
            if result != 'BACK':
                return initials_to_id(result)
            
            #clear_screen(0)