import requests
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.scheduler import start as start_scheduler
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
load_dotenv()

# Your Google API key for Gemini model (replace with your actual key)


# Gemini model endpoint URL
GEMINI_MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={os.getenv("GOOGLE_API_KEY")}"

app = FastAPI()

# Allow all origins for local dev (you can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model to receive frontend result
class RiskFormResult(BaseModel):
    total_score: int

# === Risk Classification Logic ===
def classify_risk(total_score: int) -> str:
    if total_score <= 40:
        return "risk_averse"
    elif total_score <= 80:
        return "moderate"
    else:
        return "risky"

# === API Endpoint ===
@app.post("/recommend/")
def recommend_stocks(result: RiskFormResult, db: Session = Depends(get_db)):
    """
    Accepts total risk score from frontend, classifies risk type, 
    fetches compatible stocks, and uses Gemini API to explain recommendations.
    """
    risk_type = classify_risk(result.total_score)

    # Fetch stocks from database
    query = text(
        "SELECT symbol, open_price, close_price, percent_change, pe_ratio, market_cap, rsi, macd, risk_category "
        "FROM nifty_stock_data WHERE risk_category = :risk_type"
    )
    stocks = db.execute(query, {"risk_type": risk_type}).fetchall()

    if not stocks:
        raise HTTPException(status_code=404, detail="No stocks found for your risk category.")

    top_stocks = stocks[:5]  # Limit to 5 for explanation

    # Prepare prompt for Gemini
    stock_list = "\n".join(
        [f"{row.symbol} (PE: {row.pe_ratio}, RSI: {row.rsi}, Risk: {row.risk_category})" for row in top_stocks]
    )
    prompt = (
        f"The user has a {risk_type} risk profile. Recommend the following stocks and explain briefly why they match this profile:\n"
        f"{stock_list}"
    )

    gpt_response = get_gemini_recommendation(prompt)

    return {
        "risk_profile": risk_type,
        "recommended_stocks": [
            {
                "symbol": row.symbol,
                "open_price": row.open_price,
                "close_price": row.close_price,
                "percent_change": row.percent_change,
            }
            for row in top_stocks
        ],
        "explanation": gpt_response.get("explanation", "No explanation available."),
    }


# === Gemini API call function ===
def get_gemini_recommendation(prompt: str):
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_MODEL_URL, json=payload)
        response.raise_for_status()
        result = response.json()

        # Extract explanation text from Gemini response
        explanation = ""
        candidates = result.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            explanation = " ".join(part.get("text", "") for part in parts)

        return {"explanation": explanation.strip()}

    except requests.exceptions.RequestException as e:
        print(f"Gemini API Error: {str(e)}")
        return {"error": str(e)}


# === Start scheduler for background DB updates ===
start_scheduler()
