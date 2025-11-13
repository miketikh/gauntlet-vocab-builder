# Vocab Builder API

FastAPI backend for the Personalized Vocabulary Recommendation Engine using SQLModel ORM.

## Architecture

- **Framework:** FastAPI (Python 3.9+)
- **ORM:** SQLModel (SQLAlchemy + Pydantic)
- **Database:** Supabase PostgreSQL
- **Migrations:** Alembic
- **Type Safety:** End-to-end types via OpenAPI → TypeScript codegen

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
# Edit .env with your configuration:
# - DATABASE_URL: PostgreSQL connection string (use Supabase pooler)
# - SUPABASE_URL: Your Supabase project URL
# - SUPABASE_SERVICE_ROLE_KEY: For auth and storage operations
# - AWS credentials: For S3 document storage
```

**Important:** Use the Supabase **Session mode (pooler)** connection string:
```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-us-east-2.pooler.supabase.com:6543/postgres
```

### 4. Run database migrations

```bash
# Generate initial migration (if not already done)
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

See `alembic/README.md` for detailed migration documentation.

### 5. Run development server

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **OpenAPI JSON:** http://localhost:8000/openapi.json
- **Docs:** http://localhost:8000/docs (Swagger UI)
- **ReDoc:** http://localhost:8000/redoc

## Project Structure

```
api/
├── main.py              # FastAPI app entry point
├── models/              # SQLModel database models + Pydantic schemas
│   ├── database.py      # Table models, enums, API schemas
│   └── __init__.py
├── services/            # Business logic
│   └── database.py      # Database session, queries, helpers
├── routers/             # API route handlers (future)
├── alembic/             # Database migrations
│   ├── versions/        # Migration files
│   ├── env.py           # Alembic configuration
│   └── README.md        # Migration guide
├── alembic.ini          # Alembic config file
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Python project config
└── .env                 # Environment variables (not committed)
```

## Database Management with Alembic

### Quick Commands

```bash
# Create a new migration (autogenerate from models)
alembic revision --autogenerate -m "Description"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current migration status
alembic current

# View migration history
alembic history
```

### Workflow

1. **Modify models** in `models/database.py`
2. **Generate migration:** `alembic revision --autogenerate -m "Add new field"`
3. **Review migration** in `alembic/versions/`
4. **Apply migration:** `alembic upgrade head`
5. **Commit both** model changes and migration file

**For detailed instructions, see `alembic/README.md`**

## SQLModel Database Models

Models are defined in `models/database.py`:

- **Educator:** Teacher/educator accounts
- **Student:** Student profiles (linked to educators)
- **Document:** Uploaded student documents (stored in S3)
- **GradeWord:** Grade-appropriate vocabulary word lists

Each model includes:
- Table model (for database)
- Public response model (for API responses)
- Create model (for POST requests)
- Update model (for PATCH requests)

Example:
```python
from models.database import Student, StudentCreate, StudentPublic
from services.database import get_session
from sqlmodel import Session, select

# Create student
student = Student(
    educator_id=1,
    name="John Doe",
    grade_level=8
)
session.add(student)
session.commit()

# Query students
statement = select(Student).where(Student.educator_id == 1)
students = session.exec(statement).all()
```

## Type Safety with Frontend

The frontend generates TypeScript types from the OpenAPI schema:

### Backend (FastAPI)
1. Define SQLModel models with Pydantic validation
2. Use `response_model` in route decorators
3. FastAPI auto-generates OpenAPI JSON at `/openapi.json`

### Frontend (Next.js)
1. Start API: `cd api && uvicorn main:app --reload`
2. Generate types: `cd web && npm run generate:api-types`
3. Import: `import { apiClient } from '@/lib/api-client'`
4. Use type-safe API calls

See `web/lib/api-client.ts` for usage examples.

## Development

### Running tests

```bash
pytest
```

### Code formatting

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy .
```

### Adding new endpoints

1. Define route in `main.py` or create router in `routers/`
2. Use SQLModel models for request/response
3. Add `session: Session = Depends(get_session)` for database access
4. FastAPI will auto-generate OpenAPI schema
5. Frontend can regenerate types to get new endpoints

Example:
```python
@app.get("/api/students/{student_id}", response_model=StudentPublic)
async def get_student(
    student_id: int,
    session: Session = Depends(get_session)
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
```

## Environment Variables

Required environment variables (see `.env.example`):

- `DATABASE_URL`: PostgreSQL connection string (Supabase pooler)
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: For admin operations
- `AWS_S3_BUCKET`: S3 bucket name for document storage
- `AWS_REGION`: AWS region
- `AWS_ACCESS_KEY_ID`: AWS credentials
- `AWS_SECRET_ACCESS_KEY`: AWS credentials

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

## Troubleshooting

### "Can't connect to database"
- Check DATABASE_URL is correct
- Ensure you're using the **pooler** connection string (port 6543)
- Verify Supabase project is running

### "Table does not exist"
- Run migrations: `alembic upgrade head`
- Check migration status: `alembic current`

### "OpenAPI types out of sync"
- Regenerate frontend types: `cd web && npm run generate:api-types`
- Ensure FastAPI is running on port 8000

### "Import errors for models"
- Check you're in virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## Migration from Drizzle

This project was refactored from Drizzle (Node.js) to SQLModel (Python):
- ❌ Removed: `node_modules/`, `package.json`, `drizzle/`, `db/`
- ✅ Added: SQLModel models, Alembic migrations
- ✅ Benefit: Pure Python stack, better type integration with FastAPI
- ✅ Frontend: OpenAPI → TypeScript type generation

See git history for details on the migration.
