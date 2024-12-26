import time
import requests
import asyncio
from telegram import Bot

# Telegram Bot Token and Chat ID
BOT_TOKEN = "7814985675:AAG513pk7gWR01VFFeJL4JidKbtgQEV4YhI"
CHAT_ID = 6458736937  # Replace with your actual chat ID


# Define the API endpoint and headers
url = "https://binance-futures-leaderboard1.p.rapidapi.com/v2/getTraderPositions"
headers = {
    "X-RapidAPI-Key": "889bb72fc8mshcde845fdddbc383p18eebcjsnd2997055ac07",  # Your API Key
    "X-RapidAPI-Host": "binance-futures-leaderboard1.p.rapidapi.com"
}
params = {
    "encryptedUid": ["62C1878E2A5CB866C10640E7B9FED97C"],  # Trader's ID
    "tradeType": "ALL"
}

# Store the last state of positions
last_positions = {}

async def fetch_and_notify():
    global last_positions
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
                    await bot.send_message(chat_id=CHAT_ID, text=message)

                    # Update the last position for this symbol
                    last_positions[symbol] = update_time
        else:
            print("No positions found or data is unavailable.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

async def main():
    while True:
        await fetch_and_notify()
        await asyncio.sleep(300)  # Wait 5 minutes before fetching again

# Run the main loop
if __name__ == "__main__":
    asyncio.run(main())
