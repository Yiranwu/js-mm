import numpy as np
from copy import deepcopy
import random
from math import factorial
from typing import Tuple

from state import State
from deck_utils import *
from pmf_utils import *


class AssetBase:

    def __init__(self, state: State):
        self.state = deepcopy(state)
        self.sample_size = 50000
        #self.sample_pmf = self.get_sample_pmf()
        self.analytic_pmf = self.get_analytic_pmf()
        #self.expected_value_sample = self.get_expected_value_sample()
        self.expected_value_analytic = self.get_expected_value_analytic()
        #delta = self.expected_value_analytic - self.expected_value_sample
        #assert abs(delta) / abs(self.expected_value_sample) < 0.01

        self.max_market_width = self.guarantee_trade_market_width()

    def get_exist_cards(self) -> list[Card]:
        return self.state.deck.get_exist_cards()

    def get_exist_suit_cards(self, suit: str) -> list[Card]:
        return filter_suit(self.get_exist_cards(), suit)

    def get_exist_card_unit_prob(self) -> float:
        return self.state.deck.get_exist_card_unit_prob()

    def get_cards_value(self, cards: list[Card]) -> float:
        raise NotImplementedError("get_cards_value() not implemented")

    def sample(self) -> list[Card]:
        exist_cards = self.get_exist_cards()
        remain_rounds = self.state.get_remain_rounds()
        sample_cards = np.random.choice(exist_cards, size=remain_rounds, replace=False).tolist()
        cards = self.state.cards + sample_cards
        return cards

    def sample_value(self) -> float:
        return self.get_cards_value(self.sample())

    def get_sample_pmf(self) -> Tuple[np.ndarray, np.ndarray]:
        return get_sample_pmf(self.sample_value, self.sample_size)

    def get_analytic_pmf(self) -> Tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError("get_analytic_pmf() not implemented")

    def get_expected_value_analytic(self) -> float:
        return get_expected_value_from_pmf(*self.get_analytic_pmf())

    def get_expected_value_sample(self) -> float:
        return get_expected_value_from_pmf(*self.get_sample_pmf())

    def to_string(self):
        raise NotImplementedError("to_string() not implemented")

    def guarantee_trade_market_width(self) -> float:
        return random.uniform(0.1, 0.5) * self.get_expected_value_analytic()


class SumOfValuesAsset(AssetBase):

    def __init__(self, state: State):
        super().__init__(state)

    def get_cards_value(self, cards: list[Card]) -> float:
        return get_value_sum(cards)

    # It's not the actual pmf, as it parameterizes RV
    # x = value * bernoulli(p) into x' = binomial(value, p)
    def get_analytic_pmf(self) -> Tuple[np.ndarray, np.ndarray]:
        base_value = get_value_sum(self.state.cards)

        exist_cards = self.get_exist_cards()
        remain_rounds = self.state.get_remain_rounds()
        in_prob = 1.0 * remain_rounds * self.get_exist_card_unit_prob()
        exist_value_sum = get_value_sum(exist_cards)

        return get_binomial_pmf(exist_value_sum, in_prob, base_value)

    def to_string(self):
        return "sum of card values"


class SumOfSuitValuesAsset(AssetBase):

    def __init__(self, state: State, suit: str):
        self.suit = suit
        super().__init__(state)

    def get_cards_value(self, cards: list[Card]) -> float:
        return get_value_sum(filter_suit(cards, self.suit))

    # It's not the actual pmf, as it parameterizes RV
    # x = value * bernoulli(p) into x' = binomial(value, p)
    def get_analytic_pmf(self) -> Tuple[np.ndarray, np.ndarray]:
        base_value = get_suit_value_sum(self.state.cards, self.suit)

        exist_suit_cards = self.get_exist_suit_cards(self.suit)
        in_prob = 1.0 * self.get_exist_card_unit_prob() * self.state.get_remain_rounds()
        exist_suit_value_sum = get_suit_value_sum(exist_suit_cards, self.suit)

        return get_binomial_pmf(int(exist_suit_value_sum), in_prob, base_value)

    def to_string(self):
        return f"sum of {self.suit} card values"


