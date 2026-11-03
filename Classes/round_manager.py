from Classes.actions import (
    get_bot_bid,
    get_bot_trump_selection,
    get_human_bid,
    get_human_card,
    get_human_hand_assignment,
    get_human_trump_selection,
    get_random_hand_assignment,
    get_random_trump_selection,
)
from Classes.deck import Deck
from Classes.game import GameMode
from Classes.player import Player
from Classes.ui_manager import UIManager
from game_state import GameState
from Utils.constants import CARDS_PER_ROUND
from Utils.types import PlayerStr


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
        self.state = state
        self.setup_round()
        self.select_trump()
        self.run_bidding()
        self.play_round()
        # self.score_round(state) This is already performed in the state, the state after play_round is the latest round score
        self.start_next_round()

    def setup_round(self):
        """Sets up the round by initializing hands, player order, and other necessary state.
        
        Args:
            state (GameState): The current state of the game.
        """

        self._reset_deck()

        # After initial round, reset for new round
        if self.state.round > 1:
            self.state = self.state.get_next_round_state()

        # ASSISTANT MODE HANDLING
        if self.gamemode == GameMode.ASSISTANT:

            # Assign human hand for the perspective player
            self.state.hands[self.state.perspective] = get_human_hand_assignment(
                perspective=self.state.perspective,
                cards_this_round=CARDS_PER_ROUND[self.state.round],
                deck=self.deck).hand         
            self.deck.remove_cards(self.state.hands[self.state.perspective])
            return 
        
        if self.gamemode == GameMode.SINGLE_PLAYER:
            self.ui_manager.print_random_hands_assignment_commencing(round=self.state.round)
        
        # For both single player and sim modes, assign random hands to all players
        for player in self.state.player_order:
            # THOUGHT: Possibly add CLI output alerting the assignment of hands to players
            self.state.hands[player] = get_random_hand_assignment(round=self.state.round,
                                                                deck=self.deck).hand

    def select_trump(self) -> None:

        """Handles the trump selection phase of the round."""

        selected_trump = ''

        if self.gamemode == GameMode.SINGLE_PLAYER or self.gamemode == GameMode.ASSISTANT:
            self.ui_manager.print_trump_phase_commencing(round=self.state.round)
            self.ui_manager.print_player_is_trump_decider(player=self.state.trump_decider, perspective=self.state.perspective)

        # Always randomise the trump selection for the first round
        if self.state.round == 1:
            selected_trump = get_random_trump_selection().trump
        elif (self.gamemode == GameMode.SINGLE_PLAYER and 
            self.state.trump_decider == self.state.perspective) or (
            self.gamemode == GameMode.ASSISTANT):
            selected_trump = get_human_trump_selection(round=self.state.round,
                                                        player_name=self.state.trump_decider).trump
        else:
            selected_trump = get_bot_trump_selection(
                chosen_player=self.player_map[self.state.trump_decider]).trump

        if self.gamemode == GameMode.SINGLE_PLAYER or self.gamemode == GameMode.ASSISTANT:
            self.ui_manager.print_player_selects_trump(player=self.state.trump_decider, trump=selected_trump)
        self.state.trump_suit = selected_trump

    def run_bidding(self):
        """Handles the bidding phase of the round."""

        if self.gamemode == GameMode.SINGLE_PLAYER or self.gamemode == GameMode.ASSISTANT:
            self.ui_manager.print_opening_bidding_round_statement(round=self.state.round)

        for player in self.state.player_order:
            restricted_bid = self._get_restricted_bid(self.state.bids,
                                                      CARDS_PER_ROUND[self.state.round],
                                                      player_amount=len(self.state.player_order))

            if self.gamemode == GameMode.SIMULATION:
                bid = get_bot_bid(player=self.player_map[player]).bid
                self.state.bids[player] = bid
                continue

            # Handle bidding for the current player based on the game mode and player type.
            if self.gamemode == GameMode.ASSISTANT or \
            (self.gamemode == GameMode.SINGLE_PLAYER and player == self.state.perspective):
                bid = get_human_bid(player_name=player,
                                    state=self.state,
                                    restricted_bid=restricted_bid).bid
            else:
                self.ui_manager.print_bot_bid_turn(player=player)
                bid = self.player_map[player].choose_bid()

            self.state.bids[player] = bid
            self.ui_manager.print_chosen_bid(player=player, bid=bid)
    
    def play_round(self):

        """Handles the playing phase of the round, where players play their cards."""

        max_cards_this_round = CARDS_PER_ROUND[self.state.round]

        # Loop through the number of cards in the round, as each player will play one card per trick
        # Assumes all the players start with the same amount of cards
        for _ in range(max_cards_this_round):
            self._play_trick()

    def score_round(self):
        """Calculates and updates scores based on the results of the round."""
        # Implementation for scoring the round goes here
        pass

    def start_next_round(self):
        """Prepares the game state for the next round."""
        self.ui_manager.print_total_score(self.state)
        self.state = self.state.get_next_round_state()

    def _play_trick(self) -> None:

        """Plays out a single trick within the round."""

        for _ in range(len(self.state.player_order)):
            player = self.state.next_player()

            if self.gamemode == GameMode.SIMULATION: 
                card_selected = self.player_map[player].choose_card()  # THOUGHT: The player will probably need the updated state
                # to be able to update their belief model and make an educated decision.
            
            elif self.gamemode == GameMode.SINGLE_PLAYER:
                if player == self.state.perspective:
                    card_selected = get_human_card(player_name=player,
                                                state=self.state).card
                else:
                    card_selected = self.player_map[player].choose_card()
                    self.ui_manager.print_player_card_selection(choice=card_selected,
                                                                player=player)
                          
            elif self.gamemode == GameMode.ASSISTANT:
                card_selected = get_human_card(player_name=player, state=self.state).card

            else:
                raise ValueError(f"Unsupported game mode: {self.gamemode}")

            # Apply move for player regardless of gamemode
            self.state = self.state.apply_move(
                player=player,
                card=card_selected)

    def _get_restricted_bid(self, bids: dict[PlayerStr, int], max_cards: int, player_amount: int) -> int:
        """Determines the restricted bid for the current player based on the game rules.
        Should have probably gone in biddingManager but it is sufficient here for now."""

        bid_total = sum(bids.values())
        if len(bids) == player_amount - 1:
            restricted_bid = max_cards - bid_total
        else:
            restricted_bid = -1
        return restricted_bid
    
    def _reset_deck(self) -> None:
        """Resets the deck to a full set of cards."""
        self.deck = Deck()