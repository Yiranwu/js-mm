from assets import *


class Trader:

    def propose_trade(self, asset: AssetBase, quote: list[float]) -> str:
        raise NotImplementedError("propose_trade is not implemented")


class MaxExpectedReturnTrader(Trader):

    def evaluate_expected_return(self, asset: AssetBase, price: float, action: float) -> float:
        expected_return = asset.get_expected_value_analytic() - price
        return action * expected_return

    def propose_trade(self, asset: AssetBase, quote: list[float]) -> str:
        bid, ask = quote
        assert (ask > bid, "Invalid quote")
        assert (ask - bid <= asset.max_market_width, "Quote has negative return in expectation")

        buy_return = self.evaluate_expected_return(asset, ask, 1)
        sell_return = self.evaluate_expected_return(asset, bid, -1)

        if buy_return > sell_return:
            return 'buy'
        else:
            return 'sell'
