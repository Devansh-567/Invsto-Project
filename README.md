# Trading Strategy API

A FastAPI-based application for managing stock data and implementing a Moving Average Crossover trading strategy.

## Features

- **PostgreSQL Database**: Store and manage stock price data
- **REST API**: FastAPI endpoints for data operations
- **Trading Strategy**: Moving Average Crossover strategy implementation
- **Docker Support**: Fully containerized application
- **Unit Tests**: Comprehensive test suite with 80%+ coverage

## Tech Stack

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker & Docker Compose
- Pytest

## Project Structure

```
trading-strategy-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database models and connection
│   ├── models.py            # Pydantic models
│   └── strategy.py          # Trading strategy logic
├── tests/
│   ├── __init__.py
│   ├── test_main.py         # API tests
│   └── test_strategy.py     # Strategy tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── data.csv                 # Stock data
└── README.md
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Installation

1. **Clone the repository**

```bash
   git clone <your-repo-url>
   cd trading-strategy-api
```

2. **Create data.csv**

   Copy the stock data from the document into `data.csv` with headers:

```
   datetime,open,high,low,close,volume,instrument
```

3. **Start the services**

```bash
   docker-compose up -d
```

4. **Access the API**

   The API will be available at: http://localhost:8000

   Interactive docs at: http://localhost:8000/docs

## API Endpoints

### GET /

- Root endpoint with API information

### GET /data

- Fetch all stock data
- Query parameters:
  - `skip`: Number of records to skip (default: 0)
  - `limit`: Maximum records to return (default: 100)

### POST /data

- Add new stock data record
- Request body:

```json
{
  "datetime": "2024-01-01T00:00:00",
  "open": 100.0,
  "high": 105.0,
  "low": 99.0,
  "close": 103.0,
  "volume": 1000000,
  "instrument": "HINDALCO"
}
```

### GET /strategy/performance

- Get Moving Average Crossover strategy performance
- Query parameters:
  - `short_window`: Short-term MA window (default: 20)
  - `long_window`: Long-term MA window (default: 50)

## Running Tests

### Using Docker

```bash
docker-compose exec api pytest tests/ -v --cov=app --cov-report=html
```

### Locally

```bash
pip install -r requirements.txt
pytest tests/ -v --cov=app --cov-report=html
```

View coverage report: Open `htmlcov/index.html` in your browser

## Trading Strategy

The Moving Average Crossover strategy:

- **Buy Signal**: When short-term MA crosses above long-term MA
- **Sell Signal**: When short-term MA crosses below long-term MA
- **Default Parameters**: 20-day (short) and 50-day (long) moving averages

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export DATABASE_URL="postgresql://tradinguser:tradingpass@localhost:5432/tradingdb"

# Run the application
uvicorn app.main:app --reload
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U tradinguser -d tradingdb

# View tables
\dt

# Query data
SELECT COUNT(*) FROM stock_data;
```

## Testing

The test suite includes:

- Input validation tests
- API endpoint tests
- Moving average calculation tests
- Strategy signal generation tests
-
