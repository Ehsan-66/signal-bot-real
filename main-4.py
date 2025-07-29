
import os
import asyncio
import requests
import pandas as pd
from telegram import Bot
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD

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

def calculate_indicators(df):
    df["rsi"] = RSIIndicator(close=df["close"], window=14).rsi()
    df["ema"] = EMAIndicator(close=df["close"], window=20).ema_indicator()
    df["macd"] = MACD(close=df["close"]).macd_diff()
    return df

def generate_signal(df):
    reasons = []
    if df["rsi"].iloc[-1] < 30:
        signal = "BUY"
        reasons.append("RSI oversold")
    elif df["rsi"].iloc[-1] > 70:
        signal = "SELL"
        reasons.append("RSI overbought")
    else:
        signal = None

    if df["close"].iloc[-1] > df["ema"].iloc[-1]:
        if signal == "BUY":
            reasons.append("Above EMA")
    elif df["close"].iloc[-1] < df["ema"].iloc[-1]:
        if signal == "SELL":
            reasons.append("Below EMA")

    if df["macd"].iloc[-1] > 0 and signal == "BUY":
        reasons.append("MACD bullish")
    elif df["macd"].iloc[-1] < 0 and signal == "SELL":
        reasons.append("MACD bearish")

    if len(reasons) >= 2:
        return signal, reasons
    return None, []

async def fetch_data(symbol, interval):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=66&apikey={api_key}"
    response = await asyncio.to_thread(requests.get, url)
    data = response.json()
    if "values" not in data:
        return None
    df = pd.DataFrame(data["values"])
    df["close"] = df["close"].astype(float)
    df = df[::-1]
    return df

async def analyze_market():
    for symbol_key, symbol in symbols.items():
        for tf_key, tf_val in timeframes.items():
            df = await fetch_data(symbol, tf_val)
            if df is None:
                continue
            df = calculate_indicators(df)
            signal, reasons = generate_signal(df)
            if signal:
                entry = df["close"].iloc[-1]
                text = f"📊 Signal for {symbol_key} on {tf_key} timeframe\nAction: {signal}\nEntry: {entry}\nReason: {' | '.join(reasons)}"
                await bot.send_message(chat_id=chat_id, text=text)

asyncio.run(analyze_market())
    