import os
import asyncio
import pandas as pd
import requests
from telegram import Bot

bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")
api_key = os.getenv("TWELVE_DATA_KEY")

symbols = {
    "XAUUSD": "XAU/USD",
    "EURUSD": "EUR/USD",
    "GBPJPY": "GBP/JPY",
    "BTCUSD": "BTC/USD",
    "USDJPY": "USD/JPY",
    "US30": "DJI"
}

timeframes = {
    "M5": "5min",
    "M15": "15min",
    "M30": "30min"
}

bot = Bot(token=bot_token)

async def fetch_data(symbol, interval):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=6&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    if "values" not in data:
        return None
    df = pd.DataFrame(data["values"])
    df["close"] = df["close"].astype(float)
    return df[::-1]  # reverse to ascending order

def calculate_signal(df):
    if df is None or len(df) < 6:
        return None
    last = df["close"].iloc[-1]
    prev = df["close"].iloc[-2]
    if last > prev:
        return "BUY"
    elif last < prev:
        return "SELL"
    return None

async def analyze_market():
    for symbol_key, symbol in symbols.items():
        for tf_key, tf_val in timeframes.items():
            df = await asyncio.to_thread(fetch_data, symbol, tf_val)
            signal = calculate_signal(df)
            if signal:
                entry = df["close"].iloc[-1]
                text = f"📈 Signal for {symbol_key} on {tf_key} timeframe\nAction: {signal}\nEntry: {entry}"
                await bot.send_message(chat_id=chat_id, text=text)

asyncio.run(analyze_market())
