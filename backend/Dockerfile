FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for build (if any)
RUN apt-get update && apt-get install -y gcc g++ libpq-dev && rm -rf /var/lib/apt/lists/*

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create models and plots dirs
RUN mkdir -p /ml_pipeline/models /ml_pipeline/plots

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
