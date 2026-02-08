# functions for the ViewFormat Class
from Classes.CardClass import Card

def format_hand(hand: list[Card], cols=4):
        """
        Formats hand into a readable format
        
        """

        lines = []
        for i in range(0, len(hand), cols):

            chunk = hand[i:i+cols]

            line = "    ".join(
                f"{idx+1}) {str(card)}"
                for idx, card in enumerate(chunk, start=i)
            )
            lines.append(line)
        
        return "\n".join(lines) if lines else '(Hidden)'