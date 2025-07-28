import os
import asyncio
from telegram import Bot
import pandas as pd
import requests
from datetime import datetime, timedelta

symbols = {
    "XAUUSD": "XAUUSD",
    "EURUSD": "EURUSD",
    "GBPJPY": "GBPJPY",
    "BTCUSD": "BTCUSD",
    "USDJPY": "USDJPY",
    "US30": "US30"
}

timeframes = ["M5", "M15", "M30"]
bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")
bot = Bot(token=bot_token)

async def fetch_data(symbol, interval):
    # Simulated dummy data (in real code you'd use an API)
    df = pd.DataFrame({
        "close": [1.2300, 1.2320, 1.2340, 1.2360, 1.2380, 1.2400],
    })
    return df

def calculate_signal(df):
    if len(df) < 6:
        return None
    last_close = df["close"].iloc[-1]
    prev_close = df["close"].iloc[-2]
    if last_close > prev_close:
        return "buy"
    elif last_close < prev_close:
        return "sell"
    return None

async def analyze_market():
    for symbol in symbols:
        for tf in timeframes:
            df = await fetch_data(symbol, tf)
            signal = calculate_signal(df)
            if signal:
                text = f"📊 Signal for {symbol} on {tf} timeframe\nAction: {signal.upper()}\nEntry: {df['close'].iloc[-1]}"
                await bot.send_message(chat_id=chat_id, text=text)

asyncio.run(analyze_market())
