from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from databases import Database
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

app = FastAPI()

# Database URL and connection setup
DATABASE_URL = "postgresql://myuser:12345*@localhost:5432/mydatabase"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
database = Database(DATABASE_URL)
Base = declarative_base()

# SQLAlchemy model for stock data
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

# Pydantic model for stock data response
class StockDataResponse(BaseModel):
    symbol: str
    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int

    class Config:
        orm_mode = True

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/stocks/{symbol}", response_model=list[StockDataResponse])
async def read_stock_data(symbol: str, db: Session = Depends(get_db)):
    data = db.query(StockData).filter(StockData.symbol == symbol).all()
    if not data:
        raise HTTPException(status_code=404, detail="Stock data not found")
    return data
