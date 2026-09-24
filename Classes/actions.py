# Defines various actions that players can take in the game, represented as dataclasses.

import random
from dataclasses import dataclass
from enum import Enum

from Classes.bidding_flow import ManualBiddingFlow
from Classes.deck import Deck
from Classes.local_card_assignment_flow import LocalCardAssignmentFlow
from Classes.manual_trump_selection_flow import ManualTrumpSelectionFlow
from Classes.player import Player
from Classes.ui_manager import UIManager
from game_state import GameState
from Utils.card_serialization import initials_to_id
from Utils.cli_tools import clear_screen
from Utils.constants import CARDS_PER_ROUND, VALID_CARD_INITIALS
from Utils.types import CardInt, PlayerStr, TrumpStr


class ActionType(Enum):
    ASSIGN_RANDOM_HAND = 1
    ASSIGN_HUMAN_HAND = 2
    ASSIGN_BID = 3
    ASSIGN_TRUMP = 4
    PLAY_CARD = 5

@dataclass
class BidAction:
    bid: int

    def __str__(self) -> str:
        return f"Bid({self.bid})"

@dataclass
class TrumpAction:
    trump: TrumpStr

    def __str__(self) -> str:
        return f"TrumpSelected({self.trump})"

@dataclass
class PlayCardAction:
    card: CardInt

    def __str__(self) -> str:
        return f"PlayCard({self.card})"

@dataclass
class HandAssignmentAction:
    hand: set[CardInt]

    def __str__(self) -> str:
        return f"HandAssignment({self.hand})"

ActionT = BidAction | TrumpAction | PlayCardAction | HandAssignmentAction


def get_human_hand_assignment(perspective: PlayerStr, 
                              cards_this_round: int, 
                              deck: Deck,
                              ) -> HandAssignmentAction:
    """
    Prompts the human player to assign their hand for the current round.

    Args:
        perspective (PlayerStr): The player for whom the hand is being assigned.
        cards_this_round (int): The number of cards to be assigned for this round.
        deck (Deck): The deck from which cards are drawn.

    Returns:
        HandAssignmentAction: The action representing the set of cards assigned to the player. (Sanitized and validated against the deck)
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
        UIManager().print_chosen_card(selected_card)

        if not selected_card:
            UIManager().print_initials_choice_error(choice_of_initials)
        else:
            current_hand.add(selected_card)


    return HandAssignmentAction(hand=current_hand)

def get_human_trump_selection(round: int, player_name: PlayerStr) -> TrumpAction:
    """
    Prompts the human player to select a trump card.

    Args:
        round (int): The current round number.
        player_name (PlayerStr): The name of the player selecting the trump suit.

    Returns:
        TrumpAction: The selected trump suit.
    """

    clear_screen() #2
    UIManager().print_opening_bidding_round_statement(round = round)
    trump_suit = ManualTrumpSelectionFlow().run(player_name=player_name)
    return TrumpAction(trump=trump_suit)

def get_random_trump_selection(round: int) -> TrumpAction:
    """
    Selects a trump suit randomly.

    Args:
        round (int): The current round number.

    Returns:
        TrumpAction: The randomly selected trump suit.
    """
    clear_screen() #2
    UIManager().print_opening_bidding_round_statement(round=round)
    random_trump = random.choice(['Clubs', 'Diamonds', 'Hearts', 'Spades'])
    UIManager().print_random_trump_confirmation(trump=random_trump)
    return TrumpAction(trump=random_trump)

def get_bot_trump_selection(chosen_player: Player) -> TrumpAction:
    """
    Automatically selects a trump card for the bot player.

    Args:
        chosen_player (Player): The player who is selecting the trump suit.

    Returns:
        TrumpAction: The selected trump suit.
    """

    clear_screen() #2
    trump_suit = chosen_player.choose_trump_suit()
    return TrumpAction(trump=trump_suit)

def get_human_bid(round: int, player_name: PlayerStr, state: GameState, restricted_bid: int) -> BidAction:
    """
    Prompts the human player to place a bid.

    Args:
        round (int): The current round number.
        player_name (PlayerStr): The name of the player placing the bid.
        state (GameState): The current state of the game.
        restricted_bid (int): The restricted bid value, if any.

    Returns:
        BidAction: The bid placed by the human player.
    """

    clear_screen() #2
    UIManager().print_bidding_phase_commencing(round=round)
    bid = ManualBiddingFlow().run(player=player_name, state=state, restricted_bid=restricted_bid)
    return BidAction(bid=bid)
