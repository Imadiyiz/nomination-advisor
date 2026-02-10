# functions for the ViewFormat Class
from Classes.CardClass import Card

def format_hand(hand: list[Card], cols=4):
        """
        Formats hand into a readable format
        
        """

        lines = []

        for i in range(0, len(hand), cols):

            chunk = hand[i:i+cols]
            row = []


            for idx, card in enumerate(chunk, start=i):
                card_string = str(card)
                if len(card.initials) < 3:
                     card_string = " " + str(card)

                row.append(f"\t{idx + 1}) {card_string}")

            lines.append("\t".join(row))
        
        return "\n".join(lines) if lines else '(Hidden)'