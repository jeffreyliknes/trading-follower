import asyncio
from telegram import Bot

BOT_TOKEN = "7814985675:AAG513pk7gWR01VFFeJL4JidKbtgQEV4YhI"
CHAT_ID = 6458736937  # Replace with your chat ID

async def send_test_message():
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text="Test message from your bot!")

if __name__ == "__main__":
    asyncio.run(send_test_message())
