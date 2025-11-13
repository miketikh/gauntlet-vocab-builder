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

### 3. Install Node.js dependencies (for Drizzle ORM)

```bash
npm install
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your configuration
# IMPORTANT: Add DATABASE_URL for schema migrations (see drizzle/README.md)
# NOTE: Use "Connection pooling" URI from Supabase, NOT "Direct connection"
#       Format: postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-us-east-2.pooler.supabase.com:6543/postgres
```

### 5. Push database schema

```bash
npm run db:push
```

See `/drizzle/README.md` for detailed database management instructions.

### 6. Run development server

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
├── main.py              # FastAPI app entry point
├── routers/             # API route handlers
├── services/            # Business logic (vocab analysis, AI, etc.)
├── models/              # Pydantic models
├── drizzle/             # Database schema (TypeScript)
│   ├── schema.ts        # Drizzle ORM schema definition
│   ├── migrations/      # Generated SQL migrations
│   └── README.md        # Database management guide
├── db/                  # Database client (TypeScript)
│   └── index.ts         # Drizzle client initialization
├── drizzle.config.ts    # Drizzle configuration
├── package.json         # Node.js dependencies (Drizzle)
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (not committed)
```

## Database Management

We use **Drizzle ORM** (TypeScript) for schema management and **Supabase Python client** for queries in FastAPI.

### Quick Commands

```bash
# Push schema changes to database
npm run db:push

# Generate migration files
npm run db:generate

# Open database browser
npm run db:studio
```

**For detailed database documentation, see `/drizzle/README.md`**

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
