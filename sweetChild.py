import json
import requests
from telegram import Bot
import time

# Telegram Bot Token and Chat ID
BOT_TOKEN = "7814985675:AAG513pk7gWR01VFFeJL4JidKbtgQEV4YhI"
CHAT_ID = 6458736937  # Replace with your actual chat ID

# API Endpoint and Headers
url = "https://binance-futures-leaderboard1.p.rapidapi.com/v2/getTraderPositions"
headers = {
    "X-RapidAPI-Key": "889bb72fc8mshcde845fdddbc383p18eebcjsnd2997055ac07",
    "X-RapidAPI-Host": "binance-futures-leaderboard1.p.rapidapi.com"
}

# Trader ID to monitor
TRADER_ID = "62C1878E2A5CB866C10640E7B9FED97C"

# Track the trader's open positions
previous_positions = {}

# Fetch Positions for Trader
def fetch_positions(trader_id):
    params = {"encryptedUid": trader_id, "tradeType": "ALL"}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "data" in data:
                return data["data"][0]["positions"]["perpetual"]
        print(f"Error fetching positions for trader {trader_id}: {response.text}")
    except Exception as e:
        print(f"Exception fetching positions for trader {trader_id}: {e}")
    return []

# Send Message to Telegram
def send_to_telegram(message):
    bot = Bot(token=BOT_TOKEN)
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

# Monitor Trades
def monitor_trades():
    global previous_positions
    
    positions = fetch_positions(TRADER_ID)
    if not positions:
        print("No positions found.")
        return

    current_positions = {position["symbol"]: position for position in positions}

    # Detect new trades
    for symbol, position in current_positions.items():
        if symbol not in previous_positions:
            side = "Long" if position["amount"] > 0 else "Short"
            message = f"\u2705 New Trade Alert:\nSymbol: {symbol}\nSide: {side}\nAmount: {position['amount']}\nEntry Price: {position['entryPrice']}"
            send_to_telegram(message)

    # Detect closed trades
    for symbol in list(previous_positions.keys()):
        if symbol not in current_positions:
            closed_position = previous_positions[symbol]
            side = "Long" if closed_position["amount"] > 0 else "Short"
            message = f"\u274C Trade Closed:\nSymbol: {symbol}\nSide: {side}\nAmount: {closed_position['amount']}"
            send_to_telegram(message)

    # Update previous positions
    previous_positions = current_positions

# Main Function
def main():
    print("Monitoring trades...")
    while True:
        monitor_trades()
        time.sleep(60)  # Check every minute

# Run the Script
if __name__ == "__main__":
    main()
