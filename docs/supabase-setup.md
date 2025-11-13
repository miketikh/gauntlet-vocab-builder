# Supabase Setup Guide

This guide covers setting up the Supabase database schema, authentication, and configuration for the Vocabulary Builder application.

## Table of Contents

1. [Database Schema Setup](#database-schema-setup)
2. [Running Migrations](#running-migrations)
3. [Authentication Configuration](#authentication-configuration)
4. [Verifying Setup](#verifying-setup)
5. [Troubleshooting](#troubleshooting)

---

## Database Schema Setup

The database schema is defined in SQL migration files located in `/api/supabase/migrations/`.

### Migration Files

1. **20231113000001_create_core_tables.sql** - Creates the core database tables:
   - `educators` - Educator profiles
   - `students` - Student profiles managed by educators
   - `documents` - Document metadata (files stored in S3)
   - `grade_words` - Reference table for grade-level vocabulary

2. **20231113000002_create_timestamp_triggers.sql** - Automatic timestamp updates:
   - Creates `update_updated_at_column()` function
   - Adds triggers to auto-update `updated_at` on all tables

3. **20231113000003_create_rls_policies.sql** - Row-Level Security policies:
   - Ensures educators can only access their own data
   - Allows all authenticated users to read `grade_words`
   - Implements proper data isolation

### Database Schema Overview

```
educators (id, email, name, school, created_at, updated_at)
    ↓
students (id, educator_id, name, grade_level, reading_level, notes, ...)
    ↓
documents (id, student_id, title, s3_key, upload_date, file_type, status, ...)

grade_words (id, grade_level, word, definition, example, frequency_rank, ...)
```

---

## Running Migrations

### Option 1: Using Supabase Dashboard (Recommended)

1. Log in to your Supabase project: https://supabase.com/dashboard
2. Navigate to **SQL Editor** in the left sidebar
3. Click **New Query**
4. Copy the contents of each migration file in order:
   - `20231113000001_create_core_tables.sql`
   - `20231113000002_create_timestamp_triggers.sql`
   - `20231113000003_create_rls_policies.sql`
5. Paste and run each migration
6. Verify success by checking **Database > Tables**

### Option 2: Using Supabase CLI

If you have the Supabase CLI installed:

```bash
cd api
supabase db push
```

### Verify Tables Were Created

After running migrations, verify the tables exist:

1. Go to **Database > Tables** in Supabase Dashboard
2. You should see:
   - educators
   - students
   - documents
   - grade_words

3. Click on each table to verify:
   - Columns are correct
   - RLS is enabled (green checkmark next to "Enable RLS")
   - Policies are listed in the "Policies" tab

---

## Authentication Configuration

### Email/Password Authentication

Email/password authentication is **enabled by default** in Supabase.

To verify or configure:

1. Go to **Authentication > Providers** in Supabase Dashboard
2. Ensure **Email** provider is enabled
3. **Recommended for development**: Disable email confirmation
   - Go to **Authentication > Settings**
   - Uncheck "Enable email confirmations"
   - This allows testing without email verification

### Google OAuth Setup

Google OAuth requires configuration in both Google Cloud Console and Supabase.

#### Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services > Credentials**
4. Click **Create Credentials > OAuth 2.0 Client ID**
5. Configure OAuth consent screen if prompted:
   - User Type: **External** (for testing) or **Internal** (for organization)
   - App name: "Vocabulary Builder"
   - User support email: Your email
   - Authorized domains: Add your Supabase domain and local testing domain
   - Developer contact: Your email
6. Create OAuth 2.0 Client ID:
   - Application type: **Web application**
   - Name: "Vocabulary Builder - Supabase Auth"
   - Authorized JavaScript origins:
     ```
     https://<your-project-ref>.supabase.co
     http://localhost:3000
     ```
   - Authorized redirect URIs:
     ```
     https://<your-project-ref>.supabase.co/auth/v1/callback
     http://localhost:3000/auth/callback
     ```
7. Click **Create** and save your:
   - Client ID
   - Client Secret

#### Step 2: Configure Google OAuth in Supabase

1. Go to **Authentication > Providers** in Supabase Dashboard
2. Find **Google** in the list and click to enable
3. Enter your credentials:
   - **Client ID**: Paste from Google Cloud Console
   - **Client Secret**: Paste from Google Cloud Console
4. Copy the **Callback URL** shown in Supabase (should be `https://<your-project-ref>.supabase.co/auth/v1/callback`)
5. Click **Save**

#### Step 3: Update Environment Variables

No additional environment variables are needed. The Next.js app will use:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://<your-project-ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-anon-key>
```

#### Step 4: Test Google OAuth

1. Start the Next.js development server: `cd web && npm run dev`
2. Navigate to the login page
3. Click "Sign in with Google"
4. Complete the Google OAuth flow
5. You should be redirected back to the app as an authenticated user

---

## Verifying Setup

### Test Database Connection

Run the provided test script:

```bash
cd api
python test_db_connection.py
```

This script will:
- ✓ Test Supabase connection
- ✓ Verify all tables exist
- ✓ Check RLS is enabled (manual verification recommended)
- ✓ Display table information

Expected output:
```
=============================================================
SUPABASE DATABASE CONNECTION TEST
=============================================================
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

### Manual Verification Checklist

- [ ] All tables created (educators, students, documents, grade_words)
- [ ] RLS enabled on all tables (green checkmark in Supabase Dashboard)
- [ ] RLS policies visible for each table
- [ ] Email/password auth enabled
- [ ] Google OAuth configured (if needed)
- [ ] Environment variables set in `/api/.env`
- [ ] Test script passes without errors

---

## Troubleshooting

### Connection Errors

**Problem**: `SUPABASE_URL environment variable is not set`

**Solution**: Ensure `/api/.env` file exists with correct values:
```bash
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
```

### RLS Policy Issues

**Problem**: Can't query tables, getting "permission denied" errors

**Solution**:
1. Verify RLS policies were created successfully
2. Check that you're using the correct authentication token
3. Ensure the user ID in `auth.uid()` matches the `educator_id` in the data

**Common mistake**: Using the anon key instead of a user's JWT token

### Migration Errors

**Problem**: "relation already exists" error

**Solution**: Tables already exist. You can either:
- Drop the tables and re-run migrations (⚠️ will delete data)
- Skip the migration if schema is correct

To drop tables (careful!):
```sql
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS educators CASCADE;
DROP TABLE IF EXISTS grade_words CASCADE;
```

### Google OAuth Not Working

**Problem**: Google OAuth redirects fail or show errors

**Solution**:
1. Verify redirect URIs in Google Cloud Console match exactly
2. Check that callback URL in Supabase includes `/auth/v1/callback`
3. Ensure OAuth consent screen is published (if using External user type)
4. Check browser console for CORS errors

### Performance Issues

**Problem**: Queries are slow

**Solution**: Verify indexes were created:
- `idx_educators_email`
- `idx_students_educator_id`
- `idx_documents_student_id`
- `idx_grade_words_grade_level`

Check indexes in Supabase Dashboard > Database > Indexes

---

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Row-Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Google OAuth Setup Guide](https://supabase.com/docs/guides/auth/social-login/auth-google)
- [Supabase CLI Reference](https://supabase.com/docs/reference/cli)

---

## Next Steps

After completing this setup:

1. ✅ Database schema is ready
2. ✅ Authentication is configured
3. ➡️ **Story 1.3**: Implement educator authentication in Next.js
4. ➡️ **Story 1.4**: Create authenticated educator dashboard
5. ➡️ **Story 1.5**: Set up FastAPI with JWT verification

---

*Last updated: 2023-11-13*
