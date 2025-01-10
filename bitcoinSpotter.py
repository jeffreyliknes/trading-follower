import requests
import pandas as pd
import pandas_ta as ta
from telegram import Bot
import time
from datetime import datetime

# Telegram Bot Token and Chat ID
BOT_TOKEN = "7814985675:AAG513pk7gWR01VFFeJL4JidKbtgQEV4YhI"
CHAT_ID = 6458736937  # Replace with your actual chat ID

# Binance API Endpoint
symbol = 'BTCUSDT'
binance_url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=100"

# Function to fetch real-time price data
def get_price_data():
    try:
        response = requests.get(binance_url)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            df['close'] = pd.to_numeric(df['close'])
            df['high'] = pd.to_numeric(df['high'])
            df['low'] = pd.to_numeric(df['low'])
            return df
        else:
            print(f"Error fetching data: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception fetching data: {e}")
        return None

# Function to calculate indicators
def calculate_indicators(df):
    df['EMA9'] = ta.ema(df['close'], length=9)
    df['EMA21'] = ta.ema(df['close'], length=21)
    df['RSI'] = ta.rsi(df['close'], length=14)
    df[['BB_upper', 'BB_middle', 'BB_lower']] = ta.bbands(df['close'], length=20)
    macd = ta.macd(df['close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']
    df['Fibonacci_high'] = df['high'].max()
    df['Fibonacci_low'] = df['low'].min()
    return df

# Function to check volatility
def is_volatility_high(df, period=14, multiplier=1.5):
    df['true_range'] = df['high'] - df['low']
    avg_true_range = df['true_range'].rolling(period).mean().iloc[-1]
    current_range = df['high'].iloc[-1] - df['low'].iloc[-1]
    return current_range > multiplier * avg_true_range

# Function to check Bollinger Band breakout
def is_bollinger_breakout(df):
    last_row = df.iloc[-1]
    return last_row['close'] > last_row['BB_upper'] or last_row['close'] < last_row['BB_lower']

# Function to check MACD crossover
def is_macd_crossover(df):
    last_row = df.iloc[-1]
    previous_row = df.iloc[-2]
    return (previous_row['MACD'] < previous_row['MACD_signal'] and last_row['MACD'] > last_row['MACD_signal']) or \
           (previous_row['MACD'] > previous_row['MACD_signal'] and last_row['MACD'] < last_row['MACD_signal'])

# Function to check Fibonacci retracement levels
def is_at_fibonacci_level(df):
    last_close = df['close'].iloc[-1]
    fib_0_382 = df['Fibonacci_high'].iloc[-1] - 0.382 * (df['Fibonacci_high'].iloc[-1] - df['Fibonacci_low'].iloc[-1])
    fib_0_618 = df['Fibonacci_high'].iloc[-1] - 0.618 * (df['Fibonacci_high'].iloc[-1] - df['Fibonacci_low'].iloc[-1])
    return fib_0_382 <= last_close <= fib_0_618

# Function to send messages to Telegram
def send_to_telegram(message):
    bot = Bot(token=BOT_TOKEN)
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

# Main function to generate signals
def generate_trade_signal(df):
    if is_volatility_high(df) and is_macd_crossover(df) and is_bollinger_breakout(df) and is_at_fibonacci_level(df):
        # Determine direction (EMA crossover for trend confirmation)
        last_row = df.iloc[-1]
        if last_row['EMA9'] > last_row['EMA21']:
            return "🚀 BUY Signal (Volatility + MACD + Fibonacci + Bollinger) ✅"
        elif last_row['EMA9'] < last_row['EMA21']:
            return "🔻 SELL Signal (Volatility + MACD + Fibonacci + Bollinger) 🚫"
    return "No trade signal"

# Time-based control for active market hours
def is_active_market_hour():
    current_hour = datetime.utcnow().hour
    return (2 <= current_hour <= 8) or (13 <= current_hour <= 20)  # Asia and U.S. sessions

# Main loop to run the strategy
def main():
    while True:
        if is_active_market_hour():
            df = get_price_data()
            if df is not None:
                df = calculate_indicators(df)
                signal = generate_trade_signal(df)
                if signal != "No trade signal":
                    send_to_telegram(f"Trade Signal for {symbol}: {signal}")
            else:
                send_to_telegram("Error fetching data. Please check API connection.")
        else:
            print("Outside trading hours. Pausing bot...")
        time.sleep(300)  # Check every 5 minutes

# Run the script
if __name__ == "__main__":
    main()
