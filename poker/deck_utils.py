from functools import partial
from typing import Callable

from deck import Card, Deck


def _func_get_value(card: Card) -> int:
    return card.get_value()


def _func_check_card_belong_to_suit(card: Card, suit: str) -> bool:
    return card.suit == suit


def _func_check_value_in_range(card: Card, lb: int, ub: int) -> bool:
    return lb <= card.get_value() < ub


def get_suit_filter_instance(suit: str) -> Callable[[Card], bool]:
    return partial(_func_check_card_belong_to_suit, suit=suit)


def get_value_range_filter_instance(lb: int, ub: int) -> Callable[[Card], bool]:
    return partial(_func_check_value_in_range, lb=lb, ub=ub)


def to_values(cards: list[Card]) -> list[int]:
    return list(map(_func_get_value, cards))


def get_value_sum(cards: list[Card]) -> float:
    return float(sum(list(map(_func_get_value, cards))))


def get_value_max(cards: list[Card]) -> float:
    value_list = list(map(_func_get_value, cards)) + [0]
    return float(max(value_list))


def get_value_min(cards: list[Card]) -> float:
    value_list = list(map(_func_get_value, cards))
    if len(value_list) == 0:
        return 0
    return float(min(value_list))


def filter_suit(cards: list[Card], suit: str) -> list[Card]:
    return list(filter(get_suit_filter_instance(suit), cards))


def filter_value_by_range(cards: list[Card], lb: int, ub: int) -> list[Card]:
    return list(filter(get_value_range_filter_instance(lb, ub), cards))


def get_suit_count(cards: list[Card], suit: str) -> int:
    return len(filter_suit(cards, suit))


def get_suit_value_sum(cards: list[Card], suit: str) -> float:
    return float(sum(to_values(filter_suit(cards, suit))))


if __name__ == '__main__':
    deck = Deck()
    import random
    my_cards = [random.choice(deck.cards)]
    my_filter = get_suit_filter_instance('heart')
    my_filtered_cards = my_filter(my_cards[0])
