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

def calculate_indicators(df):
    df["EMA20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["MA50"] = df["close"].rolling(window=50).mean()
    df["RSI"] = 100 - (100 / (1 + df["close"].pct_change().rolling(window=14).mean()))
    exp1 = df["close"].ewm(span=12, adjust=False).mean()
    exp2 = df["close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    return df

def generate_signal(df):
    if df is None or len(df) < 50:
        return None, []

    latest = df.iloc[-1]
    signal = None
    reasons = []

    # EMA & MA cross
    if latest["EMA20"] > latest["MA50"]:
        signal = "BUY"
        reasons.append("EMA > MA")
    elif latest["EMA20"] < latest["MA50"]:
        signal = "SELL"
        reasons.append("EMA < MA")

    # RSI confirmation
    if latest["RSI"] < 30:
        signal = "BUY"
        reasons.append("RSI oversold")
    elif latest["RSI"] > 70:
        signal = "SELL"
        reasons.append("RSI overbought")

    # MACD confirmation
    if latest["MACD"] > latest["Signal"]:
        if signal == "BUY":
            reasons.append("MACD bullish")
    elif latest["MACD"] < latest["Signal"]:
        if signal == "SELL":
            reasons.append("MACD bearish")

    if len(reasons) >= 2:
        return signal, reasons
    return None, []

async def fetch_data(symbol, interval):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=100&apikey={api_key}"
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
                price = df["close"].iloc[-1]
                text = f"📊 Signal for {symbol_key} on {tf_key}\nAction: {signal}\nEntry: {price}\nReasons: " + ", ".join(reasons)
                await bot.send_message(chat_id=chat_id, text=text)

asyncio.run(analyze_market())
