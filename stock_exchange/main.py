from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

API_KEY = "MOC8XDXRZBPN91B4"
BASE_URL = "https://www.alphavantage.co/query"

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

    return data
