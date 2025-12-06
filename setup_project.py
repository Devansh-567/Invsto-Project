import os

# Create directories
os.makedirs('app', exist_ok=True)
os.makedirs('tests', exist_ok=True)

# Create Dockerfile
dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    gcc \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

with open('Dockerfile', 'w') as f:
    f.write(dockerfile_content)

# Create requirements.txt
requirements_content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
pandas==2.1.3
numpy==1.26.2
python-dotenv==1.0.0
pytest==7.4.3
pytest-cov==4.1.0
httpx==0.25.2
"""

with open('requirements.txt', 'w') as f:
    f.write(requirements_content)

# Create docker-compose.yml
docker_compose_content = """services:
  postgres:
    image: postgres:15-alpine
    container_name: trading_postgres
    environment:
      POSTGRES_USER: tradinguser
      POSTGRES_PASSWORD: tradingpass
      POSTGRES_DB: tradingdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tradinguser"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    container_name: trading_api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://tradinguser:tradingpass@postgres:5432/tradingdb
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - .:/app

volumes:
  postgres_data:
"""

with open('docker-compose.yml', 'w') as f:
    f.write(docker_compose_content)

# Create __init__.py files
open('app/__init__.py', 'w').close()
open('tests/__init__.py', 'w').close()

# Create sample data.csv with a few rows
data_csv_content = """datetime,open,high,low,close,volume,instrument
2014-01-24 00:00:00,113.15,115.35,113,114,5737135,HINDALCO
2014-01-27 00:00:00,112,112.7,109.3,111.1,8724577,HINDALCO
2014-01-28 00:00:00,110,115,109.75,113.8,4513345,HINDALCO
2014-01-29 00:00:00,114.5,114.75,111.15,111.75,4713458,HINDALCO
2014-01-30 00:00:00,110.2,110.7,107.6,108.1,5077231,HINDALCO
"""

with open('data.csv', 'w') as f:
    f.write(data_csv_content)

print("✓ Created Dockerfile")
print("✓ Created requirements.txt")
print("✓ Created docker-compose.yml")
print("✓ Created app/__init__.py")
print("✓ Created tests/__init__.py")
print("✓ Created data.csv (with sample data)")
print("\n🎉 Project structure is ready!")
print("\nNext steps:")
print("1. Add all the Python code files (main.py, database.py, models.py, strategy.py)")
print("2. Add test files (test_main.py, test_strategy.py)")
print("3. Run: docker-compose build")
print("4. Run: docker-compose up")