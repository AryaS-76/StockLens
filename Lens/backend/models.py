from sqlalchemy import Column, Integer, String, Float, Date, TIMESTAMP
from backend.database import Base  # ✅ Correct absolute import

class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    stock_symbol = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)


