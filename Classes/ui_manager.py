# Contents of the UIManager python file
from game_state import GameState
from Utils.card_serialization import id_to_initials, id_to_prose
from Utils.types import CardInt, PlayerStr, TrumpStr

from Utils.constants import CARDS_PER_ROUND

class UIManager:
    """
    Manages UI elements containing CLI and future GUI outputs
    """

    @staticmethod
    def get_custom_player_input(self, prompt: str) -> str:
        return input(prompt)

    @staticmethod
    def display_custom_message(self, message:str):
        print(message)

    @staticmethod
    def print_game_over_message(winning_players: list[str],
                                winning_score: int,
                                state: GameState):
        """
        Displays the game over message with the final scores and winner

        Args:
            winning_players (list[str]): The list of winning players.
            winning_score (int): The winning score.
            state (GameState): The current game state object.
        """

        if len(winning_players) > 1:
            print(f"Game Over:\n There is a draw. The winners are {" ,".join(winning_players)} with a score of {winning_score}")
        else:
            print(f"Game Over!\n The winner is {winning_players[0]} with a score of {winning_score}!")

        print("\nFinal Scoreboard: ", scoreboard_display(state=state, round=False))


    @staticmethod
    def print_opening_bidding_round_statement(round: int):
         max_cards = CARDS_PER_ROUND[round - 1]
         print(f"ROUND {round} - Bidding Phase ({max_cards} cards per hand)\n")

    @staticmethod
    def print_random_trump_confirmation(trump: TrumpStr):
        print("Random trump suit selected: ", trump)

    @staticmethod
    def print_trump_initials_error(choice_of_initials: str):
        """Receives card initials and prints error statement"""
        print(f"{choice_of_initials} has already been used and is no longer in the deck")

    @staticmethod
    def print_chosen_card(chosen_card: CardInt):
        print(id_to_initials(chosen_card), "chosen")

    @staticmethod
    def print_initials_choice_error(choice_of_initials: str):
        print(f"{choice_of_initials} is no longer in the deck")

    @staticmethod
    def print_player_is_trump_decider(
                                   player: PlayerStr,
                                   perspective: PlayerStr = ''):
        """Prints a statement indicating which player decides the trump for the next round.

        Args:
            player (PlayerStr): The player who decides the trump.
            perspective (PlayerStr, optional): The perspective player. Defaults to ''.
        """
        if player:
            print(f"{player} determines trump for next round")
        elif perspective:
            print("You determine trump for next round")

    @staticmethod
    def print_bot_bid_turn(player: PlayerStr):
        print(f"{player}'s turn to bid: ")

    @staticmethod
    def print_total_score(state: GameState): 
        print("Total score: ", scoreboard_display(state, round=False))

    @staticmethod
    def print_player_card_selection(choice: CardInt, player: PlayerStr = '',
                          perspective: PlayerStr = ''):
        """Prints the card choice made by a player or the perspective player.

        Args:
            choice (CardInt): The card that was chosen.
            player (PlayerStr, optional): The player who made the choice. Defaults to ''.
            perspective (PlayerStr, optional): The perspective player who made the choice. Defaults to ''.
        """
        if player:
            print(f"{player} selected card: ", id_to_initials(choice))
        elif perspective:
            print("You selected card: ", id_to_initials(choice))
        else:
            print("choice", id_to_initials(choice))

    @staticmethod
    def print_invalid_choice_not_in_deck(choice: CardInt):
        print(f"invalid card input, {id_to_initials(choice)} is not longer in the deck")

    @staticmethod
    def print_invalid_choice_not_in_hand(choice: CardInt):
        print(f"Invalid card choice, {id_to_initials(choice)} is not in your hand")

    @staticmethod
    def print_invalid_choice_not_legal(choice: CardInt):
        print(f"Invalid card choice, {id_to_initials(choice)} is not a legal move")
    
    @staticmethod
    def print_playing_phase_commencing(round: int):
        print(f"Playing Phase Commencing for Round {round}\n")
    
    @staticmethod
    def print__random_hands_assignment_commencing(round: int):
        print(f"random hands assignment commencing for Round {round}\n")

    @staticmethod
    def print_trump_phase_commencing(round: int):
        print(f"Trump Phase Commencing for Round {round}\n")

    @staticmethod
    def print_player_selects_trump(player: PlayerStr, trump: str):
        print(f"Trump selected: {trump}")

    @staticmethod
    def print_determine_initial_trump_suit():
        print("Determine Initial Trump Suit")

    @staticmethod
    def print_chosen_bid(player: PlayerStr, bid: int):
        print(f"{player} chose bid: {bid}")

    
@staticmethod
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

    
@staticmethod
def display_hand_str(
                     player_hand: set[CardInt],
                     max_cards: int,
                     perspective: PlayerStr = '',):
        """
        Displays the user's hand depending on whether the player is an opponent
        
        Args:
            card_list (list[CardInt]): The list of cards to display
            max_cards(int): Maximum amount of cards possible for current round
        """

        card_list = list(player_hand)

        if not card_list:
            return ['X' for _ in range(max_cards)]

        # Keeps opponent's hands hidden
        if perspective:
            return [f"{id_to_prose(card)}" for card in card_list]
        else:
            return ['X' for _ in card_list]

@staticmethod
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


@staticmethod
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

@staticmethod
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