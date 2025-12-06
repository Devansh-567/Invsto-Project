import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.main import app
from app.database import Base, get_db, StockData

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint():
    """Test root endpoint returns correct information"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Trading Strategy API"


def test_create_data_valid(test_db):
    """Test creating valid stock data"""
    data = {
        "datetime": "2024-01-01T00:00:00",
        "open": 100.0,
        "high": 105.0,
        "low": 99.0,
        "close": 103.0,
        "volume": 1000000,
        "instrument": "TEST"
    }
    response = client.post("/data", json=data)
    assert response.status_code == 201
    assert response.json()["open"] == 100.0
    assert response.json()["instrument"] == "TEST"


def test_create_data_invalid_negative_price(test_db):
    """Test validation: negative prices should fail"""
    data = {
        "datetime": "2024-01-01T00:00:00",
        "open": -100.0,
        "high": 105.0,
        "low": 99.0,
        "close": 103.0,
        "volume": 1000000,
        "instrument": "TEST"
    }
    response = client.post("/data", json=data)
    assert response.status_code == 422


def test_create_data_invalid_high_low(test_db):
    """Test validation: high must be >= low"""
    data = {
        "datetime": "2024-01-01T00:00:00",
        "open": 100.0,
        "high": 95.0,  # High less than low
        "low": 99.0,
        "close": 98.0,
        "volume": 1000000,
        "instrument": "TEST"
    }
    response = client.post("/data", json=data)
    assert response.status_code == 422


def test_create_data_invalid_negative_volume(test_db):
    """Test validation: negative volume should fail"""
    data = {
        "datetime": "2024-01-01T00:00:00",
        "open": 100.0,
        "high": 105.0,
        "low": 99.0,
        "close": 103.0,
        "volume": -1000,
        "instrument": "TEST"
    }
    response = client.post("/data", json=data)
    assert response.status_code == 422


def test_get_data_empty(test_db):
    """Test getting data when database is empty"""
    response = client.get("/data")
    assert response.status_code == 200
    assert response.json() == []


def test_get_data_with_records(test_db):
    """Test getting data after adding records"""
    # Add test data
    data = {
        "datetime": "2024-01-01T00:00:00",
        "open": 100.0,
        "high": 105.0,
        "low": 99.0,
        "close": 103.0,
        "volume": 1000000,
        "instrument": "TEST"
    }
    client.post("/data", json=data)
    
    response = client.get("/data")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["open"] == 100.0


def test_get_data_pagination(test_db):
    """Test pagination parameters"""
    # Add multiple records
    for i in range(5):
        data = {
            "datetime": f"2024-01-0{i+1}T00:00:00",
            "open": 100.0 + i,
            "high": 105.0 + i,
            "low": 99.0 + i,
            "close": 103.0 + i,
            "volume": 1000000,
            "instrument": "TEST"
        }
        client.post("/data", json=data)
    
    response = client.get("/data?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_strategy_performance_insufficient_data(test_db):
    """Test strategy with insufficient data"""
    # Add only a few records
    for i in range(10):
        data = {
            "datetime": f"2024-01-0{i+1}T00:00:00",
            "open": 100.0 + i,
            "high": 105.0 + i,
            "low": 99.0 + i,
            "close": 103.0 + i,
            "volume": 1000000,
            "instrument": "TEST"
        }
        client.post("/data", json=data)
    
    response = client.get("/strategy/performance")
    assert response.status_code == 400


def test_strategy_performance_invalid_windows(test_db):
    """Test strategy with invalid window parameters"""
    response = client.get("/strategy/performance?short_window=50&long_window=20")
    assert response.status_code == 400