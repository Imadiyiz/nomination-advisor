import random

from game_engine import GameState

CardStr = str
PlayerStr = str
TrumpStr = str


class RolloutSimulator:
    """
    Simulates the actions within a rollout applying moves in logical order
    """
    def __init__(self, state: GameState):
        # local mutable copy
        self.state = state

    def rollout_round(self) -> dict[PlayerStr, int]:
        """
        Players play random moves until they run out of moves and the round terminates.
        Returns the scores from the round
        
        """
        self.state.winner = ''  # Reset winner to ensure the trick is not considered complete at the start
        while not self.state.is_terminal():
            
            player = self.state.next_player()
            legal_moves = self.state.get_legal_moves(player)
            if not tuple(legal_moves):
                raise ValueError("There is a duplicate card in play, please check assigned cards")
            move = random.choice(tuple(legal_moves))

            self.state = self.state.apply_move(player, move)

        return self.state.round_scores

    def rollout_trick(self, perspective: PlayerStr, chosen_card: CardStr) -> PlayerStr:

        """
        Similar to rollout round however, it terminates after finishing a trick
        """

        self.winner = '' # reset winner before new one is assigned
        while not self.state.is_terminal(round=False):
            player = self.state.next_player()
            legal_moves = self.state.get_legal_moves(player) # The real truth

            if not tuple(legal_moves):
                    raise ValueError("There is a duplicate card in play, please check assigned cards RT")

            # Perspective plays chosen card, others play random legal cards
            if player == perspective:
                move = chosen_card
            else:
                move = random.choice(tuple(legal_moves))

            self.state = self.state.apply_move(player, move)

        return self.state.winner      