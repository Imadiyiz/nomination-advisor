#Classes script for the Card deck
from .CardClass import Card
import random

class Deck:

    """
    This is the Deck class for the cards in the game.
    It acts as more of a deck manager, as opposed to a deck itself
    This class is responsible for managing card objects in it

    Functions:

    generate_deck populates the local deck list
    generate_valid_initials returns a set of valid initials
    remove_card removes the card selected and takes the suit and value as the parameter
    draw_card_from_initials returns a card if the initials match to a card and removes the card from deck
    find_card returns boolean depending on whether the suit and value in the parameters are found
    
    """
    def __init__(self):
        
        self.single_value_gen = ("2","3","4","5","6","7","8","9","10","J","Q","K","A" )
        self.value_gen = set()
        
        #ensures that the picture cards still have a value
        for index, item in enumerate(self.single_value_gen):
            self.value_gen.add((item,index+2))

        self.suit_gen = (("Diamonds","♦"), ("Spades","♠"),("Clubs","♣"),("Hearts","♥"))
        self.first_letter_suits = {
            "D" : "Diamonds",
            "S" : "Spades", 
            "C" : "Clubs",
            "H" : "Hearts"
        }
        self.deck = self.generate_deck()
        self.valid_card_initials = self.generate_valid_card_initials()
        
    def generate_deck(self):
        """
        Logic for iterating through both lists to create a full deck of cards.
        Also resets the local deck list
        """
        self.deck = []
        for value in self.value_gen:
            for suit in self.suit_gen:
                self.deck.append(Card(suit, value))
        random.shuffle(self.deck) #always shuffle deck after generation

        return self.deck
    
    def generate_valid_card_initials(self) -> set:
        """
        Logic for iterating through both lists to create a set of valid card initials
        """
        valid_card_initials = set()
        for character in self.single_value_gen:
            for suit in self.first_letter_suits.keys():
                valid_card_initials.add((character + suit))
        return valid_card_initials
        
    def remove_card(self, card: Card):
        """
        Function for removing card from current hand

        Requires card instance inside of current deck
        """
        if not card:
            raise ValueError("Card not found in deck")
        self.deck.remove(card)

    def find_card(self, selected_suit:str, selected_value:str):
        """
        Function which returns True or False to verify 
        whether the card is in the current hand
        """
        for card in self.deck:
            if (card.suit[0].lower() == selected_suit.lower()) and (card.value[0].lower() == selected_value.lower()):
                return True
        return False


    def draw_card_from_initials(self, initials: str) -> Card | None:
        """
        Function returns the card object from the card in the deck
        with the correct initials and removes it from the deck

        """

        value_str, suit_letter = Card.from_initials(initials)

        for card in self.deck:
            if (
                card.value[0].upper() == value_str and
                card.suit[0][0].upper() == suit_letter
            ):
                self.remove_card(card)
                return card
        return None
    
    def get_card(self, card:Card) -> Card | None:
        """Returns a card if card passed is in deck"""