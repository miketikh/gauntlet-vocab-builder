# Vocab Builder API

FastAPI backend for the Personalized Vocabulary Recommendation Engine.

## Setup

### 1. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run development server

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs (Swagger UI)
- **ReDoc:** http://localhost:8000/redoc

## Project Structure

```
api/
├── main.py           # FastAPI app entry point
├── routers/          # API route handlers
├── services/         # Business logic (vocab analysis, AI, etc.)
├── models/           # Pydantic models
├── requirements.txt  # Python dependencies
└── .env             # Environment variables (not committed)
```

## Development

### Running tests

```bash
pytest
```

### Code formatting

```bash
# Install ruff
pip install ruff

# Format code
ruff format .

# Lint code
ruff check .
```

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.
