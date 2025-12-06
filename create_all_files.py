import os

# Ensure directories exist
os.makedirs('app', exist_ok=True)
os.makedirs('tests', exist_ok=True)

files = {
    'app/__init__.py': '',
    'tests/__init__.py': '',
    'app/database.py': '''from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tradinguser:tradingpass@localhost:5432/tradingdb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class StockData(Base):
    __tablename__ = "stock_data"

    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    instrument = Column(String, nullable=False, default="HINDALCO")

    def to_dict(self):
        return {
            "id": self.id,
            "datetime": self.datetime.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "instrument": self.instrument
        }


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
''',
    'app/models.py': '''from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class StockDataCreate(BaseModel):
    datetime: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)
    instrument: str = Field(default="HINDALCO")

    @validator('high')
    def high_must_be_highest(cls, v, values):
        if 'low' in values and v < values['low']:
            raise ValueError('High must be >= low')
        return v

    class Config:
        from_attributes = True


class StockDataResponse(StockDataCreate):
    id: int


class StrategyPerformance(BaseModel):
    total_trades: int
    profitable_trades: int
    losing_trades: int
    win_rate: float
    total_return: float
    signals: list
''',
}

for filepath, content in files.items():
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created {filepath}")

print("\n🎉 Core files created!")