class XDivideBySuitCountAsset(AssetBase):

    def __init__(self, state: State, numerator: float, suit: str):
        self.numerator = numerator
        self.suit = suit
        super().__init__(state)

    def get_cards_value(self, cards: list[Card]) -> float:
        return self.numerator / len(filter_suit(cards, self.suit))

    def get_analytic_pmf(self) -> Tuple[np.ndarray, np.ndarray]:
        assert (get_suit_count(self.state.cards, self.suit) >= 1)
        xs, ys = get_suit_count_analytic_pmf(self.state, self.suit)
        xs = self.numerator / np.array(xs)
        return xs, ys

    def to_string(self):
        return f"{self.numerator} divide by {self.suit} card count"


class XToTheSuitCountAsset(AssetBase):

    def __init__(self, state: State, base: float, suit: str):
        self.base = base
        self.suit = suit
        super().__init__(state)

    def get_cards_value(self, cards: list[Card]) -> float:
        return self.base ** get_suit_count(cards, self.suit)

    def get_analytic_pmf(self) -> Tuple[np.ndarray, np.ndarray]:
        xs, ys = get_suit_count_analytic_pmf(self.state, self.suit)
        xs = self.base ** np.array(xs)
        return xs, ys

    def to_string(self) -> str:
        return f"{self.base} to the power of {self.suit} card count"


class SuitCountFactorialAsset(AssetBase):
    def __init__(self, state: State, suit: str):
        self.suit = suit
        super().__init__(state)

    def get_cards_value(self, cards: list[Card]) -> float:
        suit_count = get_suit_count(cards, self.suit)
        return factorial(suit_count)

    def get_analytic_pmf(self) -> Tuple[np.ndarray, np.ndarray]:
        xs, ys = get_suit_count_analytic_pmf(self.state, self.suit)
        xs = np.array([factorial(x) for x in xs])
        return xs, ys

    def to_string(self):
        return f"factorial of {self.suit} card count"


class MaxSuitValueAsset(AssetBase):

    def __init__(self, state: State, suit: str):
        self.suit = suit
        super().__init__(state)

    def get_cards_value(self, cards: list[Card]) -> float:
        return get_value_max(filter_suit(cards, self.suit))

    def get_analytic_pmf(self) -> Tuple[np.ndarray, np.ndarray]:
        base_value = self.get_cards_value(filter_suit(self.state.cards, self.suit))

        exist_cards = self.get_exist_cards()
        exist_suit_cards = self.get_exist_suit_cards(self.suit)
        suit_cards_prob = np.ones(len(exist_suit_cards)) * self.get_exist_card_unit_prob()
        suit_cards_x = to_values(exist_suit_cards)

        xs_extended = np.array([0] + suit_cards_x)
        probs_extended = np.array([1.0-np.sum(suit_cards_prob)] + suit_cards_prob.tolist())

        remain_rounds = self.state.get_remain_rounds()

        probs = get_k_round_max_probs(probs_extended, remain_rounds)

        gt_xs = xs_extended[xs_extended > base_value]
        gt_probs = probs[xs_extended > base_value]
        leq_probs = probs[xs_extended <= base_value]
        leq_prob = np.sum(leq_probs)

        xs = np.array([base_value] + gt_xs.tolist())
        probs = np.array([leq_prob] + gt_probs.tolist())

        return xs, probs

    def to_string(self):
        return f"max {self.suit} card value"


