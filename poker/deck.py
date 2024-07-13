import random

suits = ["heart", "square", "spade", "club"]
values = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
value2number = {}
for value_num, value_str in enumerate(values):
    value2number[value_str] = value_num + 1



class Card:
    def __init__(self, suit: str, value: str):
        self.suit = suit
        self.value = value

    def to_string(self) -> str:
        return f"{self.suit}.{self.value}"

    def get_value(self) -> int:
        return value2number[self.value]


class Deck:

    def __init__(self):
        self.suits = suits
        self.values = values
        self.deck_size = 40

        self.cards = []
        self.exist_flag = [True] * self.deck_size
        self.suits_count = {}
        self.values_count = {}

        for suit in self.suits:
            self.suits_count[suit] = 10
        for value in self.values:
            self.values_count[value] = 4

        self.card2index = {}
        for suit in self.suits:
            for value in self.values:
                card = Card(suit, value)
                self.card2index[card.to_string()] = len(self.cards)
                self.cards.append(card)

    def draw_card(self):
        while True:
            index = random.randrange(self.deck_size)
            if self.exist_flag[index]:
                break
        return self.cards[index]

    def mark_card(self, card: Card):
        index = self.card2index[card.to_string()]
        self.exist_flag[index] = False

        self.suits_count[card.suit] -= 1
        self.values_count[card.value] -= 1

    def get_exist_cards(self) -> list[str]:
        exist_cards = []

        for exist_flag, card in zip(self.exist_flag, self.cards):
            if exist_flag:
                exist_cards.append(card)

        return exist_cards

    def get_exist_card_unit_prob(self) -> float:
        return 1.0 / len(self.get_exist_cards())
