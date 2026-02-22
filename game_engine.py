from dataclasses import dataclass
from typing import Dict, List
from Classes.DeckClass import Deck
from Classes.CardClass import Card
from belief_model import BeliefModel
import random

@dataclass
class GameState():

    """

    Cards stored as ("10D", "3H")
    Suits are stored a 'D', 'S'
    Only the Truth
    Attributes:
        
    """
    
    #Cards 

    hands: Dict[str, set[str]]           # player_id -> cards.initials
    played_cards: Dict[str, set[str]] # player_id, [cards.initials]
    current_trick: List[str]        # (player_id, card)

    # Game structure
    leader: str                     # player_id whose turn it is
    trump_suit: str
    player_order: List[str]         # fixed seating order

    # Scores
    round_scores = Dict[str, int]
    bids: Dict[str, int]

    # Trick tracking
    cards_remaining: int

    # Class constants
    valid_initials = Deck().generate_valid_card_initials()

    def get_legal_moves(self, player: str, void_suits: dict[str, set]) -> set:
        """
        Function for identifing legal moves given;
        it enforces follow-suit
        respects trump rules
        respects void knowledge
        
        :returns set of legal moves
        """

        legal_moves = set()
        first_card = self.current_trick[0]
        first_card_suit = Card.from_initials(first_card)

        for card in self.hands[player]:

            card_suit = Card.from_initials(card)[1]

            # trump suits are always allowed
            if card_suit == self.trump_suit:
                legal_moves.add(card)
                continue
        
            # must follow first suit
            if card_suit == first_card_suit:
                legal_moves.add(card)
                continue

            # is allowed if suit is void due to lack of cards
            if first_card_suit in void_suits[player]:
                legal_moves.add(card)
                continue

        return legal_moves




@dataclass
class SimulationState(GameState):

    """

    Cards stored as ("10", "D")
    Suits are stored a 'D', 'S'
    Attributes:
        
    """

    def init_round(self,
                   hands: Dict[str, str],
                   player_order: List[str],
                   trump_suit: str,
                   bids: Dict[str, int],
                   cards_remaining):
        
        """
        Initialises the round ready to be simulated
        """

        self.unknown_cards = self.valid_initials

        self.current_trick = []
        self.player_order = player_order
        self.leader = player_order[0]
        self.trump_suit = trump_suit
        self.hands = hands
        self.bids = bids
        self.cards_remaining = cards_remaining

        #resets the played cards dictionary and round scores
        for player in self.player_order:
            self.played_cards[player] = set()
            self.round_scores[player] = 0
            self.unknown_cards -= self.hands[player]
        
    def sim_round(self):

        while self.cards_remaining != 0:

            for player in self.player_order:
                self.leader = player
                legal_moves = self.get_legal_moves(self.leader)
                chosen_move = random.choice(legal_moves)
                self._apply_move(chosen_move)

            self.cards_remaining -=1
            winning_player = self._verify_winner()

    def _apply_move(self, card: str):

        self.current_trick.append(card)
        self.played_cards[self.leader].add(card)
        self.unknown_cards -= card
        self.hands[self.leader] -= card

                
    def _verify_winner(self) -> str:
        """
        Rules:
        1. Trump suit beats all other suits
        2. If no trump is played, highest card of the leading suit wins

        returns winning players id
        """

        if not self.current_trick:
            raise ValueError("No trick")
        
        suits_in_current_trick = set(
            card[-1] for card in self.current_trick
        )

        if self.trump_suit in suits_in_current_trick:

            possible_winning_cards = self._remove_cards_via_suit(
                set(self.current_trick),
                self.trump_suit
            )

            winning_card = max(possible_winning_cards, key=lambda c: int(Card.from_initials(c)[0]))
        else:

            first_card_suit = self.current_trick[0][-1]
            possible_winning_cards = self._remove_cards_via_suit(
                set(self.current_trick),
                first_card_suit)
            
            winning_card = max(possible_winning_cards, key=lambda c: int(Card.from_initials(c)[0]))

        
        # determines who played the winning card returns winner
        for card, index in enumerate(self.current_trick):
            if card == winning_card:
                return self.player_order[index]

        raise ValueError("No winning card in trick")
    
    def _remove_cards_via_suit(self, card_set: set, valid_suit: str)-> set:
        """
        Removes cards from card set which are not the valid suit

        returns valid cards in a set
        """

        for card in card_set:

            card_suit = card[-1]
            if card_suit != valid_suit:
                card_set.remove(card)

        return card_set