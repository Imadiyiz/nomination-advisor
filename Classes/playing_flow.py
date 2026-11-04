
from Classes.ui_manager import (
    CLI_format_hand,
    player_hand_str_creator,
    scoreboard_display,
    table_str_creator,
)
from game_state import GameState
from Utils.card_serialization import id_to_initials, initials_to_id
from Utils.types import CardInt, PlayerStr
from Utils.constants import VALID_CARD_INITIALS

from .step_manager import *


class HumanPlayingFlow:
    """
    Handles the flow of steps to play cards

    Returns context
    """
    def __init__(self):
        
        self.stepManager = StepManager()

    def play_turn(self, player: PlayerStr, state: GameState, 
                  deck_valid_initials: set[str]) -> CardInt:
        """
        Logic for prompting the player to play their cards, loops until
        a valid move has been performed. Diverts to different methods based on whether the player
        is local or an opponent. Uses the StepManager to handle the prompting and validation.

        Returns CardInt e.g 50, 13
        """

        if player == state.perspective:
            return self._prompt_for_perspective_play_card(player, state)
        else:
            return self._prompt_for_opponent_play_card(player, state, deck_valid_initials)
            
                
    def _prompt_for_perspective_play_card(self,
                                    player: PlayerStr,
                                    state: GameState) -> CardInt:
        """
        Private method which runs the prompt for local play card and returns the index of the selected card
        
        Args:
            player(PlayerStr): The player object which is playing the card
        
        Returns:
            CardInt: The card the player has decided to play
            
        """
        table_str = table_str_creator(state)
        expanded_player_hand_str = CLI_format_hand(
            state.hands[player])
        trick_totals_scoreboard = scoreboard_display(
            state=state, round=True)

        result = self.stepManager.run_step(
                    step = PlayerPlayCardStep(),
                    prompt_args={
                        "player_name": player,
                        "player_hand": state.hands[player],
                        "expanded_player_hand_str": expanded_player_hand_str,
                        "trump_suit": state.trump_suit,
                        "table_str": table_str,
                        "trick_totals_scoreboard": trick_totals_scoreboard},
                    validate_args={"player_hand": state.hands[player]}
                    )

        # clear_screen(0)

        # Get CardInt from the result
        player_hand_list = list(state.hands[player])
        return player_hand_list[int(result)-1] # 1-indexed result from the prompt

    def _prompt_for_opponent_play_card(self,
                                       player:PlayerStr,
                                       state: GameState,
                                       deck_valid_initials: set[str]) -> CardInt:
        
        """
        Private method which runs the prompt for opponent play card 
        and returns initials of selected card
        
        Args:
            player(PlayerStr): The player object which is playing the card
            deck_valid_initials(set[str]): The set of valid card initials for the deck

        Returns:
            CardInt: the card selected by the opponent
        """

        table_str = table_str_creator(state)
        trick_totals_scoreboard = scoreboard_display(state=state, 
                                              round=True)

        #  Must be valid and be possible to given the world
        if not deck_valid_initials:
            raise ValueError("Deck valid initials set cannot be empty")

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
                        "trick_totals_scoreboard": trick_totals_scoreboard},
                        
                    validate_args={"valid_card_initials": deck_valid_initials}
                    )

            
            if result != 'BACK':
                return initials_to_id(result)
            
            #clear_screen(0)