# Drizzle ORM Database Management

This directory contains the Drizzle ORM schema and migration management for the Vocab Builder application.

## Overview

We use **Drizzle ORM** for type-safe database schema management with Supabase PostgreSQL. Drizzle provides:

- Type-safe database schema definition in TypeScript
- Automatic migration generation
- Direct schema push for rapid development
- IntelliSense support for queries
- Zero-cost abstractions

## Architecture: Hybrid Approach

Since our stack combines **TypeScript (Drizzle)** and **Python (FastAPI)**, we use a hybrid approach:

1. **Schema Management**: Drizzle ORM (TypeScript) - Define and push schema changes
2. **Python Backend**: Raw SQL queries via Supabase Python client
3. **TypeScript Scripts**: Can use Drizzle client directly for data seeding or migrations

This approach gives us:
- Type-safe schema definitions
- Best-in-class migration tooling
- Python flexibility for FastAPI endpoints
- No mixing of TypeScript and Python in production code

## Directory Structure

```
/api
├── drizzle/
│   ├── schema.ts           # Database schema definition (TypeScript)
│   ├── migrations/         # Generated SQL migrations (git-tracked)
│   └── README.md           # This file
├── db/
│   └── index.ts            # Drizzle client initialization (for TypeScript scripts)
├── drizzle.config.ts       # Drizzle Kit configuration
├── package.json            # Node.js dependencies for Drizzle
└── tsconfig.json           # TypeScript configuration
```

## Setup

### Prerequisites

1. Node.js 18+ installed
2. Supabase project created
3. Environment variables configured in `.env`

### Environment Variables

Add these to your `/api/.env` file:

```bash
# Supabase configuration
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_SERVICE_ROLE_KEY=sb_secret_[key]

# Database connection for Drizzle migrations
# Get from Supabase Dashboard: Project Settings > Database > Connection string (Session mode)
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-us-east-2.pooler.supabase.com:6543/postgres
```

**Important**: `DATABASE_URL` is the PostgreSQL connection string with your database password. This is **different** from `SUPABASE_SERVICE_ROLE_KEY` which is for API authentication.

### Getting Your DATABASE_URL

**IMPORTANT**: You must use the **Connection pooling** URI, not the "Direct connection" URI.

1. Go to your Supabase project dashboard
2. Navigate to: **Project Settings** > **Database**
3. Under "Connection string", select **Connection pooling** (NOT "Direct connection")
   - The pooling URI uses `pooler.supabase.com:6543`
   - The direct connection URI uses `db.*.supabase.co:5432` (this will NOT work with Drizzle)
4. Copy the connection string
5. Replace `[YOUR-PASSWORD]` with your actual database password
6. Add it to your `.env` file

**Why Connection Pooling?**
- The direct connection URI (`db.*.supabase.co`) is not externally accessible by default
- Connection pooling (`pooler.supabase.com`) is designed for external connections
- Without pooling, you'll get DNS errors like `ENOTFOUND db.*.supabase.co`

### Install Dependencies

```bash
cd /api
npm install
```

## Schema Definition

The database schema is defined in `/api/drizzle/schema.ts`.

### Tables

1. **educators** - Educator account information
2. **students** - Student profiles (linked to educators)
3. **documents** - Document metadata (files stored in S3)
4. **grade_words** - Reference table for grade-level vocabulary

All tables include:
- UUID primary keys
- Timestamps (created_at, updated_at)
- Proper foreign key relationships with cascade deletes
- Indexes for query performance
- Check constraints for data validation

### TypeScript Types

The schema automatically generates TypeScript types:

```typescript
import type { Educator, NewEducator, Student, NewStudent } from './drizzle/schema';
```

## Database Commands

### Push Schema to Database

Push your schema changes directly to Supabase (for rapid development):

```bash
npm run db:push
```

This command:
- Reads schema from `drizzle/schema.ts`
- Compares with current database state
- Applies changes directly to the database
- **Does NOT generate migration files**
- Best for development and prototyping

### Generate Migration Files

Create SQL migration files (for version control and production):

```bash
npm run db:generate
```

This command:
- Compares schema with database state
- Generates SQL migration files in `drizzle/migrations/`
- Files should be committed to git
- Use when you want explicit migration history

### Apply Migrations

Apply pending migrations to the database:

```bash
npm run db:migrate
```

Note: Currently using `db:push` for rapid development. Use `db:migrate` in production.

### Open Drizzle Studio

Visual database browser (optional):

```bash
npm run db:studio
```

Opens a local web interface to browse and edit database data.

## Development Workflow

### Making Schema Changes

1. **Edit schema**: Modify `/api/drizzle/schema.ts`
2. **Push changes**: Run `npm run db:push`
3. **Verify**: Check Supabase dashboard or use `db:studio`
4. **Update Python**: If needed, update Python code to match new schema

