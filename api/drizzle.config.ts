/**
 * Drizzle Kit Configuration
 *
 * This configuration file tells drizzle-kit how to connect to the database
 * and where to find schema files.
 */

import { defineConfig } from 'drizzle-kit';
import * as dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const databaseUrl = process.env.DATABASE_URL;

if (!supabaseUrl || !supabaseServiceRoleKey) {
  throw new Error('SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env file');
}

// If DATABASE_URL is provided, use it directly (this is the PostgreSQL connection string)
if (databaseUrl) {
  console.log('Using DATABASE_URL for direct connection');
}

let connectionString: string;

if (databaseUrl) {
  // Use provided DATABASE_URL
  connectionString = databaseUrl;
} else {
  // Fall back to constructing from Supabase URL
  // Extract project reference from Supabase URL
  // Format: https://[project-ref].supabase.co
  const projectRef = supabaseUrl.match(/https:\/\/([^.]+)\.supabase\.co/)?.[1];

  if (!projectRef) {
    throw new Error('Invalid SUPABASE_URL format');
  }

  // Note: You need to add DATABASE_URL to your .env file with the actual PostgreSQL connection string
  // Get it from Supabase Dashboard: Project Settings > Database > Connection string
  // IMPORTANT: Use "Connection pooling" (pooler.supabase.com:6543) NOT "Direct connection" (db.*.supabase.co:5432)
  throw new Error(
    'DATABASE_URL environment variable is required for database migrations.\n' +
    'Get your connection string from Supabase Dashboard:\n' +
    'Project Settings > Database > Connection string > Connection pooling (NOT Direct connection)\n' +
    'Format: postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-us-east-2.pooler.supabase.com:6543/postgres\n' +
    'Add it to your .env file as: DATABASE_URL=postgresql://...'
  );
}

export default defineConfig({
  schema: './drizzle/schema.ts',
  out: './drizzle/migrations',
  dialect: 'postgresql',
  dbCredentials: {
    url: connectionString,
  },
  verbose: true,
  strict: true,
});
