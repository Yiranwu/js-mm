import random

from state import State
from assets import *
from positions import Positions
from trader import MaxExpectedReturnTrader


class Game:
    def __init__(self):
        self.state = State()
        self.positions = Positions()
        self.trader = MaxExpectedReturnTrader()

    def play(self):
        self.play_round(0)
        for i in range(4):
            self.step()

    def step(self):
        card = self.state.step()
        print(f"----------Round {self.state.round}----------")
        print(f"Card revealed: {card.to_string()}")
        self.play_round(self.state.round)

    def play_round(self, round: int):
        if round == 0:
            self.make_market_on(SumOfValuesAsset(self.state))
            self.make_market_on(SumOfSuitValuesAsset(self.state, random.choice(self.state.deck.suits)))

        elif round == 1:
            self.make_market_on(XDivideBySuitCountAsset(self.state, 24, self.state.cards[0].suit))
            self.make_market_on(MinSuitValueAsset(self.state, random.choice(self.state.deck.suits)))

        elif round == 2:
            self.make_market_on(SuitCountFactorialAsset(self.state, random.choice(self.state.deck.suits)))

        elif round == 3:
            self.make_market_on(XToTheSuitCountAsset(self.state, 5, random.choice(self.state.cards).suit))

        self.make_side_bets()

        print("Your positions:")
        self.positions.show_positions()

    def make_market_on(self, asset: AssetBase):
        print(f"Please make a market on {asset.to_string()}, input bid and ask.")
        print(f"I will guarantee a trade for {asset.max_market_width}-wide market.")
        quote = self.read_quotes()
        print(f"Expected value of asset is: {asset.get_expected_value_analytic()}")
        trader_action = self.trader.propose_trade(asset, quote)
        if trader_action == 'buy':
            print("I will buy")
            self.positions.add_position(asset, -1)
        else:
            print("I will sell")
            self.positions.add_position(asset, 1)

    def make_side_bets(self):
        print("Please make suit and value based side bets")
        print("Input two values, first value positive for betting red, second value positive for betting small")
        quote = self.read_quotes()
        suit_bet_amount, value_bet_amount = quote
        if suit_bet_amount != 0:
            self.positions.add_position(SuitSideBetAsset(self.state, 'red' if suit_bet_amount > 0 else 'black'),
                                        abs(suit_bet_amount))
        if value_bet_amount != 0:
            self.positions.add_position(ValueSideBetAsset(self.state, 'small' if value_bet_amount > 0 else 'large'),
                                        abs(value_bet_amount))
        raise NotImplementedError("Please implement GT side bet amount")

    def read_quotes(self) -> list[float]:
        quotes_str = input()
        quotes = quotes_str.split()
        assert (len(quotes) == 2)
        return [float(quote) for quote in quotes]


if __name__ == '__main__':
    game = Game()
    game.play()