### Example: Adding a New Column

```typescript
// In drizzle/schema.ts
export const students = pgTable('students', {
  // ... existing columns
  phoneNumber: text('phone_number'), // Add new column
});
```

Then run:
```bash
npm run db:push
```

### Example: Adding a New Table

```typescript
// In drizzle/schema.ts
export const assignments = pgTable('assignments', {
  id: uuid('id').primaryKey().defaultRandom(),
  studentId: uuid('student_id').notNull().references(() => students.id, { onDelete: 'cascade' }),
  title: text('title').notNull(),
  dueDate: timestamp('due_date', { withTimezone: true }),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
});

export type Assignment = typeof assignments.$inferSelect;
export type NewAssignment = typeof assignments.$inferInsert;
```

Then push:
```bash
npm run db:push
```

## Using Drizzle in TypeScript Scripts

If you need to write TypeScript data seeding scripts or utilities:

```typescript
import { db, schema } from './db/index.js';
import { eq } from 'drizzle-orm';

// Query
const educators = await db.select().from(schema.educators);

// Insert
const newStudent = await db.insert(schema.students).values({
  educatorId: 'uuid',
  name: 'John Doe',
  gradeLevel: 9,
}).returning();

// Update
await db.update(schema.documents)
  .set({ status: 'completed' })
  .where(eq(schema.documents.id, 'document-uuid'));
```

## Using Schema in Python FastAPI

Python code uses the Supabase Python client for queries. While the schema is defined in TypeScript, you reference the same table and column names:

```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Query
response = supabase.table("students").select("*").eq("educator_id", educator_id).execute()
students = response.data

# Insert
new_student = supabase.table("students").insert({
    "educator_id": educator_id,
    "name": "John Doe",
    "grade_level": 9,
}).execute()

# Update
supabase.table("documents").update({
    "status": "completed"
}).eq("id", document_id).execute()
```

## Row-Level Security (RLS)

Drizzle ORM manages the **schema**, but **RLS policies** must be created separately in Supabase.

### Creating RLS Policies

RLS policies are managed via Supabase Dashboard or SQL:

```sql
-- Enable RLS on table
ALTER TABLE students ENABLE ROW LEVEL SECURITY;

-- Policy: Educators can only access their own students
CREATE POLICY "Educators can view their own students"
ON students FOR SELECT
USING (educator_id = auth.uid());

CREATE POLICY "Educators can insert their own students"
ON students FOR INSERT
WITH CHECK (educator_id = auth.uid());

-- Similar policies for documents, etc.
```

**Note**: RLS policies are part of your database configuration, not the Drizzle schema. Add them manually or via Supabase dashboard.

## Production Deployment

For production:

1. **Use migrations** instead of `db:push`:
   ```bash
   npm run db:generate  # Create migration files
   # Review generated SQL
   # Commit to git
   npm run db:migrate   # Apply in production
   ```

2. **Version control**: Always commit `drizzle/migrations/` to git

3. **CI/CD**: Add migration step to deployment pipeline

## Troubleshooting

### "Tenant or user not found" or DNS Errors (ENOTFOUND)

These errors usually mean `DATABASE_URL` is incorrectly formatted or using the wrong connection type:

**Common Issues:**
- Using "Direct connection" URI (`db.*.supabase.co:5432`) instead of "Connection pooling" URI
- Project reference doesn't match your Supabase URL
- Database password is incorrect (not the service role key)
- Wrong port number (should be 6543 for pooler, not 5432)

**Solution:**
1. Go to Supabase Dashboard > Project Settings > Database
2. Select **Connection pooling** (NOT "Direct connection")
3. Copy the connection string with format:
   ```
   postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-us-east-2.pooler.supabase.com:6543/postgres
   ```
4. Replace `[PASSWORD]` with your actual database password
5. Update your `.env` file

### Connection Timeout

If connection hangs:
- Verify your IP is whitelisted in Supabase (or disable IP restrictions for development)
- Check firewall settings
- Try direct connection (port 5432) instead of pooler

### Schema Mismatch

If Drizzle reports schema conflicts:
```bash
# Force push (careful - can lose data)
npm run db:push -- --force
```

Or manually fix conflicts in Supabase dashboard.

## Resources

- [Drizzle ORM Documentation](https://orm.drizzle.team/docs/overview)
- [Drizzle with Supabase Guide](https://orm.drizzle.team/docs/get-started-postgresql#supabase)
- [Supabase Database Documentation](https://supabase.com/docs/guides/database)

## Next Steps

After setting up Drizzle:

1. ✅ Schema defined and pushed
2. Add RLS policies in Supabase dashboard
3. Create Python helper functions for common queries
4. Implement FastAPI endpoints using schema
5. Add data seeding scripts (if needed)

---

**Questions?** Check the main `/api/README.md` or project documentation.
