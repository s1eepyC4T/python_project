import numpy as np
import pandas as pd

class SmartAgent:
    def __init__(self, short_window=5, long_window=20):
        self.name = "Smart"
        self.position = 0  # 0: No position, 1: Long, -1: Short
        self.cash = 100000  # Starting cash in USD
        self.holdings = 0
        self.short_window = short_window
        self.long_window = long_window
        self.short_mavg = None
        self.long_mavg = None

    def calculate_moving_averages(self, data):
        self.short_mavg = data['Close'].rolling(window=self.short_window).mean().iloc[-1]
        self.long_mavg = data['Close'].rolling(window=self.long_window).mean().iloc[-1]

    def generate_signals(self):
        # Generate signals based on moving averages
        if self.short_mavg > self.long_mavg:
            return 1  # Buy signal
        elif self.short_mavg < self.long_mavg:
            return 2  # Sell signal
        else:
            return 0  # Hold signal

    def trade(self, data):
        self.calculate_moving_averages(data)
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
