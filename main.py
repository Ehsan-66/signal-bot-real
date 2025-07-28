import os
import asyncio
from telegram import Bot

# گرفتن توکن و چت آیدی از محیط
bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")
bot = Bot(token=bot_token)

async def send_test_message():
    await bot.send_message(chat_id=chat_id, text="✅ ربات با موفقیت اجرا شد و به تلگرام وصله!")

# اجرای تابع
asyncio.run(send_test_message())
