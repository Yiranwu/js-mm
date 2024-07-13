from deck import Deck, Card


class State:

    def __init__(self):
        self.deck = Deck()
        self.max_round = 4
        self.round = 0
        self.cards = []

    def get_remain_rounds(self) -> int:
        return self.max_round - self.round

    def step(self) -> Card:
        card = self.deck.draw_card()
        return self.step_with(card)

    def step_with(self, card: Card) -> Card:
        assert (self.round < self.max_round, "no more rounds after round 4!")
        self.round += 1
        self.deck.mark_card(card)
        self.cards.append(card)
        return card

