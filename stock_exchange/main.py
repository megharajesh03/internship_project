from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
import requests

app = FastAPI()

# Replace with your actual PostgreSQL database connection URL
DATABASE_URL = "postgresql://myuser:12345*@localhost:5432/mydatabase"

# SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a SessionLocal class to handle database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Database instance for async operations
database = Database(DATABASE_URL)

# Declarative base for ORM models
Base = declarative_base()

# Define SQLAlchemy model for stock data
class StockData(Base):
    __tablename__ = "stock_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    date = Column(Date)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)

# Create the database tables based on the defined models
Base.metadata.create_all(bind=engine)

# API key for Alpha Vantage (replace with your actual API key)
API_KEY = "MOC8XDXRZBPN91B4"
BASE_URL = "https://www.alphavantage.co/query"

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/stocks/{symbol}")
async def get_stock_data(symbol: str):
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    # Check if the API responded with an error
    if "Error Message" in data:
        raise HTTPException(status_code=404, detail="Stock symbol not found")

    # Parse and store data in the database
    async with database.transaction():
        session = SessionLocal()
        try:
            for date, values in data["Time Series (Daily)"].items():
                db_data = StockData(
                    symbol=symbol,
                    date=date,
                    open_price=float(values["1. open"]),
                    high_price=float(values["2. high"]),
                    low_price=float(values["3. low"]),
                    close_price=float(values["4. close"]),
                    volume=int(values["5. volume"])
                )
                session.add(db_data)
            session.commit()
        finally:
            session.close()

    return {"message": f"Stock data for {symbol} stored successfully"}
