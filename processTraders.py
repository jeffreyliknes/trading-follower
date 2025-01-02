import json
import requests
from telegram import Bot

# Telegram Bot Token and Chat ID
BOT_TOKEN = "7814985675:AAG513pk7gWR01VFFeJL4JidKbtgQEV4YhI"
CHAT_ID = 6458736937  # Replace with your actual chat ID

# API Endpoint and Headers
url = "https://binance-futures-leaderboard1.p.rapidapi.com/v2/getTraderPositions"
headers = {
    "X-RapidAPI-Key": "3b165f4f65mshf704118488ccc4p1b2b96jsnb0b9cc0930c7",  # Updated API token
    "X-RapidAPI-Host": "binance-futures-leaderboard1.p.rapidapi.com"
}

# Load Trader IDs from JSON
with open("topTraders.json", "r") as file:
    trader_ids = json.load(file)["trader_ids"]

# Fetch Positions for Each Trader
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

# Find Common Trades
def find_common_trades(trader_ids):
    all_positions = {}
    for trader_id in trader_ids:
        positions = fetch_positions(trader_id)
        if not positions:
            continue
        for position in positions:
            symbol = position["symbol"]
            side = "Long" if position["amount"] > 0 else "Short"  # Determine trade side
            if symbol not in all_positions:
                all_positions[symbol] = {"Long": 0, "Short": 0}
            all_positions[symbol][side] += 1
    # Filter symbols traded by more than one trader
    common_trades = {symbol: sides for symbol, sides in all_positions.items() if sum(sides.values()) > 1}
    return common_trades

# Send Summary to Telegram
def send_to_telegram(message):
    bot = Bot(token=BOT_TOKEN)
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

# Main Function
def main():
    common_trades = find_common_trades(trader_ids)
    if common_trades:
        message = "📊 Common Trades:\n\n"
        for symbol, sides in common_trades.items():
            total_traders = sides["Long"] + sides["Short"]
            message += (
                f"Symbol: {symbol}\n"
                f"Traders: {total_traders}\n"
                f"  Long: {sides['Long']}\n"
                f"  Short: {sides['Short']}\n\n"
            )
        if len(message) > 4096:  # Telegram message limit
            message = message[:4093] + "..."
        send_to_telegram(message)
    else:
        send_to_telegram("No common trades found.")

# Run the Script
if __name__ == "__main__":
    main()
