import numpy as np
import pandas as pd
import random


def get_random_entry(filename):
    return random.choice(open(filename).readlines()).replace("\n", "")

class Strategy:

    def __init__(self, talent):
        self.days = 250
        self.name = self.generate_name()
        self.daily_expected_trades = np.random.exponential(4)
        self.exponent = np.random.poisson(2)
        self.daily_stdev = max(0, np.random.normal(10, 3))
        self.mean = np.random.normal(talent, 2)
        self.size_factor = np.random.uniform(0, 1)

    def generate_name(self):
        provenance = get_random_entry("data/products/provenance.txt")
        product = get_random_entry("data/products/product.txt").lower()
        return f"{provenance} {product}"

    def generate_annual_daily_pnl(self):
        daily_size = np.random.poisson(
            self.daily_expected_trades,
            self.days
        ) ** self.exponent
        daily_size = self.size_factor * daily_size / daily_size.mean()
        daily_pnl = pd.Series(
            daily_size * np.random.normal(
                self.mean,
                self.daily_stdev,
                self.days
            ),
            index=np.arange(self.days)
        )
        return daily_pnl

    def generate_reported_pnl(self, deceptiveness):
        annual_pnls = [
            self.generate_annual_daily_pnl()
            for i in range(np.random.geometric(1 / deceptiveness))
        ]
        reported_pnl = sorted([
            [annual_pnl.sum(), annual_pnl] for annual_pnl in annual_pnls
        ])[-1][1]
        return reported_pnl
