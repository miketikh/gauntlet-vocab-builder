FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy language model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Expose port (Railway will set the PORT env var)
EXPOSE 8000

# Run migrations and start the server
# Railway provides $PORT environment variable
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
