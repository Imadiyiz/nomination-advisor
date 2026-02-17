from dataclasses import dataclass
from typing import Dict, List
from Classes.DeckClass import Deck
from Classes.CardClass import Card



@dataclass
class SimulationState(GameState):

    """

    Cards stored as ("10", "D")
    Suits are stored a 'D', 'S'
    Attributes:
        
    """
    
    #Cards 

    hands: Dict[str, str]           # player_id -> cards.initials
    played_cards: Dict[str, set[str]] # player_id, [cards.initials]
    void_suits: Dict[str, set[str]] # player_id, set(suit)
    unknown_cards: set[str]        # cards not yet assigned
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



@dataclass
class GameState():

    """

    Cards stored as ("10", "D")
    Suits are stored a 'D', 'S'
    Attributes:
        
    """
    
    #Cards 

    hands: Dict[str, str]           # player_id -> cards.initials
    played_cards: Dict[str, set[str]] # player_id, [cards.initials]
    void_suits: Dict[str, set[str]] # player_id, set(suit)
    unknown_cards: set[str]        # cards not yet assigned
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

    def get_legal_moves(self, player: str, state: SimulationState) -> set:
        """
        Function for identifing legal moves given 
        it enforces follow-suit
        respects trump rules
        respects void knowledge
        
        :param player: Description
        :param state: Description
        """

        legal_moves = set()
        first_card = self.current_trick[0]
        first_card_suit = Card().from_initials(first_card)

        for card in self.unknown_cards:

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
            if first_card_suit in self.void_suits[player]:
                legal_moves.add(card)
                continue

        return legal_moves


    




    