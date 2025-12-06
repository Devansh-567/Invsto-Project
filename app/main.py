from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import os

from app.database import get_db, init_db, StockData
from app.models import StockDataCreate, StockDataResponse, StrategyPerformance
from app.strategy import calculate_strategy_performance

app = FastAPI(
    title="Trading Strategy API",
    description="API for stock data management and Moving Average Crossover strategy",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and load CSV data on startup"""
    init_db()
    
    # Load data from CSV if database is empty
    db = next(get_db())
    count = db.query(StockData).count()
    
    if count == 0:
        print("Loading data from CSV...")
        load_csv_data(db)
        print(f"Loaded {db.query(StockData).count()} records")
    
    db.close()


def load_csv_data(db: Session):
    """Load data from CSV file"""
    csv_file = "data.csv"
    
    if not os.path.exists(csv_file):
        print(f"Warning: {csv_file} not found. Please create it with the provided data.")
        return
    
    df = pd.read_csv(csv_file)
    
    for _, row in df.iterrows():
        stock_data = StockData(
            datetime=pd.to_datetime(row['datetime']),
            open=float(row['open']),
            high=float(row['high']),
            low=float(row['low']),
            close=float(row['close']),
            volume=int(row['volume']),
            instrument=row['instrument']
        )
        db.add(stock_data)
    
    db.commit()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Trading Strategy API",
        "version": "1.0.0",
        "endpoints": {
            "GET /data": "Fetch all stock data",
            "POST /data": "Add new stock data",
            "GET /strategy/performance": "Get strategy performance"
        }
    }


@app.get("/data", response_model=List[StockDataResponse], tags=["Data"])
async def get_all_data(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Fetch all stock data with pagination
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    data = db.query(StockData).order_by(StockData.datetime).offset(skip).limit(limit).all()
    return data


@app.post("/data", response_model=StockDataResponse, status_code=status.HTTP_201_CREATED, tags=["Data"])
async def create_data(
    stock_data: StockDataCreate,
    db: Session = Depends(get_db)
):
    """
    Add new stock data record
    
    - **datetime**: Timestamp of the data point
    - **open**: Opening price
    - **high**: Highest price
    - **low**: Lowest price
    - **close**: Closing price
    - **volume**: Trading volume
    - **instrument**: Stock symbol
    """
    # Validate using Pydantic v2 (ensures field validators run)
    validated_data = StockDataCreate.model_validate(stock_data.model_dump())

    db_stock = StockData(**validated_data.model_dump())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock



@app.get("/strategy/performance", response_model=StrategyPerformance, tags=["Strategy"])
async def get_strategy_performance(
    short_window: int = 20,
    long_window: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get Moving Average Crossover strategy performance
    
    - **short_window**: Short-term moving average window (default: 20)
    - **long_window**: Long-term moving average window (default: 50)
    """
    if short_window >= long_window:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Short window must be less than long window"
        )
    
    # Fetch all data
    data = db.query(StockData).order_by(StockData.datetime).all()
    
    if len(data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data found in database"
        )
    
    # Convert to dict
    data_dicts = [record.to_dict() for record in data]
    
    # Calculate performance
    performance = calculate_strategy_performance(data_dicts, short_window, long_window)
    
    if "error" in performance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=performance["error"]
        )
    
    return performance


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)