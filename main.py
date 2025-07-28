import os
from telegram import Bot

# گرفتن توکن و چت آیدی از تنظیمات رندر
bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

# ساخت ربات
bot = Bot(token=bot_token)

# ارسال پیام تست به تلگرام شما
bot.send_message(chat_id=chat_id, text="✅ ربات با موفقیت اجرا شد و به تلگرام وصله!")
