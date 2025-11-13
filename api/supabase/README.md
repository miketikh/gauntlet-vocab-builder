# Supabase Database Migrations

This directory contains SQL migration files for the Vocabulary Builder database schema.

## Migration Files

Execute these migrations in order:

1. **20231113000001_create_core_tables.sql** - Creates core database tables
2. **20231113000002_create_timestamp_triggers.sql** - Adds automatic timestamp triggers
3. **20231113000003_create_rls_policies.sql** - Implements Row-Level Security policies

## How to Run Migrations

### Method 1: Supabase Dashboard (Recommended)

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Navigate to **SQL Editor** (left sidebar)
4. Click **New Query**
5. Copy the content of each migration file (in order)
6. Paste into the SQL Editor
7. Click **Run** to execute
8. Verify success (no errors)
9. Repeat for all migration files

### Method 2: View All Migrations at Once

Run this command to output all migrations in the terminal:

```bash
cd api
python3 apply_migrations.py
```

This will display all SQL that needs to be executed. Copy and paste each section into the Supabase SQL Editor.

### Method 3: Supabase CLI (Advanced)

If you have the Supabase CLI installed:

```bash
cd api
supabase db push
```

## Verify Migrations

After running migrations, verify they were successful:

```bash
cd api
python3 test_db_connection.py
```

This script will:
- Test the Supabase connection
- Verify all tables exist
- Check RLS is enabled
- Display table information

## Troubleshooting

### "relation already exists" error

The tables already exist. You can skip the migration or drop the existing tables first (WARNING: will delete data):

```sql
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS educators CASCADE;
DROP TABLE IF EXISTS grade_words CASCADE;
```

### Permission errors

Ensure you're using a service role key or execute migrations via the Supabase Dashboard which has full admin privileges.

### RLS blocking queries

Row-Level Security policies are designed to block unauthorized access. When using the service role key (backend), RLS policies are bypassed. When using the anon key (frontend), RLS policies are enforced.

## What the Migrations Do

### Migration 1: Core Tables

- **educators**: Stores educator profiles (id, email, name, school)
- **students**: Stores student profiles (id, educator_id, name, grade_level, reading_level, notes)
- **documents**: Stores document metadata (id, student_id, title, s3_key, upload_date, file_type, status)
- **grade_words**: Reference table for vocabulary words (id, grade_level, word, definition, example, frequency_rank, subject)

Includes:
- UUID primary keys
- Foreign key constraints with CASCADE delete
- Indexes for performance
- Check constraints for data validation

### Migration 2: Timestamp Triggers

Creates:
- `update_updated_at_column()` function
- Triggers on all tables to auto-update `updated_at` timestamp on row updates

### Migration 3: RLS Policies

Implements Row-Level Security:
- Educators can only view/modify their own profile
- Educators can only access students they created
- Educators can only access documents for their students
- All authenticated users can read grade_words (reference data)

## Database Schema Diagram

```
educators (id, email, name, school, ...)
    |
    | educator_id (FK)
    ↓
students (id, educator_id, name, grade_level, ...)
    |
    | student_id (FK)
    ↓
documents (id, student_id, title, s3_key, ...)

grade_words (id, grade_level, word, definition, ...)  [Reference table]
```

## Next Steps

After migrations are complete:

1. ✅ Verify with `python3 test_db_connection.py`
2. ➡️ Proceed to Story 1.3: Implement educator authentication in Next.js
3. ➡️ See full setup guide: `/docs/supabase-setup.md`
