import numpy as np
import pandas as pd

class MomentumAgent:
    def __init__(self, window=20):
        self.name = "Momentum"
        self.position = 0  # 0: No position, 1: Long, -1: Short
        self.cash = 100000  # Starting cash in USD
        self.holdings = 0
        self.window = window
        self.price_change = None

    def calculate_momentum(self, data):
        self.price_change = data['Close'].pct_change(periods=self.window).iloc[-1]

    def generate_signals(self):
        # Generate signals based on price momentum
        if self.price_change > 0:
            return 1  # Buy signal
        elif self.price_change < 0:
            return 2  # Sell signal
        else:
            return 0  # Hold signal

    def trade(self, data):
        self.calculate_momentum(data)
        signal = self.generate_signals()
        price = data['Close'].iloc[-1]
        if signal == 1 and self.position != 1:
            if self.cash > 0:
                self.holdings = self.cash / price
                self.cash = 0
                self.position = 1
                print(f"{pd.Timestamp.now()}: {self.name} Buy at {price}")
        elif signal == 2 and self.position != -1:
            if self.holdings > 0:
                self.cash = self.holdings * price
                self.holdings = 0
                self.position = -1
                print(f"{pd.Timestamp.now()}: {self.name} Sell at {price}")
        else:
            print(f"{pd.Timestamp.now()}: {self.name} Hold")

    def get_portfolio_value(self, current_price):
        return self.cash + (self.holdings * current_price)
