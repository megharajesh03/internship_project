from fastapi import FastAPI
from databases import Database
import requests
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date

app = FastAPI()

DATABASE_URL = "postgresql://myuser:12345*@localhost/mydatabase"
database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
metadata = MetaData()

stocks = Table(
    "stocks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("symbol", String),
    Column("date", Date),
    Column("open", String),
    Column("high", String),
    Column("low", String),
    Column("close", String),
    Column("volume", String),
)

metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
def read_root():
    return {"Hello": "World"}

API_KEY = "your_alpha_vantage_api_key"

def fetch_stock_data(symbol: str):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data

async def store_stock_data(symbol: str, data: dict):
    for date, values in data['Time Series (Daily)'].items():
        query = stocks.insert().values(
            symbol=symbol,
            date=date,
            open=values['1. open'],
            high=values['2. high'],
            low=values['3. low'],
            close=values['4. close'],
            volume=values['5. volume'],
        )
        await database.execute(query)

@app.get("/stocks/{symbol}")
async def get_stock_data(symbol: str):
    query = stocks.select().where(stocks.c.symbol == symbol)
    result = await database.fetch_all(query)
    return {"data": result}
