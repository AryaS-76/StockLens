import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
# === DB CONNECTION STRING ===

engine = create_engine(os.getenv("DATABASE_URL"))

# === Technical Indicator Calculations ===
def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss.replace(0, 0.001)
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2) if not rsi.isna().iloc[-1] else None

def calculate_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return round(macd.iloc[-1], 2), round(signal_line.iloc[-1], 2)

def calculate_sma(series, window=20):
    sma = series.rolling(window=window).mean()
    return round(sma.iloc[-1], 2) if not sma.isna().iloc[-1] else None

def calculate_ema(series, window=20):
    ema = series.ewm(span=window, adjust=False).mean()
    return round(ema.iloc[-1], 2) if not ema.isna().iloc[-1] else None

def assign_risk_category(metrics):
    score = 0
    pe = metrics.get("pe_ratio")
    market_cap = metrics.get("market_cap")
    dividend_yield = metrics.get("dividend_yield")
    book_value = metrics.get("book_value")
    close_price = metrics.get("close_price")

    # Fundamental scoring
    if pe is not None:
        if 10 <= pe <= 25:
            score += 2
        elif 25 < pe <= 40:
            score += 1

    if market_cap is not None:
        if market_cap > 5e12:
            score += 2
        elif 1e12 <= market_cap <= 5e12:
            score += 1

    if dividend_yield is not None:
        if dividend_yield > 0.025:
            score += 2
        elif 0.01 <= dividend_yield <= 0.025:
            score += 1

    if book_value is not None and close_price is not None:
        if book_value >= 0.9 * close_price:
            score += 2

    # Technical indicator scoring
    rsi = metrics.get("rsi")
    sma = metrics.get("sma_20")
    ema = metrics.get("ema_20")
    macd = metrics.get("macd")
    macd_signal = metrics.get("macd_signal")
    volatility = metrics.get("volatility")
    oi_score = metrics.get("oi_score")

    if rsi is not None:
        if 40 <= rsi <= 60:
            score += 2
        elif 30 <= rsi <= 70:
            score += 1

    if macd is not None and macd_signal is not None:
        if macd > macd_signal:
            score += 1

    if sma is not None and close_price is not None:
        if close_price > sma:
            score += 1

    if ema is not None and close_price is not None:
        if close_price > ema:
            score += 1

    if volatility is not None:
        if volatility < 2:
            score += 2
        elif 2 <= volatility <= 4:
            score += 1

    if oi_score is not None:
        if oi_score <= 20:
            score += 2
        elif 20 < oi_score <= 60:
            score += 1

    # === Sentiment-related scoring added here ===
    percent_change = metrics.get("percent_change")
    volume = metrics.get("volume")
    high_52w = metrics.get("high_52w")
    low_52w = metrics.get("low_52w")

    # 1. Percent Change
    if percent_change is not None:
        if percent_change > 2:
            score += 3
        elif 0 < percent_change <= 2:
            score += 1
        elif percent_change < -2:
            score -= 3
        elif -2 <= percent_change < 0:
            score -= 1

    # 2. Volume
    if volume is not None:
        if volume > 1e7:
            score += 2
        elif volume > 5e6:
            score += 1

    # 3. RSI sentiment extremes handled above (no change)

    # 4. MACD sentiment handled above (no change)

    # 5. Proximity to 52-week high/low
    if close_price and high_52w and low_52w:
        dist_to_high = (high_52w - close_price) / high_52w
        dist_to_low = (close_price - low_52w) / low_52w
        if dist_to_high is not None and dist_to_high < 0.05:
            score += 2
        if dist_to_low is not None and dist_to_low < 0.05:
            score -= 2

    # Final category assignment
    if score >= 10:
        return "risk_averse"
    elif 6 <= score < 10:
        return "moderate"
    else:
        return "risky"

