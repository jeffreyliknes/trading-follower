import time
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
params = {
    "encryptedUid": ["62C1878E2A5CB866C10640E7B9FED97C"],  # Trader's ID
    "tradeType": "ALL"
}

# Store the last state of positions
last_positions = {}

def fetch_and_notify():
    """
    Fetches trader positions and sends Telegram notifications for new/updated positions.
    """
    global last_positions
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                positions = data['data'][0]['positions']['perpetual']
                for position in positions:
                    symbol = position['symbol']
                    update_time = position['updateTimeStamp']

                    # Check if this symbol has new or updated data
                    if symbol not in last_positions or last_positions[symbol] != update_time:
                        # Format a message
                        message = (
                            f"🚨 Trade Update for {symbol}:\n"
                            f"  Entry Price: {position['entryPrice']}\n"
                            f"  Mark Price: {position['markPrice']}\n"
                            f"  PnL: {position['pnl']}\n"
                            f"  ROE: {position['roe']}\n"
                            f"  Amount: {position['amount']}\n"
                            f"  Leverage: {position['leverage']}\n"
                            f"  Long: {position['long']}\n"
                            f"  Short: {position['short']}\n"
                        )
                        # Send the message via Telegram
                        bot = Bot(token=BOT_TOKEN)
                        bot.send_message(chat_id=CHAT_ID, text=message)

                        # Update the last position for this symbol
                        last_positions[symbol] = update_time
            else:
                print("No positions found or data is unavailable.")
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error in fetch_and_notify: {e}")

def main():
    """
    Main function to run the fetch and notify loop.
    """
    while True:
        fetch_and_notify()
        time.sleep(300)  # Wait 5 minutes before fetching again

if __name__ == "__main__":
    main()
