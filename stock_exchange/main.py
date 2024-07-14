from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
from fastapi.templating import Jinja2Templates
import requests
from datetime import datetime

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
    date = Column(DateTime)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    timestamp = Column(DateTime)

# Create the database tables based on the defined models
Base.metadata.create_all(bind=engine)

# API key for Alpha Vantage
API_KEY = "MOC8XDXRZBPN91B4"
BASE_URL = "https://www.alphavantage.co/query"

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/stocks/{symbol}")
async def get_stock_data(symbol: str):
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "5min", #### the chosen interval
        "apikey": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "Error Message" in data:
        raise HTTPException(status_code=404, detail="Stock symbol not found")

    if "Time Series (5min)" not in data:  ### the chosen interval
        raise HTTPException(status_code=500, detail="Unexpected response from API")

    async with database.transaction():
        session = SessionLocal()
        try:
            for date_str, values in data["Time Series (5min)"].items():  ### the chosen interval
                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                existing_data = session.query(StockData).filter(
                    StockData.symbol == symbol,
                    StockData.date == date
                ).first()

                if not existing_data:
                    db_data = StockData(
                        symbol=symbol,
                        date=date,
                        open_price=float(values["1. open"]),
                        high_price=float(values["2. high"]),
                        low_price=float(values["3. low"]),
                        close_price=float(values["4. close"]),
                        volume=int(values["5. volume"]),
                        timestamp=date  # timestamp from the API
                    )
                    session.add(db_data)
            session.commit()
        finally:
            session.close()

    return {"message": f"Stock data for {symbol} stored successfully"}

@app.get("/stocks/data/{symbol}", response_class=HTMLResponse)
async def get_stored_stock_data(request: Request, symbol: str):
    session = SessionLocal()
    try:
        stock_data = session.query(StockData).filter(StockData.symbol == symbol).all()
        if not stock_data:
            raise HTTPException(status_code=404, detail="Stock data not found")

        # Prepare data for the chart
        dates = [data.date.isoformat() for data in stock_data]  # ISO format for timestamp
        close_prices = [data.close_price for data in stock_data]

        # Debug logs
        print("Retrieved Dates: ", dates)
        print("Retrieved Close Prices: ", close_prices)

        return templates.TemplateResponse("stock_data.html", {
            "request": request,
            "symbol": symbol,
            "dates": dates,
            "close_prices": close_prices
        })
    finally:
        session.close()
