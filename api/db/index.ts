/**
 * Drizzle Database Client
 *
 * This module initializes and exports the Drizzle database client for use
 * in TypeScript/Node.js scripts. For Python FastAPI, use raw SQL queries
 * with the Supabase Python client.
 */

import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as dotenv from 'dotenv';
import * as schema from '../drizzle/schema.js';

// Load environment variables
dotenv.config();

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseServiceRoleKey) {
  throw new Error('SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env file');
}

// Extract project reference from Supabase URL
const projectRef = supabaseUrl.match(/https:\/\/([^.]+)\.supabase\.co/)?.[1];

if (!projectRef) {
  throw new Error('Invalid SUPABASE_URL format');
}

// Construct PostgreSQL connection string for Supabase
// Using session mode pooler for regular queries (port 6543)
const connectionString = `postgresql://postgres.${projectRef}:${supabaseServiceRoleKey}@aws-0-us-east-2.pooler.supabase.com:6543/postgres`;

// Create postgres client
const queryClient = postgres(connectionString);

// Create Drizzle ORM instance
export const db = drizzle(queryClient, { schema });

// Export schema for use in queries
export { schema };

// Export types
export type {
  Educator,
  NewEducator,
  Student,
  NewStudent,
  Document,
  NewDocument,
  GradeWord,
  NewGradeWord,
  DocumentStatusType,
  GradeLevelType,
} from '../drizzle/schema.js';

// ============================================================================
// Example Usage (for reference)
// ============================================================================

/*
import { db, schema } from './db/index.js';
import { eq } from 'drizzle-orm';

// Query all educators
const allEducators = await db.select().from(schema.educators);

// Query educator by email
const educator = await db
  .select()
  .from(schema.educators)
  .where(eq(schema.educators.email, 'educator@example.com'))
  .limit(1);

// Insert new student
const newStudent = await db
  .insert(schema.students)
  .values({
    educatorId: 'educator-uuid',
    name: 'John Doe',
    gradeLevel: 9,
    readingLevel: 'Proficient',
  })
  .returning();

// Update document status
await db
  .update(schema.documents)
  .set({ status: 'completed' })
  .where(eq(schema.documents.id, 'document-uuid'));

// Delete student (cascades to documents)
await db
  .delete(schema.students)
  .where(eq(schema.students.id, 'student-uuid'));
*/
