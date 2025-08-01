# StockLens
 Investing that understands you

StockLens is a stock recommendation platform that provides personalized investment insights based on risk profiling and real-time market analysis. It leverages a combination of fundamental, technical, and sentiment analysis to generate smart, explainable recommendations for Nifty 100 stocks.

---

🚀 Features

- 🧠 AI-based stock rating (Buy / Hold / Sell)
- 📊 Real-time analysis using:
  - Fundamental metrics (PE, Market Cap, Dividend Yield)
  - Technical indicators (RSI, MACD, SMA, EMA)
  - Sentiment & volatility
- 🧍‍♂️ Risk profiling: Classify users into Conservative, Moderate, or Aggressive
- 💬 Natural language explanations for each stock recommendation
- 📈 Live stock data integration using `yfinance`
- 🖼️ Intuitive frontend UI (HTML/CSS based on Figma)
- 🔗 REST API built with FastAPI

---

📁 Project Structure
Lens/
├── backend/ # FastAPI backend with analysis & DB logic
│ ├── main.py
│ ├── stock_data.py
│ ├── database.py
│ ├── scheduler.py
│ └── ...
├── frontend/ # Static frontend HTML/CSS (questionnaire & results)
├── requirements.txt # Python dependencies
├── .gitignore # Git ignore rules
└── README.md # Project documentation

---

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS (based on Figma design)
- **Backend:** FastAPI, SQLAlchemy, Pandas, Uvicorn
- **Database:** SQLite (can be upgraded to PostgreSQL)
- **Data Source:** yfinance (Nifty 100 stocks)
- **AI:** Agentic reasoning (LLMs for explanation generation)
- **Deployment Ready:** Local or cloud-ready API

---

## 📦 Getting Started

### 🔧 Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### ⚙️ Setup Instructions

```bash
# 1. Clone the wrepo
git clone https://github.com/YOUR_USERNAME/StockLens.git
cd StockLens

# 2. Create and activate virtual environment
python -m venv env
source env/bin/activate   # On Windows: env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
touch backend/.env
# Add: DATABASE_URL=sqlite:///stocklens.db

# 5. Run the backend
cd backend
uvicorn main:app --reload

# 6. Open the frontend (static files in /frontend)
```
🧠 How It Works
User answers a risk profiling questionnaire

Backend fetches and processes real-time stock data

Stocks are scored based on fundamental, technical, and sentiment metrics

Each stock is matched to a user's risk profile

AI explains each recommendation in human-readable text

📌 Example Risk Categories
Risk Averse: Blue-chip, low volatility, high dividend

Moderate: Balanced growth and stability

Aggressive: High momentum, small-cap, volatile stocks

🧪 Future Enhancements
 Add portfolio tracking

 Integrate news sentiment analysis via NLP

 Add login & user history

 Cloud deployment via Render/Heroku

 Portfolio optimization engine