# List of Nifty Symbols
nifty_symbols = [
    "ABB", "ADANIENSOL", "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ADANIPOWER",
    "AMBUJACEM", "APOLLOHOSP", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV",
    "BAJAJHFL", "BAJAJHLDNG", "BAJFINANCE", "BANKBARODA", "BEL", "BHARTIARTL",
    "BOSCHLTD", "BPCL", "BRITANNIA", "CANBK", "CGPOWER", "CHOLAFIN", "CIPLA", "COALINDIA",
    "DABUR", "DIVISLAB", "DLF", "DMART", "DRREDDY", "EICHERMOT", "GAIL", "GODREJCP",
    "GRASIM", "HAL", "HAVELLS", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO",
    "HINDUNILVR", "HYUNDAI", "ICICIBANK", "ICICIGI", "ICICIPRULI", "INDHOTEL", "INDIGO",
    "INDUSINDBK", "INFY", "IOC", "IRFC", "ITC", "JINDALSTEL", "JIOFIN", "JSWENERGY",
    "JSWSTEEL", "KOTAKBANK", "LICI", "LODHA", "LT", "LTIM", "M&M", "MARUTI", "MOTHERSON",
    "NAUKRI", "NESTLEIND", "NTPC", "ONGC", "PFC", "PIDILITIND", "PNB", "POWERGRID", "RECLTD",
    "RELIANCE", "SBILIFE", "SBIN", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SUNPHARMA",
    "SWIGGY", "TATACONSUM", "TATAMOTORS", "TATAPOWER", "TATASTEEL", "TCS", "TECHM", "TITAN",
    "TORNTPHARM", "TRENT", "TVSMOTOR", "ULTRACEMCO", "UNITDSPR", "VBL", "VEDL", "WIPRO",
    "ETERNAL", "ZYDUSLIFE"
]

# Function to fetch and store stock data
def fetch_and_store_stock_data():
    stock_data = []

    for symbol in nifty_symbols:
        try:
            stock = yf.Ticker(symbol + ".NS")
            hist = stock.history(period="3mo")
            info = stock.info

            if hist.empty:
                continue

            latest = hist.iloc[-1]
            rsi = calculate_rsi(hist["Close"])
            macd, macd_signal = calculate_macd(hist["Close"])
            sma = calculate_sma(hist["Close"])
            ema = calculate_ema(hist["Close"])

            metrics = {
                "pe_ratio": info.get("trailingPE"),
                "market_cap": info.get("marketCap"),
                "dividend_yield": info.get("dividendYield"),
                "book_value": info.get("bookValue"),
                "close_price": float(latest["Close"]),
                "rsi": rsi,
                "sma_20": sma,
                "ema_20": ema,
                "macd": macd,
                "macd_signal": macd_signal,
                "volatility": None,
                "oi_score": info.get("openInterest"),
                "percent_change": round(((latest["Close"] - latest["Open"]) / latest["Open"]) * 100, 2),
                "volume": latest["Volume"],
                "high_52w": info.get("fiftyTwoWeekHigh"),
                "low_52w": info.get("fiftyTwoWeekLow")
            }

            risk_category = assign_risk_category(metrics)

            stock_data.append({
                "symbol": symbol,
                "last_updated": datetime.utcnow(),
                "open_price": latest["Open"],
                "high_price": latest["High"],
                "low_price": latest["Low"],
                "close_price": latest["Close"],
                "volume": latest["Volume"],
                "value_crores": round((latest["Volume"] * latest["Close"]) / 1e7, 2),
                "percent_change": metrics["percent_change"],
                "price_change": latest["Close"] - latest["Open"],
                "high_52w": metrics["high_52w"],
                "low_52w": metrics["low_52w"],
                "rsi": rsi,
                "macd": macd,
                "macd_signal": macd_signal,
                "sma_20": sma,
                "ema_20": ema,
                "pe_ratio": info.get("trailingPE"),
                "eps": info.get("trailingEps"),
                "market_cap": info.get("marketCap"),
                "book_value": info.get("bookValue"),
                "dividend_yield": info.get("dividendYield"),
                "oi_score": metrics["oi_score"],
                "risk_category": risk_category
            })

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    df = pd.DataFrame(stock_data)
    df.to_sql("nifty_stock_data", con=engine, if_exists="replace", index=False)
    print("✅ Data successfully inserted into the database!")

if __name__ == "__main__":
    fetch_and_store_stock_data()
    print(f"📌 Running stock update at {datetime.now()}")
