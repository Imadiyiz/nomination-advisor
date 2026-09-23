# Defines various actions that players can take in the game, represented as dataclasses.

from dataclasses import dataclass
from Classes.iterative_trump_flow import IterativeTrumpFlow
from Classes.local_card_assignment_flow import LocalCardAssignmentFlow
from Classes.manual_trump_selection_flow import ManualTrumpSelectionFlow
from Classes.player import Player
self.iterativeTrumpFlow = IterativeTrumpFlow()
from Classes.deck import Deck
from Utils.cli_tools import clear_screen
from Utils.constants import VALID_CARD_INITIALS, CARDS_PER_ROUND
from Utils.types import CardInt, PlayerStr, TrumpStr
from typing import Union
from Utils.helpers import initials_to_id
from enum import Enum
from Classes.ui_manager import UIManager
import random
from Utils.cli_tools import clear_screen

class ActionType(Enum):
    ASSIGN_RANDOM_HAND = 1
    ASSIGN_HUMAN_HAND = 2
    ASSIGN_BID = 3
    ASSIGN_TRUMP = 4
    PLAY_CARD = 5

@dataclass
class BidAction:
    bid: int

@dataclass
class TrumpAction:
    trump: CardInt

@dataclass
class PlayCardAction:
    card: CardInt

@dataclass
class HandAssignmentAction:
    hand: list[CardInt]

ActionT = Union[BidAction, TrumpAction, PlayCardAction, HandAssignmentAction]


def get_human_hand_assignment(perspective: PlayerStr, 
                              cards_this_round: int, 
                              deck: Deck,
                              ) -> set[CardInt]:
    """
    Prompts the human player to assign their hand for the current round.

    Args:
        perspective (PlayerStr): The player for whom the hand is being assigned.
        cards_this_round (int): The number of cards to be assigned for this round.
        deck (Deck): The deck from which cards are drawn.

    Returns:
        set[CardInt]: The set of cards assigned to the player. (Sanitized and validated against the deck)
    """
    local_card_assignment_flow = LocalCardAssignmentFlow(valid_card_initials=VALID_CARD_INITIALS)
    local_card_assignment_flow.generate_prompt(perspective)

    current_hand = set()
    while len(current_hand) < cards_this_round:

        choice_of_initials = local_card_assignment_flow.assign_card(
            perspective=perspective,
            player_hand=current_hand,
            max_cards=cards_this_round,
        )

        if not deck.contains(initials_to_id(choice_of_initials)):
                UIManager().print_trump_initials_error(choice_of_initials)
                continue # loops until there is a valid card

        # ACTION: Remove chosen card print out
        selected_card = initials_to_id(choice_of_initials)
        UIManager.print_chosen_card(selected_card)

        if not selected_card:
            UIManager().print_initials_choice_error(choice_of_initials)
        else:
            current_hand.add(selected_card)


    return current_hand

def get_human_trump_selection(round: int) -> TrumpStr:
    """
    Prompts the human player to select a trump card.

    Args:
        round (int): The current round number.

    Returns:
        TrumpStr: The selected trump suit.
    """

    clear_screen() #2
    UIManager().print_opening_bidding_round_statement(round = round)
    return ManualTrumpSelectionFlow().run()

def get_random_trump_selection(round: int) -> TrumpStr:
    """
    Selects a trump suit randomly.

    Returns:
        TrumpStr: The randomly selected trump suit.
    """
    clear_screen() #2
    UIManager().print_opening_bidding_round_statement(round=round)
    random_trump = random.choice(['Clubs', 'Diamonds', 'Hearts', 'Spades'])
    UIManager().print_random_trump_confirmation(trump=random_trump)
    return random_trump

def get_player_trump_selection(chosen_player: Player) -> TrumpStr:
    """
    Prompts the player to select a trump card.

    Args:
        round (int): The current round number.
        chosen_player (Player): The player who is selecting the trump suit.

    Returns:
        TrumpStr: The selected trump suit.
    """

    iterativeTrumpFlow = IterativeTrumpFlow()

    clear_screen() #2
    trump_suit = iterativeTrumpFlow.run(player=chosen_player)['trump_suit']
    return trump_suit