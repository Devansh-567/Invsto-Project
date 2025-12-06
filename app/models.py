from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List


class StockDataCreate(BaseModel):
    datetime: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)
    instrument: str = Field(default="HINDALCO")

    # Validate that high >= low
    @field_validator("high")
    @classmethod
    def validate_high(cls, v, info):
        low = info.data.get("low")
        if low is not None and v < low:
            raise ValueError("High must be >= low")
        return v

    # Validate that low <= high
    @field_validator("low")
    @classmethod
    def validate_low(cls, v, info):
        high = info.data.get("high")
        if high is not None and v > high:
            raise ValueError("Low must be <= high")
        return v

    model_config = {
        "from_attributes": True
    }


class StockDataResponse(StockDataCreate):
    id: int


class StrategyPerformance(BaseModel):
    total_trades: int
    profitable_trades: int
    losing_trades: int
    win_rate: float
    total_return: float
    signals: List

    # Ensure win_rate is always float
    @field_validator("win_rate")
    @classmethod
    def ensure_float(cls, v):
        return float(v)
