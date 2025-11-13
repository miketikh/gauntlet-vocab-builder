# Supabase Database Migration Instructions

## Story 1.2 Setup Complete! ✓

All migration files and utilities have been created. Now you need to execute the migrations in your Supabase dashboard.

## Quick Start

### Step 1: View the Migration SQL

The combined SQL for all migrations is available in:
```
/Users/mike/gauntlet/vocab-builder/api/supabase/combined_migrations.sql
```

Or run this to see it in your terminal:
```bash
cd /Users/mike/gauntlet/vocab-builder/api
python3 apply_migrations.py
```

### Step 2: Execute in Supabase Dashboard

1. **Open Supabase Dashboard**
   - Go to: https://supabase.com/dashboard
   - Select your vocab-builder project
   - Your project URL: https://afpskpdxuubdsxxxuxar.supabase.co

2. **Navigate to SQL Editor**
   - Click "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Copy and Execute Migration Files (in order)**

   **MIGRATION 1 - Core Tables:**
   - Open: `/api/supabase/migrations/20231113000001_create_core_tables.sql`
   - Copy the entire contents
   - Paste into SQL Editor
   - Click "Run" (or press Cmd/Ctrl + Enter)
   - Wait for "Success" message

   **MIGRATION 2 - Timestamp Triggers:**
   - Open: `/api/supabase/migrations/20231113000002_create_timestamp_triggers.sql`
   - Copy the entire contents
   - Paste into SQL Editor
   - Click "Run"
   - Wait for "Success" message

   **MIGRATION 3 - RLS Policies:**
   - Open: `/api/supabase/migrations/20231113000003_create_rls_policies.sql`
   - Copy the entire contents
   - Paste into SQL Editor
   - Click "Run"
   - Wait for "Success" message

### Step 3: Verify Setup

After executing all migrations, run the test script:

```bash
cd /Users/mike/gauntlet/vocab-builder/api
python3 test_db_connection.py
```

Expected output:
```
============================================================
SUPABASE DATABASE CONNECTION TEST
============================================================
Testing Supabase connection...
✓ Supabase connection successful!

Checking if tables exist...
✓ Table 'educators' exists (count: 0)
✓ Table 'students' exists (count: 0)
✓ Table 'documents' exists (count: 0)
✓ Table 'grade_words' exists (count: 0)

...

ALL TESTS PASSED! Database is ready.
```

## What Was Created

### Database Tables

1. **educators** - Educator profiles
   - Fields: id, email, name, school, created_at, updated_at
   - Primary key: id (UUID)
   - Unique constraint: email
   - Index: email

2. **students** - Student profiles
   - Fields: id, educator_id, name, grade_level, reading_level, notes, created_at, updated_at
   - Primary key: id (UUID)
   - Foreign key: educator_id → educators(id) CASCADE
   - Indexes: educator_id, grade_level
   - Constraint: grade_level CHECK (6-12)

3. **documents** - Document metadata
   - Fields: id, student_id, title, s3_key, upload_date, file_type, status, created_at, updated_at
   - Primary key: id (UUID)
   - Foreign key: student_id → students(id) CASCADE
   - Indexes: student_id, status, upload_date
   - Constraint: status CHECK (pending, processing, completed, failed)

4. **grade_words** - Vocabulary reference table
   - Fields: id, grade_level, word, definition, example, frequency_rank, subject, created_at, updated_at
   - Primary key: id (UUID)
   - Indexes: grade_level, word, frequency_rank
   - Unique constraint: (grade_level, word, subject)
   - Constraint: grade_level CHECK (6-12)

### Automatic Triggers

- `update_updated_at_column()` function
- Triggers on all tables to auto-update `updated_at` timestamp

### Row-Level Security (RLS) Policies

**Educators Table:**
- ✓ Can view own profile
- ✓ Can update own profile
- ✓ Can insert own profile (during signup)

**Students Table:**
- ✓ Can view own students
- ✓ Can insert students for self
- ✓ Can update own students
- ✓ Can delete own students

**Documents Table:**
- ✓ Can view documents for own students
- ✓ Can insert documents for own students
- ✓ Can update documents for own students
- ✓ Can delete documents for own students

**Grade Words Table:**
- ✓ All authenticated users can read (reference data)
- ✓ Only service role can modify

### Utilities Created

**Files in `/api/services/`:**
- `supabase.py` - Supabase client initialization and helper functions

**Helper Functions:**
- `get_educator_by_id(educator_id)`
- `get_educator_by_email(email)`
- `get_students_by_educator(educator_id)`
- `get_documents_by_student(student_id)`
- `get_grade_words(grade_level, limit?)`
- `update_document_status(document_id, status)`
- `create_educator(user_id, email, name, school?)`
- `check_connection()` - Test connection

**Test Scripts:**
- `test_db_connection.py` - Comprehensive database test
- `apply_migrations.py` - Output all migration SQL
- `auto_run_migrations.py` - Generate combined migration file

### Documentation

**Created:**
- `/api/supabase/README.md` - Migration instructions
- `/docs/supabase-setup.md` - Complete setup guide including Google OAuth
- `/api/MIGRATION_INSTRUCTIONS.md` - This file

## Troubleshooting

### Connection Test Fails Before Migrations

If you see:
```
Could not find the table 'public.educators' in the schema cache
```

This is NORMAL and means the migrations haven't been executed yet. Proceed with Step 2 above.

### "relation already exists" Error

The tables already exist. You can either:
1. Skip the migration (if schema is correct)
2. Drop the tables and re-run (⚠️ WARNING: deletes data)

To drop tables:
```sql
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS educators CASCADE;
DROP TABLE IF EXISTS grade_words CASCADE;
```

### RLS Policy Errors

If you see policy-related errors, ensure:
1. Tables were created successfully first
2. RLS is enabled on each table
3. Policies reference existing tables

## Next Steps

After successful migration:

1. ✅ **Story 1.2 Complete!** - Database schema set up
2. ➡️ **Story 1.3** - Implement educator authentication in Next.js
3. ➡️ **Story 1.4** - Create authenticated educator dashboard
4. ➡️ **Story 1.5** - Set up FastAPI with JWT verification

## Authentication Notes

**Email/Password:**
- Already enabled by default in Supabase
- For development: Disable email confirmation in Auth settings

**Google OAuth:**
- See `/docs/supabase-setup.md` for detailed Google OAuth setup
- Requires Google Cloud Console configuration
- Instructions provided for creating OAuth credentials

## Environment Variables

Already configured in `/api/.env`:
```bash
SUPABASE_URL=https://afpskpdxuubdsxxxuxar.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sb_secret_E6c4Xlw1uX5JcGxWAMCd4Q_1g4ty4Yx
```

## Database Connection String

For advanced use (direct PostgreSQL access):
```
postgresql://postgres:[YOUR-DB-PASSWORD]@db.afpskpdxuubdsxxxuxar.supabase.co:5432/postgres
```

Get your database password from:
- Supabase Dashboard → Settings → Database → Connection String

---

**Status:** ✅ Migration files ready - awaiting manual execution

**Estimated Time:** 5-10 minutes to execute all migrations and verify

**Last Updated:** 2023-11-13
