# Contents of the UIManager python file
from game_state import GameState
from Utils.card_serialization import id_to_prose, id_to_initials
from Utils.types import PlayerStr, CardInt, TrumpStr


class UIManager:
    """
    Manages UI elements containing CLI and future GUI outputs
    """

    def get_player_input(self, prompt: str) -> str:
        return input(prompt)
    
    def display_message(self, message:str):
        print(message)

    def game_over_message(self, state: GameState):
        """
        Displays the game over message with the final scores and winner

        Args:
            state (GameState): The current game state object
        """

        final_scores = state.total_scores
        winning_score = max(final_scores.values())

        winning_players = [player for player in state.player_order
                           if final_scores[player] == winning_score]

        if len(winning_players) > 1:
            print(f"Game Over:\n There is a draw. The winners are {" ,".join(winning_players)} with a score of {winning_score}")
        else:
            print(f"Game Over!\n The winner is {winning_players[0]} with a score of {winning_score}!")

        print("\nFinal Scoreboard: ", scoreboard_display(state=state, round=False))


    def print_opening_bidding_round_statement(self, state: GameState):
         max_cards = state.CARDS_PER_ROUND[state.round - 1]
         print(f"ROUND {state.round} - Bidding Phase ({max_cards} cards per hand)\n")

    def print_random_trump_confirmation(self, state: GameState, trump_card: TrumpStr):
        print(f"Random trump card - {trump_card}")
        print("Trump suit: ", state.trump_suit)

    def print_trump_initials_error(self, choice_of_initials: str):
        """Receives card initials and prints error statement"""
        print(f"{choice_of_initials} has already been used and is no longer in the deck")

    def print_chosen_card(self, chosen_card: CardInt):
        print(chosen_card, "chosen card")

    def print_initials_choice_error(self, choice_of_initials: str):
        print(f"{choice_of_initials} is no longer in the deck")

    def print_player_decides_trump(self, player: PlayerStr):
        print(f"""{player} determines trump for next round""")

    def print_total_score(self, state: GameState):
        """"""
        print("Total score: ", scoreboard_display(state, round=False))

    def print_choice_made(self, choice: CardInt):
        print("choice", id_to_initials(choice))

    def print_player_choice_made(self, player: PlayerStr, choice: CardInt):
        print(f"{player} selected card", id_to_initials(choice))

    def print_perspective_choice_made(self, choice: CardInt):
        print("You selected card ", id_to_initials(choice))

    def print_invalid_choice_not_in_deck(self, choice: CardInt):
        print(f"invalid card input, {id_to_initials(choice)} is not longer in the deck")

    def print_invalid_choice_not_in_hand(self, choice: CardInt):
        print(f"Invalid card choice, {id_to_initials(choice)} is not in your hand")

    def print_invalid_choice_not_legal(self, choice: CardInt):
        print(f"Invalid card choice, {id_to_initials(choice)} is not a legal move")

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

def scoreboard_display(state: GameState, round: bool = False) -> str:
        """
        Function for outputting the scores in the game

        Args:
            Round (bool): True by default and determines whether the display should be the 
            round scoreboard or total scoreboard 

        Returns:
            List: Formatted and sorted version of the scoreboard for readability 
        """

        scoreboard = state.round_scores if round else state.total_scores

        formatted_scoreboard = sorted(
                    scoreboard.items(), 
                    key= lambda x:x[1], #sort by the second element of each function
                    reverse = True
                )

        return " | ".join([
                f"{name} {score} ({state.bids[name]})" 
                for name, score in formatted_scoreboard
            ]
    
            ) if round else " | ".join([
                f"{name} {score}" 
                for name, score in formatted_scoreboard
            ]
    
            )