import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
from IPython.display import Image, display
import io
from analyst import Analyst


def get_random_entry(filename):
    return random.choice(open(filename).readlines()).replace("\n", "")

class Pod:

    def __init__(self, num_analysts):
        self.analysts = [Analyst() for _ in range(num_analysts)]
        self.fired_analysts = []
        self.aum = 1000
        self.name = get_random_entry("data/firm_name/name.txt")
        print(f"The firm {self.name} has just been opened")
        print(f"Assets under management: {self.aum}s")
        names = '\n\t'.join([analyst.name for analyst in self.analysts])
        print(f"Current staff are:\n\t{names}")

    def display_graph_as_png(self, fig):
        buffer = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        display(Image(buffer.read()))
        plt.close(fig)

    def show_history(self):
        """
        For each analyst, pulls up their history of coming up with strats
        """
        for analyst in self.analysts:
            analyst.report_history()

    def get_multi_choice(self, options):
        for i, option in zip(range(1, len(options) + 1), options):
            print(f"({i}) {option}")
        print("Type in your choice:")
        while True:
            player_choice = input()
            if player_choice == "HISTORY":
                self.show_history()
                continue
            try:
                choice_num = int(player_choice)
                if choice_num > len(options) or choice_num <= 0:
                    print("Invalid number, try again")
                    continue
                return choice_num
            except ValueError:
                print("That's not a number, try again")

    def get_strategy_choice(self):
        """
        Returns one of three options:
            1. Play it safe and go for imperial debt
            2. Irresponsibly put on a single huge bet at the chariots
            3. Choose a given analyst's strategy
        Note in case (3) it returns an Analyst, not a Strategy
        """
        # Generate and display strategies
        for analyst in self.analysts:
            analyst.generate_strategy()
        if len(self.analysts) > 0:
            fig, ax = plt.subplots(
                nrows=1,
                ncols=len(self.analysts),
                figsize=(len(self.analysts) * 3, 3),
                sharex=True,
                sharey=True
            )
            for i, analyst in zip(range(len(self.analysts)), self.analysts):
                cumulative_reported = analyst.report_strategy().cumsum()
                if len(self.analysts) > 1:
                    ax[i].plot(cumulative_reported, color="black")
                else:
                    ax.plot(cumulative_reported, color="black")
                title = "\n".join([
                    analyst.name,
                    analyst.current_strategy.name,
                    f"{cumulative_reported.iloc[-1]:.2f}s"
                ])
                if len(self.analysts) > 1:
                    ax[i].set_title(title)
                else:
                    ax.set_title(title)
            self.display_graph_as_png(fig)
        treasury_rate = random.choice([1, 2, 3, 4, 5])
        chariot_odds = 1 + np.random.binomial(8, 0.25)
        strategy_names = [
            f"Imperial bonds ({treasury_rate}%)",
            f"Punt on Blue at the chariots ({chariot_odds}:1 odds)"
        ]
        # Get player choice of strategies
        strategy_names += [
            f"{analyst.name}'s {analyst.current_strategy.name} trade"
            for analyst in self.analysts
        ]
        choice = self.get_multi_choice(strategy_names)
        print("How much will you stake?")
        print(f"NOTE: cannot be more than current AUM, {self.aum:.2f}s")
        while True:
            input_stake = input()
            try:
                stake = float(input_stake)
                if stake > self.aum or stake < 0:
                    print("Invalid number, try again")
                    continue
                break
            except ValueError:
                print("That's not a number, try again")
        if choice == 1:
            return [f"IMPERIAL BONDS {treasury_rate}", stake]
        elif choice == 2:
            return [f"CHARIOT PUNT {chariot_odds}", stake]
        else:
            return [self.analysts[choice - 3], stake]

    def process_annual_finances(self, strat_choice):
        """
        Gets returns from investments, updates AUM, and pays employees
        Args is strat_choice, which is [strategy, stake] list
        """
        # Get strat pnl, add to the total
        strat, stake = strat_choice[0], strat_choice[1]
        old_salaries = [analyst.salary for analyst in self.analysts]
        old_aum = self.aum
        new_aum = old_aum - strat_choice[1]
        if type(strat) == str:
            if strat[:-2] == "IMPERIAL BONDS":
                treasury_rate = int(strat[-1])
                interest = stake * (1 + treasury_rate / 100)
                print(f"Interest accumulated: {interest - stake:.2f}s")
                new_aum += interest
            else:
                chariot_odds = int(strat[-1]) + 1
                chariot_wins = random.random() < 0.25
                if chariot_wins:
                    print("Blue chariot wins!")
                    winnings = stake * chariot_wins * chariot_odds
                    print(f"Winnings: {winnings - stake:.2f}s")
                    new_aum += winnings
                else:
                    print("Blue chariot does NOT win")
        else:
            chosen_analyst = strat
            actual_result = chosen_analyst.run_strategy()
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.plot(actual_result.cumsum(), color="black")
            title = "\n".join([
                chosen_analyst.name,
                chosen_analyst.current_strategy.name,
                "Actual result"
            ])
            ax.set_title(title)
            self.display_graph_as_png(fig)
            returns = stake * (1 + actual_result.sum() / 1000)
            print(f"Return on investment: {returns - stake:.2f}s")
            new_aum += returns
        self.aum = new_aum
        print(f"AUM after investments: {self.aum:.2f}s")
        # Now pay salaries and update new wages
        salary_bill = sum(old_salaries)
        print(f"Paid out {salary_bill:.2f}s in salaries")
        self.aum -= salary_bill
        print(f"Current AUM: {self.aum:.2f}s")

    def fire_analysts(self):
        while len(self.analysts) > 0:
            print("Fire employees?")
            options = ["No firing"] + [an.name for an in self.analysts]
            choice = self.get_multi_choice(options)
            if choice == 1:
                break
            else:
                fired_analyst = self.analysts[choice - 2]
                self.analysts.remove(fired_analyst)
                self.fired_analysts.append(fired_analyst)
                print('> "' + get_random_entry(
                        "data/fire_message/youre_fired.txt"
                    ).replace("NAME", fired_analyst.name)+ '"'
                )
                print(
                    '> "' + get_random_entry(
                        "data/fire_message/response.txt"
                    ) + '"'
                )
                print(get_random_entry("data/fire_message/zoom_out.txt"))

    def hire_analysts(self):
        print("How many analysts to hire?")
        while True:
            player_input = input()
            try:
                choice = int(player_input)
                if choice < 0:
                    print("You can't hire negative analysts")
                    continue
                break
            except ValueError:
                print("That's not an integer - try again")
        new_analysts = [Analyst() for _ in range(choice)]
        self.analysts += new_analysts
        if len(new_analysts) > 0:
            names = '\n\t'.join([analyst.name for analyst in new_analysts])
            print(f"Welcome to the team:\n\t{names}")

    def run_one_year(self):
        strat_choice = self.get_strategy_choice()
        self.process_annual_finances(strat_choice)
        if self.aum <= 0:
            print("Oh no! You ran out of money!")
            return True
        self.fire_analysts()
        self.hire_analysts()
        return False

    def print_end_data(self):
        print("GAME OVER")
        print(f"Final PNL: {self.aum - 1000:.2f}s")
        print("Current analyst stats")
        for analyst in self.analysts:
            analyst.print_stats()
        print("Fired analyst stats")
        for analyst in self.fired_analysts:
            analyst.print_stats()
        print("You spend whatever sesterces you gained.")
        print("Life goes on, for better or worse you cannot say.")
        print("Soon your name is forgotten.")

    def run_multi_years(self, num_years):
        for year in range(num_years):
            over = self.run_one_year()
            if over:
                break
        self.print_end_data()
