from typing import Tuple
import numpy as np

from assets import AssetBase
from pmf_utils import get_sample_pmf


class Positions:
    def __init__(self):
        self.positions = []

    def add_position(self, asset: AssetBase, amount: float):
        self.positions.append((asset, amount))

    def get_expected_value(self) -> float:
        value = 0.0
        for (asset, amount) in self.positions:
            value += asset.get_expected_value_analytic() * amount
        return value

    def sample_value(self) -> float:
        value = 0.0
        for (asset, amount) in self.positions:
            value += asset.sample_value() * amount
        return value

    def get_sample_pmf(self, sample_size=100000) -> Tuple[np.ndarray, np.ndarray]:
        return get_sample_pmf(self.sample_value, sample_size)

    def show_positions(self):
        for (asset, amount) in self.positions:
            print(f"{amount} * {asset.to_string()}")
