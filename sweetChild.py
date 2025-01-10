import http.client
import json
from telegram import Bot
import time

# Telegram Bot Token and Chat ID
BOT_TOKEN = "7814985675:AAG513pk7gWR01VFFeJL4JidKbtgQEV4YhI"
CHAT_ID = 6458736937  # Replace with your actual chat ID

# API Configuration
API_HOST = "binance-futures-leaderboard1.p.rapidapi.com"
API_KEY = "3b165f4f65mshfb704118488ccc4p1b2b96jsnb0b9cc0930c7"

# Trader ID to monitor
TRADER_ID = "62C1878E2A5CB866C10640E7B9FED97C"

# Track the trader's open positions
previous_positions = {}

# Fetch Positions for Trader (tradeType=ALL)
def fetch_positions(trader_id):
    conn = http.client.HTTPSConnection(API_HOST)
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }
    # Corrected endpoint with encryptedUid
    endpoint = f"/v2/getTraderPositions?tradeType=ALL&encryptedUid={trader_id}"

    try:
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        response = json.loads(data.decode("utf-8"))

        print("Full API Response:")
        print(json.dumps(response, indent=4))

        if response.get("success") and "data" in response:
            return response["data"][0]["positions"]["perpetual"]  # Corrected path to get perpetual contracts
        else:
            print(f"Error: {response.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Exception fetching positions: {e}")
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
        time.sleep(600)  # Check every minute

# Run the Script
if __name__ == "__main__":
    main()
