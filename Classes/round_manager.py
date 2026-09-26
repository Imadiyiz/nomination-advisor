from Classes.game import GameMode
from Classes.ui_manager import UIManager
from Tests.test_Steps import player
from Utils.types import PlayerStr
from Classes.player import Player
from actions import (
    get_bot_trump_selection,
    get_human_hand_assignment, 
    get_random_trump_selection, 
    get_human_trump_selection, 
    get_human_bid,
    get_random_hand_assignment,
    get_bot_bid,
    get_human_card,
)

from Classes.deck import Deck
from game_state import GameState
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
        self.deck = Deck()
        self.player_map = player_map
        self.gamemode = gamemode
        self.ui_manager = UIManager()

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
        
        Args:
            state (GameState): The current state of the game.
        """

        self._reset_deck()

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
            ).hand
            return 
        
        if self.gamemode == GameMode.SINGLE_PLAYER:
            self.ui_manager.print__random_hands_assignment_commencing(round=state.round)
        
        # For both single player and sim modes, assign random hands to all players
        for player in state.player_order:
            # THOUGHT: Possibly add CLI output alerting the assignment of hands to players
            state.hands[player] = get_random_hand_assignment(round=state.round,
                                                                deck=self.deck).hand



    def select_trump(self, state: GameState) -> None:

        """Handles the trump selection phase of the round."""

        selected_trump = ''

        if self.gamemode == GameMode.SINGLE_PLAYER or self.gamemode == GameMode.ASSISTANT:
            self.ui_manager.print_trump_phase_commencing(round=state.round)
            self.ui_manager.print_player_is_trump_decider(player=state.trump_decider, perspective=state.perspective)

        # Always randomise the trump selection for the first round
        if state.round == 1:
            selected_trump = get_random_trump_selection().trump
        elif (self.gamemode == GameMode.SINGLE_PLAYER and 
            state.trump_decider == state.perspective) or (
            self.gamemode == GameMode.ASSISTANT):
            selected_trump = get_human_trump_selection(round=state.round,
                                                        player_name=state.trump_decider).trump
        else:
            selected_trump = get_bot_trump_selection(
                chosen_player=self.player_map[state.trump_decider]).trump

        if self.gamemode == GameMode.SINGLE_PLAYER or self.gamemode == GameMode.ASSISTANT:
            self.ui_manager.print_player_selects_trump(player=state.trump_decider, trump=selected_trump)
        state.trump_suit = selected_trump

    def run_bidding(self, state: GameState):
        """Handles the bidding phase of the round."""

        if self.gamemode == GameMode.SINGLE_PLAYER or self.gamemode == GameMode.ASSISTANT:
            self.ui_manager.print_opening_bidding_round_statement(round=state.round)

        for player in state.player_order:
            restricted_bid = self._get_restricted_bid(state.bids, CARDS_PER_ROUND[state.round])

            if self.gamemode == GameMode.SIMULATION:
                bid = get_bot_bid(player=self.player_map[player]).bid
                state.bids[player] = bid
                continue

            # Handle bidding for the current player based on the game mode and player type.
            if self.gamemode == GameMode.ASSISTANT or \
            (self.gamemode == GameMode.SINGLE_PLAYER and player == state.perspective):
                bid = get_human_bid(player_name=player,
                                    state=state,
                                    restricted_bid=restricted_bid).bid
            else:
                self.ui_manager.print_bot_bid_turn(player=player)
                bid = self.player_map[player].choose_bid()

            state.bids[player] = bid
            self.ui_manager.print_chosen_bid(player=player, bid=bid)
    
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

        max_cards_this_round = CARDS_PER_ROUND[self.state.round]

        if self.gamemode == GameMode.SIMULATION:
            for _ in range(max_cards_this_round):
                player = self.state.next_player()
                card_selected = self.player_map[player].choose_card(self.state)
                self.state = self.state.apply_move(
                    player=player,
                    card=card_selected
                )
            return
        
        elif self.gamemode == GameMode.SINGLE_PLAYER:
            for _ in range(max_cards_this_round):
                player = self.state.next_player()

                if player == self.state.perspective:
                    card_selected = get_human_card(player_name=player,
                                                   state=self.state,
                                                   perspective=self.state.perspective).card
                else:
                    card_selected = self.player_map[player].choose_card()
                    self.ui_manager.print_player_card_selection(choice=card_selected,
                                                                player=player)
                    self.state = self.state.apply_move(
                        player=player,
                        card=card_selected
                    )
            return      
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
    
    def _reset_deck(self) -> None:
        """Resets the deck to a full set of cards."""
        self.deck = Deck()