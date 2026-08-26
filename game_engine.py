from dataclasses import dataclass, field

from Utils.card_tools import *
from Utils.nom_rule_tools import calculate_correct_bid_score
from Utils.types import *

# This GameState class is for showing what the gamestate is after actions occur

# Can get orchestration from rollout round and iterate it 6 times

@dataclass()
class GameState:

    """

    Only the Truth, fully concrete. Responsible for the state of the current game. Is not 
    responsible for facilitating gameplay other than applying moves for rollouts.
    Attributes:
        
    """
    
    hands: dict[PlayerStr, set[CardInt]]           # player_id -> cards.initials
    current_trick: tuple[tuple[PlayerStr, CardInt], ...]        # (player_id, card)
    trump_suit: TrumpStr
    player_order: tuple[PlayerStr, ...]   # fixed seating order
    round_scores: dict[PlayerStr, int]
    total_scores: dict[PlayerStr, int]
    winner: PlayerStr | None = None            # Winner of the previous trick

    # Must use default_factory for when declaring mutable types
    bids: dict[PlayerStr, int]  = field(default_factory=dict)      # Don't always have bids assigned and 
    # Private attribute
    _leader: PlayerStr | None = None

    # must be used to avoid generating inaccurate worlds due to inaccurate ordering
    def _get_leader(self) -> str:
        """
        Returns a valid leader given the current trick restraints
        """

        if self._leader:
            return self._leader

        # Leader is first player in tuple if current trick is empty
        if not self.current_trick:
            return self.player_order[0] 

        # Leader is who played the first card in the trick    
        leader = self.current_trick[0][0] 

        if leader not in self.player_order:
            raise RuntimeError("The player who played the first trump card has not been registered")
        return leader


    def next_player(self) -> PlayerStr:
        """Determines next player to perform play a card. Based on the
        who is the leader."""

        # Need a leader in order to figure who is next
        if not self._leader:
            self._leader = self._get_leader()

        # Tested and works¦
        leader_idx = self.player_order.index(self._leader)
        next_player_idx = max(0, leader_idx + len(self.current_trick) % 
                              len(self.player_order))
        return self.player_order[next_player_idx]

    def get_legal_moves(self, player: PlayerStr) -> set[CardInt]:
        """
        Function for identifing legal moves given;
        enforces follow-suit and respects trump rules
        
        :returns set of legal moves
        """

        player_hand = self.hands[player]

        if not player_hand:
            print("HANDS, ", self.hands.items())
            raise ValueError(f"""
        No Cards in {player}'s hand at all, may not be {player}'s turn.
        DIagnosis:: 
        Bids: {self.bids},
        RS: {self.round_scores},
        TS: {self.total_scores},
        current_trick: {self.current_trick}""")

        if not self.current_trick:
            return set(player_hand)

        lead_suit = get_suit_str(self.current_trick[0][1])
        
        follow_cards = {card for card in player_hand 
                        if get_suit_str(card) == lead_suit
        }
        
        if follow_cards:  # Can not play trumps if in possesion of follow card
            return set(follow_cards) 
        else:
            # if no legal moves, any card can be discarded
            return set(player_hand)
    
    def apply_move(self, player: PlayerStr, card: CardInt) -> "GameState":
        """
        Returns a NEW updated GameState after applying move if the move is legal.
        If the trick has concluded then the scores are updated accordingly
        """

        # Initially there isn't a winner
        winner = None

        # Can not proceed with empty hand
        if not self.hands[player]:
            raise ValueError("No Cards in hand, can not apply move")

        # Card must be in player posession and legal
        if (card not in self.get_legal_moves(player) 
            or card not in self.hands[player]):
            raise ValueError(f"""Illegal move attempted by {player}: {card}")
            Player's hand: {self.hands[player]}
            Current trick: {self.current_trick}
            legal moves: {self.get_legal_moves(player)}
            Check World Constraints""")

        # Declare new parameters for GameState instance being returned
        new_hands = {
            p: (cards - {card}) if p == player else cards
            for p, cards in self.hands.items()
        }
        new_round_scores = dict(self.round_scores)
        new_trick = tuple(self.current_trick + ((player, card),))
        new_leader = self._leader
        new_total_scores = dict(self.total_scores)

        # if trick complete, resolve it
        if len(new_trick) == len(self.player_order):
            winner = self._resolve_trick(new_trick)
            new_round_scores[winner] += 1
            new_trick = ()
            new_leader = winner
            new_total_scores = self._calculate_new_total_score(
                new_hands, new_round_scores)

        return GameState(
            hands=new_hands,
            current_trick=new_trick,
            _leader=new_leader,
            trump_suit=self.trump_suit,
            player_order= self.player_order,
            round_scores=new_round_scores,
            total_scores=new_total_scores,
            bids=dict(self.bids), 
            winner = winner
        )

    def _calculate_new_total_score(self,
        new_hands: dict[PlayerStr, set[CardInt]],
        new_round_scores: dict[PlayerStr, int]) -> dict[PlayerStr, int]:
        """Calcalates the new total score if round has ended and there are valid
        bids available. Returns orignal total scores if this is the case.
        Receives new hands dictionary and the latest round score"""

        # Only update total score if round has finished
        if not self.is_round_terminal(new_hands):
            return self.total_scores

        # Only update total scores if there are bids present
        if not self.bids:
            return self.total_scores

        # Update new total scores depending on whether the player satisifed their bid
        new_total_scores = self.total_scores
        for player, tricks_won in new_round_scores.items():
            if tricks_won == self.bids[player]:
                new_total_scores[player] += calculate_correct_bid_score(tricks_won)
            else:
                new_total_scores[player] += tricks_won  

        return new_total_scores

    def _resolve_trick(
            self, trick: tuple[tuple[PlayerStr, CardInt], ...]) -> PlayerStr:
        """ Returns player who wins the trick"""

        if not trick:
            raise ValueError("Trick is empty, unable to resolve the trick")
        
        lead_suit = get_suit_str(trick[0][1])
        
        # trump suit evaluation
        trump_cards = [
            (player, card) for player, card in trick
            if get_suit_str(card) == self.trump_suit]
        if trump_cards:
            return max(trump_cards, key = lambda tc: get_rank(tc[1]))[0]
        
        # Lead suit evaluation
        lead_cards = [
            (p, c) for p, c in trick if get_suit_str(c) == lead_suit]
        return max(lead_cards, key=lambda lc: get_rank(lc[1]))[0]


    def is_round_terminal(self, new_hand: dict[PlayerStr, set[CardInt]]) -> bool:
        """
        Decides whether the current round has ended, judging by the amount 
        of cards in each players hands in the most recent hand dict. 
        No more cards means the round should be terminated.
        """
        # Terminal state if there are no cards remaining in play
        return sum([len(hand) for hand in new_hand]) == 0
      
    
    def is_trick_terminal(self) -> bool:
        """
        Decides whether the current trick has ended. Terminal state if a winner
        has been declared"""
        return self.winner != None   