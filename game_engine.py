from dataclasses import dataclass
from typing import Dict, List, Tuple, Set
from Classes.DeckClass import Deck
from Classes.CardClass import Card
from belief_model import BeliefModel
import random

CardStr = str
PlayerStr = str
TrumpStr = str

@dataclass()
class GameState():

    """

    Cards stored as ("10D", "3H")
    Suits are stored a 'D', 'S'
    Only the Truth, fully concrete
    Attributes:
        
    """
    
    #Cards 

    hands: Tuple[Tuple[PlayerStr, set[CardStr]], ...]           # player_id -> cards.initials
    current_trick: Tuple[Tuple[PlayerStr, CardStr], ...]        # (player_id, card)
    leader: PlayerStr                     # player_id whose turn it is
    trump_suit: TrumpStr
    player_order: Tuple[PlayerStr, ...]         # fixed seating order
    round_scores: Dict[PlayerStr, int]
    bids: Dict[PlayerStr, int]
    cards_remaining: int

    # Class constants
    valid_initials = Deck().generate_valid_card_initials()

    def _get_turn_order(self) -> tuple[PlayerStr, ...]:
        """Returns player order based on game leader's pos index """
        start_index = self.player_order.index(self.leader)

        return (
        self.player_order[start_index:] +
        self.player_order[:start_index]
    )

    def next_player(self) -> PlayerStr:
        order = self._get_turn_order()
        return order[len(self.current_trick)]

    def get_legal_moves(self, player: PlayerStr) -> set[CardStr]:
        """
        Function for identifing legal moves given;
        it enforces follow-suit
        respects trump rules
        
        :returns set of legal moves
        """

        player_hand = self.hands[player]

        if not self.current_trick:
            return set(player_hand)
        
        lead_suit = self.current_trick[0][1][-1]
        
        follow_cards = {card for card in player_hand 
                        if card[-1] == lead_suit
        }

        trump_cards = {trump_card for trump_card in player_hand
                       if trump_card[-1] == self.trump_suit}
        
        if follow_cards:
            return set(follow_cards) 
        elif trump_cards:
            return set(trump_cards)

        # if no legal moves, any card can be discarded
        return set(player_hand)
    
    def apply_move(self, player: PlayerStr, card: CardStr) -> "GameState":
        """
        Returns a NEW GameState after move
        """

        if card not in self.get_legal_moves(player):
            raise ValueError("Illegal move")
        

        new_hands = {
            p: (cards - {card}) if p == player else cards
            for p, cards in self.hands.items()
        }

        #print("New hands", new_hands)

        new_scores = dict(self.round_scores)
        #print("New scores", new_scores)

        new_trick = self.current_trick + ((player, card),)
        #print("New trick", new_trick)

        new_leader = self.leader
        new_cards_remaining = self.cards_remaining
        #print("New leader", new_leader)
        #print("New cards remaining", new_cards_remaining)


        # if trick complete, resolve it
        if len(new_trick) == len(self.player_order):
            winner = self._resolve_trick(new_trick)
            new_scores[winner] += 1
            new_trick = ()
            new_leader = winner
            new_cards_remaining -= 1


        return GameState(
            hands=new_hands,
            current_trick=new_trick,
            leader=new_leader,
            trump_suit=self.trump_suit,
            player_order= self.player_order,
            round_scores=new_scores,
            cards_remaining=new_cards_remaining,
            bids=dict()
        )


    def _resolve_trick(
            self, trick: Tuple[Tuple[PlayerStr, CardStr], ...]
    ) -> PlayerStr:
        
        """ Returns player who wins the trick"""
        
        lead_suit = trick[0][1][-1]

        def _card_value(card_str: CardStr):
            rank, suit = Card.from_initials(card_str) 
            picture_to_rank = {"J": 11,
             "Q": 12,
             "K": 13,
             "A": 14}
            
            if rank.isnumeric():
                card_value_output = int(rank)
                return card_value_output
            
            return picture_to_rank[rank]
        
        # trump first
        trump_cards = [
            (player, card) for player, card in trick
            if card[-1] == self.trump_suit
        ]

        if trump_cards:
            return max(trump_cards, key = lambda tc: _card_value(tc[1]))[0] ### error here
        
        # Otherwise lead suit, player card
        lead_cards = [
            (p, c) for p, c in trick if c[-1] == lead_suit
        ]

        return max(lead_cards, key=lambda x: _card_value(x[1]))[0]

    
    def is_terminal(self) -> bool:
        return self.cards_remaining == 0





class RolloutSimulator:

    def __init__(self, state: GameState):
        # local mutable copy
        self.state = state

    def rollout(self) -> Dict[PlayerStr, int]:

        state = self.state

        while not state.is_terminal():
            player = state.next_player()
            legal_moves = state.get_legal_moves(player)
            move = random.choice(tuple(legal_moves))

            state = state.apply_move(player, move)

        return state.round_scores
        