# Database Migration Instructions

## Status

The SQLModel schema and Alembic migrations are fully configured. However, migrations cannot be generated or applied until the DATABASE_URL is configured with valid Supabase credentials.

## What's Ready

- ✅ SQLModel models defined in `models/database.py`
- ✅ Alembic initialized and configured
- ✅ `alembic/env.py` configured to import SQLModel metadata
- ✅ Database service with session management
- ✅ FastAPI integrated with SQLModel

## What's Needed

1. **Valid DATABASE_URL** in `.env` file
2. **Access to Supabase database**

## Steps to Complete Migration Setup

### 1. Ensure DATABASE_URL is Set

In `.env`:
```bash
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-us-east-2.pooler.supabase.com:6543/postgres
```

**Important:** Use the **Session mode (pooler)** connection string from Supabase:
- Go to Supabase Dashboard
- Project Settings → Database
- Connection string → Session mode
- Copy the URI (with password filled in)

### 2. Test Database Connection

```bash
cd api
python3 -c "from services.database import engine; print('Connected!' if engine else 'Failed')"
```

### 3. Generate Initial Migration

```bash
cd api
alembic revision --autogenerate -m "Initial schema with SQLModel"
```

This will create a migration file in `alembic/versions/` with:
- `educators` table
- `students` table
- `documents` table
- `grade_words` table
- All foreign key relationships
- Indexes
- Constraints

### 4. Review the Generated Migration

Open the file in `alembic/versions/` and verify the changes:
- Check table definitions
- Verify foreign keys
- Ensure indexes are created
- Confirm constraints are correct

### 5. Apply the Migration

```bash
alembic upgrade head
```

This will create all tables in your Supabase database.

### 6. Verify Tables Were Created

Check in Supabase Dashboard:
- Go to Table Editor
- You should see: `educators`, `students`, `documents`, `grade_words`, `alembic_version`

Or via SQL Editor:
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';
```

## Expected Schema

After migration, you'll have:

### `educators` Table
- `id` (integer, primary key)
- `email` (varchar, unique)
- `name` (varchar)
- `school` (varchar, nullable)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### `students` Table
- `id` (integer, primary key)
- `educator_id` (integer, foreign key → educators.id)
- `name` (varchar)
- `grade_level` (integer, 6-12)
- `reading_level` (varchar, nullable)
- `notes` (text, nullable)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### `documents` Table
- `id` (integer, primary key)
- `student_id` (integer, foreign key → students.id)
- `title` (varchar)
- `s3_key` (varchar)
- `upload_date` (timestamp)
- `file_type` (enum: pdf, docx, txt)
- `status` (enum: pending, processing, completed, failed)
- `error_message` (text, nullable)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### `grade_words` Table
- `id` (integer, primary key)
- `grade_level` (integer, 6-12)
- `word` (varchar)
- `definition` (text)
- `example` (text, nullable)
- `frequency_rank` (integer, nullable)
- `subject` (varchar, nullable)
- `created_at` (timestamp)

## Troubleshooting

### "could not translate host name"

Your DATABASE_URL is invalid or the hostname is incorrect. Check:
1. Is the DATABASE_URL set in `.env`?
2. Is it the correct format?
3. Did you replace `[PROJECT-REF]` and `[PASSWORD]`?

### "permission denied for schema public"

Your database user doesn't have permissions. Use the Supabase **service role** connection string.

### "table already exists"

Tables might exist from a previous schema. Options:
1. Drop existing tables (dev only):
   ```sql
   DROP TABLE IF EXISTS documents, students, educators, grade_words CASCADE;
   DROP TABLE IF EXISTS alembic_version CASCADE;
   ```
2. Or create a new Alembic migration that handles existing tables

### "target database is not empty"

This is fine if you have other tables (like Supabase auth tables). Alembic will only manage tables it creates.

## Alternative: Manual Table Creation

If you can't run Alembic, you can create tables manually via Supabase SQL Editor:

```sql
-- See alembic/versions/<generated_file>.py for exact SQL
-- Or check SQLModel models in models/database.py
```

However, it's strongly recommended to use Alembic for proper version control.

## Next Steps After Migration

1. **Test API** with database:
   ```bash
   uvicorn main:app --reload
   curl http://localhost:8000/health
   ```

2. **Generate OpenAPI types** for frontend:
   ```bash
   cd ../web
   npm run generate:api-types
   ```

3. **Start building features!**
   - Add authentication endpoints
   - Implement student management
   - Build document upload
   - Develop vocabulary analysis

## Need Help?

Check:
- `alembic/README.md` for detailed migration guide
- `api/README.md` for general API documentation
- FastAPI docs: https://fastapi.tiangolo.com/
- SQLModel docs: https://sqlmodel.tiangolo.com/
- Alembic docs: https://alembic.sqlalchemy.org/
