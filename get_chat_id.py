import asyncio
from telegram import Bot

# Replace with your bot token
BOT_TOKEN = "7814985675:AAG513pk7gWR01VFFeJL4JidKbtgQEV4YhI"

async def get_updates():
    bot = Bot(token=BOT_TOKEN)
    updates = await bot.get_updates()
    for update in updates:
        print(update)

if __name__ == "__main__":
    asyncio.run(get_updates())
