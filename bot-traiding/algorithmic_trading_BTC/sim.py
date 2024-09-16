# Import Library and Fetch Data
import requests
import pandas as pd
import numpy as np
import sys
import time
import datetime
from sklearn.linear_model import LogisticRegression

recursion = 2000
sys.setrecursionlimit(recursion)

def fetch_historical_data(symbol, interval, start_date, end_date, limit=1000):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&startTime={start_date}&endTime={end_date}&limit={limit}'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df

# Define the time ranges
now = datetime.datetime.now(datetime.timezone.utc)  # Current time in UTC
start_date_history = now - datetime.timedelta(days=445)  # 445 days ago for backtesting
end_date_backtest = now - datetime.timedelta(days=80)  # 80 days ago for backtesting
start_date_live = now - datetime.timedelta(days=80)  # Last 30 days for live trading, with 50 days for data collection.

# Convert datetime to milliseconds for API request
def to_milliseconds(dt):
    return int(dt.timestamp() * 1000)

# Fetch data for different intervals
df_1m = fetch_historical_data('BTCUSDT', '1m', to_milliseconds(start_date_history), to_milliseconds(end_date_backtest))
df_1h = fetch_historical_data('BTCUSDT', '1h', to_milliseconds(start_date_history), to_milliseconds(end_date_backtest))
df_4h = fetch_historical_data('BTCUSDT', '4h', to_milliseconds(start_date_history), to_milliseconds(end_date_backtest))
df_1d = fetch_historical_data('BTCUSDT', '1d', to_milliseconds(start_date_history), to_milliseconds(end_date_backtest))

