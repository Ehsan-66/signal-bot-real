
import os
import asyncio
import pandas as pd
import requests
from telegram import Bot
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator, SMAIndicator

# گرفتن متغیرها از محیط
bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")
api_key = os.getenv("TWELVE_DATA_KEY")

bot = Bot(token=bot_token)

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

async def fetch_data(symbol, interval):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=100&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    if "values" not in data:
        return None
    df = pd.DataFrame(data["values"])
    df["close"] = pd.to_numeric(df["close"], errors='coerce')
    df = df[::-1].dropna()
    return df

def calculate_signal(df):
    if df is None or len(df) < 50:
        return None

    rsi = RSIIndicator(df["close"]).rsi()
    macd = MACD(df["close"]).macd_diff()
    ema = EMAIndicator(df["close"]).ema_indicator()
    ma = SMAIndicator(df["close"]).sma_indicator()

    if rsi.iloc[-1] > 50 and macd.iloc[-1] > 0 and df["close"].iloc[-1] > ema.iloc[-1] > ma.iloc[-1]:
        return "BUY"
    elif rsi.iloc[-1] < 50 and macd.iloc[-1] < 0 and df["close"].iloc[-1] < ema.iloc[-1] < ma.iloc[-1]:
        return "SELL"
    return None

async def analyze_market():
    for symbol_key, symbol_val in symbols.items():
        for tf_key, tf_val in timeframes.items():
            df = await asyncio.to_thread(fetch_data, symbol_val, tf_val)
            signal = calculate_signal(df)
            if signal:
                entry = df["close"].iloc[-1]
                text = f"📉 Signal for {symbol_key} on {tf_key} timeframe\nAction: {signal}\nEntry: {entry}"
                await bot.send_message(chat_id=chat_id, text=text)

asyncio.run(analyze_market())