class MinSuitValueAsset(AssetBase):

    def __init__(self, state: State, suit: str):
        self.suit = suit
        super().__init__(state)

    def get_cards_value(self, cards: list[Card]) -> float:
        return get_value_min(filter_suit(cards, self.suit))

    def get_analytic_pmf(self) -> Tuple[np.ndarray, np.ndarray]:
        base_value = self.get_cards_value(filter_suit(self.state.cards, self.suit))
        if base_value == 0:
            base_value = 11.0

        exist_cards = self.get_exist_cards()
        exist_suit_cards = self.get_exist_suit_cards(self.suit)
        suit_cards_prob = np.ones(len(exist_suit_cards)) * self.get_exist_card_unit_prob()
        suit_cards_x = to_values(exist_suit_cards)

        xs_extended = np.array(suit_cards_x + [11])
        probs_extended = np.array(suit_cards_prob.tolist() + [1.0-np.sum(suit_cards_prob)])

        remain_rounds = self.state.get_remain_rounds()

        probs = get_k_round_min_probs(probs_extended, remain_rounds)

        lt_xs = xs_extended[xs_extended < base_value]
        lt_probs = probs[xs_extended < base_value]
        geq_probs = probs[xs_extended >= base_value]
        geq_prob = np.sum(geq_probs)

        if base_value == 11.0:
            base_value = 0.0

        xs = np.array(lt_xs.tolist() + [base_value])
        probs = np.array(lt_probs.tolist() + [geq_prob])

        return xs, probs

    def to_string(self):
        return f"min {self.suit} card value"


class SuitSideBetAsset(AssetBase):

    def __init__(self, state: State, side: str):
        assert (side == 'red' or side == 'black')
        self.side = side
        super().__init__(state)

    def get_cards_value(self, cards: list[Card]) -> float:
        next_card = cards[self.state.round]
        red_value = 1 if next_card.suit == 'heart' or next_card.suit == 'square' else -1

        return red_value if self.side == 'red' else -red_value

    def get_analytic_pmf(self) -> Tuple[np.ndarray, np.ndarray]:
        xs = [-1, 1]

        exist_cards = self.get_exist_cards()
        exist_r_cards = filter_suit(exist_cards, 'heart') + filter_suit(exist_cards, 'square')
        exist_r_cnt = len(exist_r_cards)
        r_prob = 1.0 * exist_r_cnt * self.get_exist_card_unit_prob()
        b_prob = 1 - r_prob

        ys = [b_prob, r_prob] if self.side == 'red' else [r_prob, b_prob]

        return np.array(xs), np.array(ys)

    def to_string(self):
        return f"suit side bet: {self.side}"


class ValueSideBetAsset(AssetBase):

    def __init__(self, state: State, side: str):
        assert (side == 'small' or side == 'large')
        self.side = side
        super().__init__(state)

    def get_cards_value(self, cards: list[Card]) -> float:
        next_card = cards[self.state.round]
        small_value = 1 if next_card.get_value() <= 5 else -1

        return small_value if self.side == 'small' else -small_value

    def get_analytic_pmf(self) -> Tuple[np.ndarray, np.ndarray]:
        xs = [-1, 1]

        exist_cards = self.get_exist_cards()
        exist_small_cards = filter_value_by_range(exist_cards, 1, 6)
        exist_small_cnt = len(exist_small_cards)
        small_prob = 1.0 * exist_small_cnt * self.get_exist_card_unit_prob()
        large_prob = 1 - small_prob

        ys = [large_prob, small_prob] if self.side == 'small' else [small_prob, large_prob]

        return np.array(xs), np.array(ys)

    def to_string(self):
        return f"value side bet: {self.side}"


if __name__ == '__main__':
    state = State()
    card1 = state.step()
    while True:
        diff_suit = random.choice(state.deck.suits)
        if diff_suit != card1.suit:
            break
    print(f"card1={card1.to_string()}")
    print(f"diff_sult={diff_suit}")
    asset = XDivideBySuitCountAsset(state, 24, card1.suit)
    #asset2 = XDivideBySuitCountAsset(state, 24,  diff_suit)
