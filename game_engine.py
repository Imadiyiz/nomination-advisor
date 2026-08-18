from dataclasses import dataclass

from Classes.CardClass import Card
from Classes.DeckClass import Deck

CardStr = str
PlayerStr = str
TrumpStr = str

@dataclass()
class GameState:

    """

    Cards stored as ("10D", "3H")
    Suits are stored a 'D', 'S'
    Only the Truth, fully concrete
    Attributes:
        
    """
    
    hands: dict[PlayerStr, set[CardStr]]           # player_id -> cards.initials
    current_trick: tuple[tuple[PlayerStr, CardStr], ...]        # (player_id, card)
    trump_suit: TrumpStr
    player_order: tuple[PlayerStr, ...]   # fixed seating order
    round_scores: dict[PlayerStr, int]
    bids: dict[PlayerStr, int]
    cards_remaining: int
    winner: PlayerStr = ''              # Winner of the previous trick

    # Private attribute
    _leader: PlayerStr = ''              


    # Class constants
    valid_initials = Deck().generate_valid_card_initials()

    def __post_init__(self):
        if not self._leader:
            self._leader = self._get_leader(self.player_order, self.current_trick)

    # must be used to avoid generating inaccurate worlds
    def _get_leader(self, players: tuple, current_trick: tuple) -> str:
        """
        Returns a valid leader given the current trick restraints
        """

        if self._leader:
            return self._leader
        
        if not current_trick:
            return players[0]
        leader = current_trick[0][0]

        if leader not in players:
            raise RuntimeError("The player who played the first trump card has not been registered")
        return leader

    def _get_turn_order(self) -> tuple[PlayerStr, ...]:
        """Returns player order based on game leader's pos index """

        start_index = self.player_order.index(self._leader)

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
        enforces follow-suit and respects trump rules
        
        :returns set of legal moves
        """

        player_hand = self.hands[player] 

        if not self.current_trick:
            return set(player_hand)

        lead_suit = self.current_trick[0][1][-1]
        
        follow_cards = {card for card in player_hand 
                        if card[-1] == lead_suit
        }
        
        if follow_cards:
            return set(follow_cards) 
        else:
            # if no legal moves, any card can be discarded
            return set(player_hand)
    
    def apply_move(self, player: PlayerStr, card: CardStr) -> "GameState":
        """
        Returns a NEW GameState after move
        """

        # Initially there isn't a winner
        winner = ''

        if card not in self.get_legal_moves(player):
            print("")
            print(f"Illegal move attempted by {player}: {card}")
            print(f"Player's hand: {self.hands[player]}")
            print(f"Current trick: {self.current_trick}")
            print(f"legal moves: {self.get_legal_moves(player)}")
            raise ValueError("Illegal move - Check world status")
        

        new_hands = {
            p: (cards - {card}) if p == player else cards
            for p, cards in self.hands.items()
        }

        new_scores = dict(self.round_scores)

        new_trick = self.current_trick + ((player, card),)

        new_leader = self._leader
        new_cards_remaining = self.cards_remaining

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
            _leader=new_leader,
            trump_suit=self.trump_suit,
            player_order= self.player_order,
            round_scores=new_scores,
            cards_remaining=new_cards_remaining,
            bids=dict(self.bids), 
            winner = winner
        )


    def _resolve_trick(
            self, trick: tuple[tuple[PlayerStr, CardStr], ...]
    ) -> PlayerStr:
        
        """ Returns player who wins the trick"""
        
        lead_suit = trick[0][1][-1]

        def _card_value(card_str: CardStr) -> int:
            rank, _ = Card.from_initials(card_str) 
            picture_to_rank = {"J": 11, "Q": 12, "K": 13, "A": 14}
            
            if rank.isnumeric():
                return int(rank)
                
            return picture_to_rank[rank]
        
        # trump suit evaluation
        trump_cards = [
            (player, card) for player, card in trick
            if card[-1] == self.trump_suit
        ]

        if trump_cards:
            return max(trump_cards, key = lambda tc: _card_value(tc[1]))[0]
        
        # Lead suit evaluation
        lead_cards = [
            (p, c) for p, c in trick if c[-1] == lead_suit
        ]

        return max(lead_cards, key=lambda lc: _card_value(lc[1]))[0]

    
    def is_terminal(self, round = True) -> bool:
        """
        round or trick is terminal
        """

        # Terminal state if there are no cards remaining in play 
        if round == True:
            return self.cards_remaining == 0


        # Terminal state if a winner has been declared
        return self.winner != '' and round == False              