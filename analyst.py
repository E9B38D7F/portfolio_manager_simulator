import numpy as np
import pandas as pd
import random
from strategy import Strategy


def get_random_entry(filename):
    return random.choice(open(filename).readlines()).replace("\n", "")

class Analyst:

    def __init__(self):
        """
        Special note: history is a list of triples:
        [strategy_name, reported_pnl, actual_pnl]
        If the strat wasn't chosen, actual_pnl is None
        """
        self.name = self.generate_name()
        self.deceptive = np.random.geometric(1/3)
        self.talented = np.random.normal(0.5, 1)
        self.current_strategy = None
        self.salary = 50
        self.history = []

    def generate_name(self):
        gender = random.choice(["Male", "Female"])
        # Not a political statement, just how Roman names work
        suffix = "us" if gender == "Male" else "a"
        praenomen = get_random_entry("data/name/praenomen.txt") + suffix
        nomen = get_random_entry("data/name/nomen.txt")
        if gender == "Female":
            nomen = nomen[:-2] + "a"
        cognomen = get_random_entry(f"data/name/{gender.lower()}_cognomen.txt")
        return f"{praenomen} {nomen} {cognomen}"

    def generate_strategy(self):
        self.current_strategy = Strategy(self.talented)

    def report_strategy(self):
        reported = self.current_strategy.generate_reported_pnl(self.deceptive)
        self.history.append([self.current_strategy.name, reported.sum(), None])
        return reported

    def run_strategy(self):
        actual = self.current_strategy.generate_annual_daily_pnl()
        self.salary += 50
        self.history[-1][2] = actual.sum()
        return actual

    def report_history(self):
        print(f"\t{self.name}'s history:")
        for it in self.history:
            print_str = f"\t\t{it[0]}. Reported: {it[1]:+.2f}, "
            if it[2] is None:
                print_str += "not implemented"
            else:
                print_str += f"actual: {it[2]:+.2f}"
            print(print_str)

    def print_stats(self):
        print(f"\t{self.name}'s history:")
        print(f"\t\tTalented: {self.talented:.2f}")
        print(f"\t\tDeceptive: {self.deceptive:.2f}")