#2 Trading Agents
class TradingAgent:
    def __init__(self, initial_cash=100000, name="Please Add My Name"):
        self.cash = initial_cash
        self.position = 0
        self.holdings = 0
        self.name = name

    def trade(self, signal, data):
        price = data['close'].iloc[-1]
        if signal == 1 and self.position != 1:
            # Calculate how much can be bought with available cash
            max_buyable_units = self.cash / price
            units_to_buy = min(max_buyable_units, self.cash // price)  # Ensure integer units

            if units_to_buy > 0:
                self.holdings += units_to_buy
                self.cash -= units_to_buy * price
                self.position = 1
                print(f"{pd.Timestamp.now()}: {self.name} Buy {units_to_buy} units at {price} per unit")

        elif signal == -1 and self.position != -1:
            if self.holdings > 0:
                self.cash += self.holdings * price
                self.holdings = 0
                self.position = -1
                print(f"{pd.Timestamp.now()}: {self.name} Sell all holdings at {price} per unit")

        else:
            print(f"{pd.Timestamp.now()}: {self.name} Hold")

    def get_portfolio_value(self, data):
        return self.cash + self.holdings * data['close'].iloc[-1]

class LogisticRegressionAgent(TradingAgent):
    def __init__(self, initial_cash=100000, name="Logistic Regression Agent"):
        super().__init__(initial_cash, name)
        self.model = LogisticRegression()
    
    def train_model(self, X_train, y_train):
        self.model.fit(X_train, y_train)
    
    def predict_signal(self, X):
        return self.model.predict(X)
    
    def trade(self, data):
        # Extract features and the latest data point for prediction
        features = ['SMA_20', 'SMA_50', 'RSI', 'MACD', 'Signal_Line', 'Upper_Band', 'Middle_Band', 'Lower_Band']
        latest_data = data.iloc[-1:][features]
        
        signal = self.predict_signal(latest_data)[0]
        
        # Call the parent class trade method with the predicted signal
        super().trade(signal, data)
            
#3 Data Preparation
# Prepare the training data
def prepare_data(data):
  data['Returns'] = data['close'].pct_change()
  data.ffill(inplace=True)
  data.bfill(inplace=True)
  data.dropna(inplace=True)
  return data

df_1m = prepare_data(df_1m)
df_1h = prepare_data(df_1h)
df_4h = prepare_data(df_4h)
df_1d = prepare_data(df_1d)

def calculate_rsi(data, window=14):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, short_window=50, long_window=200, signal_window=9):
    short_ema = data['close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['close'].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal_line

def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    # Calculate the middle band (SMA)
    middle_band = data['close'].rolling(window=window).mean()
    
    # Calculate the rolling standard deviation
    rolling_std_dev = data['close'].rolling(window=window).std()
    
    # Calculate the upper and lower bands
    upper_band = middle_band + (rolling_std_dev * num_std_dev)
    lower_band = middle_band - (rolling_std_dev * num_std_dev)
    
    return upper_band, middle_band, lower_band

def calculate_technical_indicators(data):
    # Ensure there are enough data points for each indicator calculation
    if len(data) < 50:
        return data
    
    # Calculate SMA
    data['SMA_20'] = data['close'].rolling(window=20).mean()
    data['SMA_50'] = data['close'].rolling(window=50).mean()
    
    # Calculate RSI
    data['RSI'] = calculate_rsi(data)
    
    # Calculate MACD and Signal Line
    data['MACD'], data['Signal_Line'] = calculate_macd(data)
    
    # Calculate Bollinger Bands
    data['Upper_Band'], data['Middle_Band'], data['Lower_Band'] = calculate_bollinger_bands(data)
    
    # Drop rows with NaN values
    data.dropna(inplace=True)
    
    return data

df_1m = calculate_technical_indicators(df_1m)
df_1h = calculate_technical_indicators(df_1h)
df_4h = calculate_technical_indicators(df_4h)
df_1d = calculate_technical_indicators(df_1d)

def split_data(data, train_ratio=0.8):
    split_index = int(len(data) * train_ratio)
    train_data = data.iloc[:split_index]
    test_data = data.iloc[split_index:]
    return train_data, test_data

# Split Traning and Testing set for historical data
df_1m_train, df_1m_test = split_data(df_1m)
df_1h_train, df_1h_test = split_data(df_1h)
df_4h_train, df_4h_test = split_data(df_4h)
df_1d_train, df_1d_test = split_data(df_1d)

# Prepare the features and target for training
def prepare_features_and_target(data):
    data['Future_Close'] = data['close'].shift(-1)
    data['Target'] = np.where(data['Future_Close'] > data['close'], 1, 0)
    
    features = ['SMA_20', 'SMA_50', 'RSI', 'MACD', 'Signal_Line', 'Upper_Band', 'Middle_Band', 'Lower_Band']
    X = data[features]
    y = data['Target']
    
    # Drop the last row since it will have NaN target
    X = X.iloc[:-1]
    y = y.iloc[:-1]
    
    return X, y

# prepare features and target
X_1m, y_1m = prepare_features_and_target(df_1m_train)
X_1h, y_1h = prepare_features_and_target(df_1h_train)
X_4h, y_4h = prepare_features_and_target(df_4h_train)
X_1d, y_1d = prepare_features_and_target(df_1d_train)

#4 Backtesting
# Backtesting function
def backtest(agent, data):
    data = calculate_technical_indicators(data)
    for timestamp, row in data.iterrows():
        agent.trade(data.loc[:timestamp])
    return agent.get_portfolio_value(data)

# Initialize agents for different intervals (Logistic Regression)
agent_1m = LogisticRegressionAgent(name="1m Interval Agent")
agent_1h = LogisticRegressionAgent(name="1h Interval Agent")
agent_4h = LogisticRegressionAgent(name="4h Interval Agent")
agent_1d = LogisticRegressionAgent(name="1d Interval Agent")

# Train the agents
agent_1m.train_model(X_1m, y_1m)
agent_1h.train_model(X_1h, y_1h)
agent_4h.train_model(X_4h, y_4h)
agent_1d.train_model(X_1d, y_1d)

# Backtest each agent and get portfolio values (Uncomment to test)
# portfolio_value_1m = backtest(agent_1m, df_1m_test)
# portfolio_value_1h = backtest(agent_1h, df_1h_test)
# portfolio_value_4h = backtest(agent_4h, df_4h_test)
# portfolio_value_1d = backtest(agent_1d, df_1d_test)

# Print portfolio values for each interval
# print(f"Portfolio Value for 1m Interval: {portfolio_value_1m}")
# print(f"Portfolio Value for 1h Interval: {portfolio_value_1h}")
# print(f"Portfolio Value for 4h Interval: {portfolio_value_4h}")
# print(f"Portfolio Value for 1d Interval: {portfolio_value_1d}")

#5 Live-Trading
# Function to update agents in real-time
def update_data(data, interval):
    new_data = fetch_historical_data('BTCUSDT', interval, limit=1)
    new_data = prepare_data(new_data)
    data = pd.concat([data, new_data])
    data = calculate_technical_indicators(data)
    return data

def update_agents():
    global df_1m, df_1h, df_4h, df_1d
    df_1m = update_data(df_1m, '1m')
    df_1h = update_data(df_1h, '1h')
    df_4h = update_data(df_4h, '4h')
    df_1d = update_data(df_1d, '1d')
    agent_1m.trade(df_1m)
    agent_1h.trade(df_1h)
    agent_4h.trade(df_4h)
    agent_1d.trade(df_1d)
    print(f"1m Interval Portfolio Value: {agent_1m.get_portfolio_value()}")
    print(f"1h Interval Portfolio Value: {agent_1h.get_portfolio_value()}")
    print(f"4h Interval Portfolio Value: {agent_4h.get_portfolio_value()}")
    print(f"1d Interval Portfolio Value: {agent_1d.get_portfolio_value()}")

# while True:
#     update_agents()
#     time.sleep(60) # Adjust the sleep time according to the interval

# 5.5 Near-Live Trading
# Near-live data (30 days)
df_1m_live = fetch_historical_data('BTCUSDT', '1m', to_milliseconds(start_date_live), to_milliseconds(now))
df_1h_live = fetch_historical_data('BTCUSDT', '1h', to_milliseconds(start_date_live), to_milliseconds(now))
df_4h_live = fetch_historical_data('BTCUSDT', '4h', to_milliseconds(start_date_live), to_milliseconds(now))
df_1d_live = fetch_historical_data('BTCUSDT', '1d', to_milliseconds(start_date_live), to_milliseconds(now))

# Prepare Data
df_1m_live = prepare_data(df_1m_live)
df_1h_live = prepare_data(df_1h_live)
df_4h_live = prepare_data(df_4h_live)
df_1d_live = prepare_data(df_1d_live)

def live_trading_simulation(agent, data, initial_data_points=50):
    # Initialize a list to store the initial data points
    collected_data_list = []

    # Collect initial data points to ensure enough data for calculations
    for idx, row in data.iterrows():
        collected_data_list.append(row)
        if len(collected_data_list) >= initial_data_points:
            break

    # Convert collected data to a DataFrame
    collected_data = pd.DataFrame(collected_data_list, columns=data.columns)
    
    # Ensure collected_data has enough rows to calculate indicators
    if len(collected_data) < initial_data_points:
        return agent.get_portfolio_value(collected_data)

    # Start live trading simulation after collecting initial data
    for idx, row in data.iterrows():
        # Convert the new row to a DataFrame
        new_row = pd.DataFrame([row], columns=data.columns)
        
        # Append the new row to the collected data
        collected_data = pd.concat([collected_data, new_row], ignore_index=True)
        
        # Recalculate technical indicators based on the collected data
        collected_data = calculate_technical_indicators(collected_data)

        # Prepare features and target for the most recent data point
        features = ['SMA_20', 'SMA_50', 'RSI', 'MACD', 'Signal_Line', 'Upper_Band', 'Middle_Band', 'Lower_Band']
        latest_data = collected_data[features].iloc[-1:].copy()  # Take the latest row for prediction

        # Make trading decision based on the predicted signal
        agent.trade(latest_data)

        # Optional: Print portfolio value or other metrics
        print(f"Timestamp: {idx}, Portfolio Value: {agent.get_portfolio_value(collected_data)}")

    return agent.get_portfolio_value(collected_data)

# Near-Live Trading Simulation (Uncomment to test)
portfolio_value_1m_live = live_trading_simulation(agent_1m, df_1m_live)
portfolio_value_1h_live = live_trading_simulation(agent_1h, df_1h_live)
portfolio_value_4h_live = live_trading_simulation(agent_4h, df_4h_live)
portfolio_value_1d_live = live_trading_simulation(agent_1d, df_1d_live)

# Print portfolio values after near-live trading simulation
print(f"Near-Live Trading Portfolio Value for 1m Interval: {portfolio_value_1m_live}")
print(f"Near-Live Trading Portfolio Value for 1h Interval: {portfolio_value_1h_live}")
print(f"Near-Live Trading Portfolio Value for 4h Interval: {portfolio_value_4h_live}")
print(f"Near-Live Trading Portfolio Value for 1d Interval: {portfolio_value_1d_live}")
