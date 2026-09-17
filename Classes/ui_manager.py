# Contents of the UIManager python file
from game_state import GameState
from Utils.card_tools import id_to_prose, id_to_initials
from Utils.types import PlayerStr, CardInt


class UIManager:
    """
    Manages UI elements containing CLI and future GUI outputs
    """

    def get_player_input(self, prompt: str) -> str:
        return input(prompt)
    
    def display_message(self, message:str):
        print(message)

def table_str_creator(state: GameState) -> str: 

    if state.current_trick:

        _reversed_stack = reversed(state.current_trick)
        string = ""

        for player, card in _reversed_stack:
            if len(id_to_initials(card)) >= 3:
                    string += f"{id_to_prose(card)}   ~  {player}\n"
            else:
                    string += f" {id_to_prose(card)}   ~  {player}\n"
        return f"Table:\n{string}"
    return "(Empty)" 


def display_hand_str(self, card_list: list[CardInt], max_cards: int = 8): # currently the hands are empty
        """
        Displays the user's hand depending on whether the player is an opponent
        
        Args:
            card_list (list[CardInt]): The list of cards to display
            max_cards(int): Maximum amount of cards possible for current round
        """

        if not card_list:
            return ['X' for _ in range(max_cards)]

        # Keeps opponent's hands hidden
        if self.opponent == False:
            return [f"{id_to_prose(card)}" for card in card_list]
        else:
            return ['X' for _ in self.hand]

def player_hand_str_creator(player: PlayerStr, state: GameState) -> str:

    player_hand = state.hands[player]
    max_cards = state.CARDS_PER_ROUND[state.round]
    hand_output = []

    if not player_hand:
        hand_output = ['X' for _ in range(max_cards)]
        return f"Current Hand:\n {hand_output}"

    # Keep opponent's hands hidden
    if player == state.perspective:
        hand_output = [f"{id_to_prose(card)}" for card in state.hands[player]]
    else:
        hand_output = ['X' for _ in player_hand]
    return f"Current Hand:\n {hand_output}"


def CLI_format_hand(hand: set[CardInt], cols = 4) -> str:
        """
        Formats hand into a columns for the CLI readable format
        
        """

        lines = []
        hand_list = list(hand)

        for i in range(0, len(hand), cols):

            chunk = hand_list[i:i+cols]
            row = []


            for idx, card in enumerate(chunk, start=i):
                card_string = id_to_prose(card)
                if len(id_to_initials(card)) < 3:
                     card_string = " " + card_string

                row.append(f"    {idx + 1}) {card_string}")

            lines.append("    ".join(row))
        
        return "\n".join(lines) if lines else '(Hidden)'