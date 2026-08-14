import random
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
    leader: PlayerStr                     # player_id whose turn it is
    trump_suit: TrumpStr
    player_order: tuple[PlayerStr, ...]   # fixed seating order
    round_scores: dict[PlayerStr, int]
    bids: dict[PlayerStr, int]
    cards_remaining: int
    winner: PlayerStr = ''              # Winner of the previous trick


    # Class constants
    valid_initials = Deck().generate_valid_card_initials()

    def _get_turn_order(self) -> tuple[PlayerStr, ...]:
        """Returns player order based on game leader's pos index """
        start_index = self.player_order.index(self.leader)
        print("START INDEX", start_index)

        return (
        self.player_order[start_index:] +
        self.player_order[:start_index]
        )

    def _next_player(self) -> PlayerStr:
        order = self._get_turn_order()
        print("order", order)
        return order[len(self.current_trick)]

    def get_legal_moves(self, player: PlayerStr) -> set[CardStr]:
        """
        Function for identifing legal moves given;
        enforces follow-suit and respects trump rules
        
        :returns set of legal moves
        """

        player_hand = self.hands[player] # hands are null 

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
    
    def _apply_move(self, player: PlayerStr, card: CardStr) -> "GameState":
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
            raise ValueError("Illegal move")
        

        new_hands = {
            p: (cards - {card}) if p == player else cards
            for p, cards in self.hands.items()
        }

        new_scores = dict(self.round_scores)

        new_trick = self.current_trick + ((player, card),)

        new_leader = self.leader
        new_cards_remaining = self.cards_remaining


        print(len(new_trick), len(self.player_order), "DEBUGGING LENGTHS")
        # if trick complete, resolve it
        if len(new_trick) == len(self.player_order):
            winner = self._resolve_trick(new_trick)
            print("Final trick", new_trick, winner)
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
        if round == True:
            return self.cards_remaining == 0

        return self.winner != '' and round == False
    

class RolloutSimulator:

    def __init__(self, state: GameState):
        # local mutable copy
        self.state = state

    def rollout_round(self) -> dict[PlayerStr, int]:

        self.state.winner = ''  # Reset winner to ensure the trick is not considered complete at the start
        while not self.state.is_terminal():
            
            player = self.state._next_player()
            legal_moves = self.state.get_legal_moves(player)
            if not tuple(legal_moves):
                raise ValueError("There is a duplicate card in play, please check assigned cards")
            move = random.choice(tuple(legal_moves))

            self.state = self.state._apply_move(player, move)

        return self.state.round_scores

    def rollout_trick_until_perspective(self, perspective: PlayerStr) -> "set[CardStr]":

        """Completes rollout until it is the perspective player's turn to play, then returns the legal moves for that player. 
        This function does not play the perspective player's move, it only advances the game state to their turn."""

        self.state.winner = ''  # Reset winner to ensure the trick is not considered complete at the start
        while not self.state.is_terminal(round=False):
            print(f"Current trick: {self.state.current_trick} RTUP")  # Debugging statement
            player = self.state._next_player()
            print("Player Turn", player)
            legal_moves = self.state.get_legal_moves(player)
            if not tuple(legal_moves):
                raise ValueError("There is a duplicate card in play, please check assigned cards RTUP")

            # If the current player is the perspective player, return the legal moves for that player
            if player == perspective:
                print("returned legal moves", self.state.get_legal_moves(perspective))
                return self.state.get_legal_moves(perspective)
                # while the player has been skipped, the loop will keep repeating the same player as next_player() gives the same next player as it is based off of the leader
            else:
                move = random.choice(tuple(legal_moves))
                self.state = self.state._apply_move(player, move)


    def rollout_trick(self, perspective: PlayerStr, chosen_card: CardStr) -> PlayerStr:

        """
        Similar to rollout round however, it terminates after finishing a trick
        """

        while not self.state.is_terminal(round=False):
            print(f"Current trick: {self.state.current_trick} RT")  # Debugging statement
            player = self.state._next_player()
            legal_moves = self.state.get_legal_moves(player) # The real truth
            print(f"Legal moves for {player}: {legal_moves} DEBUG RT")  # Debugging statement

            if not tuple(legal_moves):
                    raise ValueError("There is a duplicate card in play, please check assigned cards RT")

            # Perspective plays chosen card, others play random legal cards
            if player == perspective:
                move = chosen_card
                self.state = self.state._apply_move(player, move)
            # Determine if the player has already played a card in the current trick
            elif any(play[0] == player for play in self.state.current_trick):
                continue  # Skip this player if they have already played
            else:
                move = random.choice(tuple(legal_moves))
                self.state = self.state._apply_move(player, move)

        print("Returned winner:", self.state.winner)  # Debugging statement
        return self.state.winner                    




### It never reduces the cards remaining when there are already items in the trick.
""" 
To solve this I will need to do checks before making any evaluations.
The check should iterate through the cards and should remove hand length from AI player, although this won't make a difference
since everything is reset once the trick is over. The check should iterate through the cards and omit them from having a turn, but in trutth
there shouldn't be a player able to play a card after the perspective player if they have ALREADY played their card.

11/08/2026

Currently the legal moves function is not getting called and the card manually input into the trick is still in the deck

"""