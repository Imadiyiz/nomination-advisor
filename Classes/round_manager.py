
from django.db.migrations import state
import random
from Classes.game import GameMode
from Tests.test_Steps import player
from Utils.types import PlayerStr
from Classes.player import Player
from .local_card_assignment_flow import LocalCardAssignmentFlow
from actions import (
    get_bot_trump_selection,
    get_human_hand_assignment, 
    get_random_trump_selection, 
    get_human_trump_selection, 
    get_human_bid)

from Classes.deck import Deck
from game_state import GameState
from .bidding_flow import ManualBiddingFlow
from .manual_trump_selection_flow import ManualTrumpSelectionFlow
from .player_setup_flow import PlayerSetupFlow
from .playing_flow import PlayingFlow
from .trump_selection_type_flow import TrumpSelectionTypeFlow
from Utils.constants import VALID_CARD_INITIALS, CARDS_PER_ROUND

class RoundManager:
    """Manages the flow of a round in the game. Responsible for handling player setup, 
    trump selection, bidding, playing, and scoring phases."""

    def __init__(self, player_map: dict[PlayerStr, Player], gamemode: GameMode):
        """Initializes the round manager with the given player map and game mode.

        Args:
            player_map (dict[PlayerStr, Player]): Mapping of player identifiers to player objects.
            gamemode (GameMode): The current game mode.
        """
        self.deck = None
        self.manual_bidding_flow = ManualBiddingFlow()
        self.manual_trump_selection_flow = ManualTrumpSelectionFlow()
        self.player_setup_flow = PlayerSetupFlow()
        self.playing_flow = PlayingFlow()
        self.trump_selection_type_flow = TrumpSelectionTypeFlow()
        self.player_map = player_map
        self.gamemode = gamemode

    def run(self, state: GameState):
        """Runs a single round of the game, managing the flow from player selection to scoring."""
        self.setup_round(state)
        self.select_trump(state)
        self.run_bidding(state)
        self.play_round(state)
        self.score_round(state)
        self.start_next_round(state)

    def setup_round(self, state: GameState):
        """Sets up the round by initializing hands, player order, and other necessary state.
        
        args:
            state (GameState): The current state of the game.
        """

        self.deck = Deck()

        # After initial round, reset for new round
        if state.round > 1:
            state = state.get_next_round_state()

        # ASSISTANT MODE HANDLING
        if self.gamemode == GameMode.ASSISTANT:

            # Assign human hand for the perspective player
            self.deck.remove_cards(state.hands[state.perspective])
            state.hands[state.perspective] = get_human_hand_assignment(
                perspective=state.perspective,
                cards_this_round=CARDS_PER_ROUND[state.round],
                deck=self.deck,
            )

        elif (self.gamemode == GameMode.SINGLE_PLAYER or 
              self.gamemode == GameMode.SIMULATION):

            # Automatically assign hands to players based on the game mode and player type
            for player in state.player_order:

                hand_sample = random.sample(
                    population=self.deck.cards,
                    k=CARDS_PER_ROUND[state.round],
                )
                state.hands[player] = set(hand_sample)
                self.deck.remove_cards(state.hands[player])
            


    def select_trump(self, state: GameState) -> None:

        """Handles the trump selection phase of the round."""

        selected_trump = ''

        # Trump selection logic based on game mode and round

        # Always randomise the trump selection for the first round
        if state.round == 1:
            selected_trump = get_random_trump_selection(round=state.round)
        elif (self.gamemode == GameMode.SINGLE_PLAYER and 
            state.trump_decider == state.perspective) or (
            self.gamemode == GameMode.ASSISTANT):
            selected_trump = get_human_trump_selection(round=state.round,
                                                        player_name=state.trump_decider)
        else:
            selected_trump = get_bot_trump_selection(
                chosen_player=self.player_map[state.trump_decider])
        state.trump_suit = selected_trump

    def run_bidding(self, state: GameState):
        """Handles the bidding phase of the round."""


        for player in state.player_order:

            restricted_bid = self._get_restricted_bid(state.bids, CARDS_PER_ROUND[state.round])

            # Handle bidding for the current player based on the game mode and player type.
            if self.gamemode == GameMode.ASSISTANT or \
            (self.gamemode == GameMode.SINGLE_PLAYER and player == state.perspective):
                bid = get_human_bid(round=state.round,
                                    player_name=player,
                                    state=state,
                                    restricted_bid=restricted_bid)
            else:
                bid = self.player_map[player].choose_bid()

            state.bids[player] = bid

    
    def play_round(self, state: GameState):

        """Handles the playing phase of the round, where players play their cards."""

        max_cards_this_round = CARDS_PER_ROUND[state.round]

        # Loop through the number of cards in the round, as each player will play one card per trick
        # Assumes all the players start with the same amount of cards
        for _ in range(max_cards_this_round):
            self._play_trick()


    def score_round(self, state: GameState):
        """Calculates and updates scores based on the results of the round."""
        # Implementation for scoring the round goes here
        pass

    def start_next_round(self, state: GameState):
        """Prepares the game state for the next round."""
        # Implementation for starting the next round goes here
        pass

    def _play_trick(self) -> None:

        """Plays out a single trick within the round."""

        self.playingFlow = PlayingFlow()

        for player in self.state.player_order:
            player = self.state.next_player()

            if self.gamemode == GameMode.ASSISTANT:
            action = self.player_map[player].choose_card(self.state)

            self.state = self.state.apply_move(
                player=player,
                card=action,
            )

    def _get_restricted_bid(self, bids: dict[PlayerStr, int], max_cards: int) -> int:
        """Determines the restricted bid for the current player based on the game rules.
        Should have probably gone in biddingManager but it is sufficient here for now."""

        bid_total = sum(bids.values())
        if len(bids) == len(self.state.player_order) - 1:
            restricted_bid = max_cards - bid_total
        else:
            restricted_bid = -1
        return restricted_bid