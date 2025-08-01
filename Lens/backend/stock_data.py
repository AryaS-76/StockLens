import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import StockPrice

def fetch_stock_data(stock_symbol: str):
    """
    Fetches real-time stock data for a given stock symbol from Yahoo Finance.
    """
    try:
        stock = yf.Ticker(stock_symbol)
        data = stock.history(period="1d")  # Fetch today's data

        if data.empty:
            return {"error": f"No data found for the stock symbol: {stock_symbol}"}

        latest = data.iloc[-1]

        return {
            "stock_symbol": stock_symbol,
            "date": latest.name.strftime('%Y-%m-%d'),
            "open_price": float(latest["Open"]),
            "high_price": float(latest["High"]),
            "low_price": float(latest["Low"]),
            "close_price": float(latest["Close"]),
            "volume": int(latest["Volume"])
        }
    except Exception as e:
        return {"error": str(e)}

def fetch_and_store_stock_data(stock_symbol: str):
    """
    Fetches real-time stock data and stores it in PostgreSQL.
    """
    stock_data = fetch_stock_data(stock_symbol)

    # Check if an error occurred during data fetching
    if "error" in stock_data:
        print(stock_data["error"])
        return

    # Print the fetched data for reference
    print(f"Fetched data: {stock_data}")

    # Save to Database
    try:
        db: Session = SessionLocal()
        stock_entry = StockPrice(
            stock_symbol=stock_data["stock_symbol"],
            date=stock_data["date"],
            open_price=stock_data["open_price"],
            high_price=stock_data["high_price"],
            low_price=stock_data["low_price"],
            close_price=stock_data["close_price"],
            volume=stock_data["volume"]
        )
        db.add(stock_entry)
        db.commit()
        db.close()
        print(f"Stock data for {stock_symbol} stored successfully.")
    except Exception as e:
        print(f"Error storing data: {str(e)}")

if __name__ == "_main_":
    # Get the stock ticker dynamically from the user
    ticker = input("Enter the stock ticker (e.g., RELIANCE.NS): ")
    fetch_and_store_stock_data(ticker)