import numpy as np
from typing import Tuple, Callable, TYPE_CHECKING
from scipy.stats import hypergeom, binom

from state import State

from deck_utils import *


def get_sample_pmf(sample_value_func: Callable[[], float], sample_size=100000) -> Tuple[np.ndarray, np.ndarray]:
    counter = {}
    for i in range(sample_size):
        value_sample = sample_value_func()
        ## DEBUG
        #print(f"value = {value_sample}")
        if not counter.get(value_sample):
            counter[value_sample] = 0
        counter[value_sample] += 1

    sample_pmf = {
        value: count * 1.0 / sample_size for value, count in counter.items()
    }

    return np.array(list(sample_pmf.keys())), np.array(list(sample_pmf.values()))


def get_expected_value_from_pmf(xs: np.ndarray, ys: np.ndarray) -> float:
    expectation = 0.0
    for value, prob in zip(xs, ys):
        expectation += prob * value
    return expectation


def get_binomial_pmf(n: int, p: float, offset: float) -> Tuple[np.ndarray, np.ndarray]:
    rv = binom(n, p)
    xs_togo = np.arange(0, n + 1)
    probs = rv.pmf(xs_togo)
    xs = xs_togo + offset

    return xs, probs


def get_suit_count_analytic_pmf(state: State, suit: str) -> Tuple[np.ndarray, np.ndarray]:
    base_suit_count = get_suit_count(state.cards, suit)

    deck_suits_count = state.deck.suits_count
    deck_total_cards = sum(deck_suits_count.values())
    target_suit_count = deck_suits_count[suit]
    rounds = state.get_remain_rounds()
    extra_suit_count_distribution = hypergeom(deck_total_cards, target_suit_count, rounds)

    extra_suit_count_xs = np.arange(0, min(rounds, target_suit_count) + 1)
    probs = extra_suit_count_distribution.pmf(extra_suit_count_xs)
    suit_count_xs = extra_suit_count_xs + base_suit_count

    return suit_count_xs.tolist(), probs.tolist()


def get_k_round_max_probs(probs: np.ndarray, k: int) -> np.ndarray:
    probs_cumsum = np.cumsum(probs)
    y_cumsum = probs_cumsum ** k
    ys = np.ediff1d(y_cumsum, to_begin=y_cumsum[0])
    return ys


def get_k_round_min_probs(probs: np.ndarray, k: int) -> np.ndarray:
    probs_flip = np.flip(probs)
    probs_cumsum = np.cumsum(probs_flip)
    y_cumsum = probs_cumsum ** k
    ys = np.ediff1d(y_cumsum, to_begin=y_cumsum[0])
    return np.flip(ys)
