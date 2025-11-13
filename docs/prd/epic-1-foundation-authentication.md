# Epic 1: Foundation & Authentication

**Expanded Goal:**
Establish the technical foundation for the Personalized Vocabulary Recommendation Engine by setting up the monorepo structure, initializing Next.js and FastAPI projects, configuring Supabase for authentication and database hosting, and implementing secure educator login. This epic delivers a working authentication system where educators can register, log in via email/password or Google OAuth, and access an authenticated dashboard, validating the core infrastructure before feature development begins.

## Story 1.1: Initialize Monorepo and Project Structure

As a **developer**,
I want **a monorepo with Next.js and FastAPI projects initialized with proper tooling**,
so that **the team has a consistent development environment and can begin building features**.

### Acceptance Criteria:

1. Monorepo created with structure:
   ```
   vocab-builder/
   ├── web/          # Next.js 14+ with TypeScript
   ├── api/          # FastAPI with Python 3.11+
   ├── docs/         # Documentation
   ├── data/         # Word lists (placeholder)
   └── README.md
   ```

2. Next.js project (`web/`) includes:
   - TypeScript configured (strict mode)
   - Tailwind CSS installed and configured
   - shadcn/ui initialized with at least one component installed
   - App Router (Next.js 13+ structure)
   - ESLint and Prettier configured

3. FastAPI project (`api/`) includes:
   - Python virtual environment setup
   - `requirements.txt` with FastAPI, uvicorn, pydantic
   - Basic main.py with health check endpoint (`GET /health`)
   - Ruff or Black formatter configured
   - Type hints with mypy configuration

4. Git repository initialized with:
   - `.gitignore` for Node.js and Python
   - Initial commit with project structure
   - README with setup instructions

5. Both projects run locally:
   - `cd web && npm run dev` starts Next.js on localhost:3000
   - `cd api && uvicorn main:app --reload` starts FastAPI on localhost:8000
   - Health check endpoint returns 200 OK

6. Pre-commit hooks configured (optional but recommended):
   - Format and lint on commit

## Story 1.2: Set Up Supabase Project and Core Database Schema

As a **developer**,
I want **a Supabase project with core database tables and RLS policies configured**,
so that **we have a secure, hosted PostgreSQL database ready for application data**.

### Acceptance Criteria:

1. Supabase project created with:
   - Project name: "vocab-builder" (or similar)
   - Region selected (closest to target users)
   - Database password stored securely

2. Core database tables created via Supabase SQL editor:
   - `educators` table (id, email, name, school, created_at)
   - `students` table (id, educator_id, display_name, grade_level, created_at)
   - `documents` table (id, student_id, title, subject, content_s3_key, uploaded_at)
   - Foreign key constraints properly defined
   - Indexes on common query fields (educator_id, student_id)

3. Row-Level Security (RLS) policies implemented:
   - `educators` table: Users can only read/update their own row
   - `students` table: Educators can only access their own students
   - `documents` table: Educators can only access documents for their students
   - RLS enabled on all tables

4. Supabase Auth configured:
   - Email/password provider enabled
   - Google OAuth provider configured (client ID/secret from Google Cloud Console)
   - Email confirmation disabled for development (can enable later)

5. Environment variables documented:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY` (for backend use)

6. Connection test successful:
   - Can connect to Supabase from local machine
   - Can query tables via Supabase Studio

## Story 1.3: Implement Educator Authentication in Next.js

As an **educator**,
I want **to register and log in using email/password or Google OAuth**,
so that **I can securely access my personalized dashboard**.

### Acceptance Criteria:

1. Supabase client configured in Next.js:
   - `@supabase/auth-helpers-nextjs` installed
   - Supabase client initialized with environment variables
   - Middleware configured to refresh session

2. Login page (`/login`) implemented with:
   - Email/password input fields
   - "Sign In" button (calls Supabase auth)
   - "Sign in with Google" button (Google OAuth flow)
   - Link to sign-up page
   - Error messages display for invalid credentials
   - Uses shadcn/ui components (Input, Button, Card)

3. Sign-up page (`/signup`) implemented with:
   - Email, password, name, school (optional) input fields
   - "Create Account" button
   - Creates educator record in `educators` table after successful auth
   - Redirects to dashboard on success
   - Validation for password strength, email format

4. Authentication state management:
   - Session persists across page refreshes
   - Unauthenticated users redirected to `/login`
   - Authenticated users can access protected routes

5. Sign-out functionality:
   - User menu with "Sign Out" button
   - Clears session and redirects to `/login`

6. Testing:
   - Can create account with email/password
   - Can log in with created account
   - Can log in with Google OAuth (test account)
   - Session persists after page refresh
   - Cannot access dashboard when logged out

## Story 1.4: Create Authenticated Educator Dashboard (Empty State)

As an **educator**,
I want **to see a personalized dashboard after logging in**,
so that **I can access student management features** (even if empty initially).

### Acceptance Criteria:

1. Dashboard page (`/dashboard`) implemented with:
   - Protected route (requires authentication)
   - Header with app branding and user menu (name, sign out)
   - Main content area showing empty state:
     - Message: "No students yet. Add your first student to get started!"
     - "Add New Student" button (non-functional placeholder)
   - Responsive layout using Tailwind CSS
   - Uses shadcn/ui components (Button, Card, Avatar)

2. Layout component created:
   - Shared layout for authenticated pages
   - Navigation/header
   - Main content area
   - Footer (optional)

3. User menu displays:
   - Educator's name (from `educators` table)
   - Email
   - "Sign Out" option

4. Routing logic:
   - `/` redirects to `/dashboard` if authenticated
   - `/` redirects to `/login` if not authenticated
   - `/dashboard` redirects to `/login` if not authenticated

5. Basic styling applied:
   - Professional, clean design
   - Follows shadcn/ui design system
   - Responsive (works on desktop and tablet)

6. Testing:
   - Authenticated educator sees dashboard with their name
   - Unauthenticated user redirected to login
   - Sign out button works and redirects to login
   - Empty state message displays correctly

## Story 1.5: Set Up FastAPI with Supabase JWT Verification

As a **developer**,
I want **FastAPI to verify Supabase JWT tokens for authenticated requests**,
so that **backend API endpoints are secure and only accessible to authenticated educators**.

### Acceptance Criteria:

1. Dependencies installed in FastAPI:
   - `supabase-py` (Supabase Python client)
   - `python-jose[cryptography]` (JWT verification)
   - `python-dotenv` (environment variables)

2. Environment variables configured:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`

3. Supabase client initialized in FastAPI:
   - Client configured with service role key
   - Can perform database operations

4. Authentication middleware implemented:
   - Extracts JWT from `Authorization: Bearer <token>` header
   - Verifies JWT signature using Supabase JWKS endpoint (`https://<project>.supabase.co/auth/v1/.well-known/jwks.json`)
   - Uses asymmetric key verification (modern approach, replaces legacy JWT secret)
   - Extracts educator ID from token
   - Attaches educator ID to request context
   - Returns 401 Unauthorized for invalid/missing tokens

5. Protected endpoint created for testing:
   - `GET /api/me` - Returns current educator info
   - Requires valid JWT
   - Returns educator data from `educators` table

6. CORS configured:
   - Allow requests from Next.js frontend (localhost:3000 in dev)
   - Proper headers for credentials

7. Testing:
   - Health check endpoint (`GET /health`) works without auth
   - Protected endpoint returns 401 without token
   - Protected endpoint returns educator data with valid token from Next.js
   - Can query Supabase from FastAPI using service role

## Story 1.6: Set Up AWS S3 Bucket for Document Storage

As a **developer**,
I want **an S3 bucket configured for secure document storage**,
so that **uploaded student documents (essays, transcripts) can be stored and retrieved safely**.

### Acceptance Criteria:

1. AWS S3 bucket created:
   - Bucket name: `vocab-builder-documents-[env]` (e.g., dev, prod)
   - Region: Same as FastAPI deployment (for low latency)
   - Versioning enabled (optional but recommended)

2. Security configuration:
   - Block all public access enabled
   - Server-side encryption enabled (SSE-S3 or SSE-KMS)
   - Bucket policy allows access only from FastAPI IAM role

3. IAM configuration:
   - IAM user or role created for FastAPI
   - Policy attached with permissions:
     - `s3:PutObject` (upload documents)
     - `s3:GetObject` (retrieve documents)
     - `s3:DeleteObject` (delete documents)
   - Access key/secret stored securely (AWS Secrets Manager or env vars)

4. FastAPI S3 integration:
   - `boto3` library installed
   - S3 client configured with credentials
   - Environment variables:
     - `AWS_S3_BUCKET`
     - `AWS_REGION`
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`

5. Utility functions created in FastAPI:
   - `upload_document(file, key)` - Uploads file to S3
   - `get_document(key)` - Retrieves file from S3
   - `generate_presigned_url(key, expiration)` - Generates temporary download URL

6. Test endpoint created:
   - `POST /api/test-upload` - Accepts file, uploads to S3, returns key
   - `GET /api/test-download/{key}` - Returns pre-signed URL for download

7. Testing:
   - Can upload text file to S3 via test endpoint
   - Can retrieve uploaded file via pre-signed URL
   - File is encrypted at rest (verify in S3 console)
   - Cannot access file directly via public URL

## Story 1.7: Deploy Frontend to Vercel and Backend to AWS

As a **developer**,
I want **the Next.js app deployed to Vercel and FastAPI deployed to AWS**,
so that **the application is accessible online and we have a production-like environment for testing**.

### Acceptance Criteria:

1. Frontend deployment (Vercel):
   - GitHub repository connected to Vercel
   - Automatic deployments configured on push to `main`
   - Environment variables configured in Vercel:
     - `NEXT_PUBLIC_SUPABASE_URL`
     - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
     - `NEXT_PUBLIC_API_URL` (FastAPI URL)
   - Deployment successful, accessible via Vercel URL
   - Custom domain configured (optional)

2. Backend deployment (AWS Lambda or ECS):
   - **Option A: AWS Lambda (recommended for MVP):**
     - FastAPI containerized using Docker
     - Container pushed to ECR (Elastic Container Registry)
     - Lambda function created from container image
     - API Gateway configured to route HTTP requests to Lambda
     - Environment variables configured in Lambda
   - **Option B: AWS ECS Fargate:**
     - FastAPI containerized using Docker
     - ECS task definition created
     - Fargate service deployed
     - Application Load Balancer configured

3. Environment variables configured in AWS:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `AWS_S3_BUCKET`
   - `AWS_REGION`
   - OpenAI/OpenRouter keys (for later use)
   - Note: JWT verification uses JWKS endpoint, no JWT_SECRET needed

4. Networking and security:
   - HTTPS enabled for both frontend and backend
   - CORS properly configured for production domains
   - API Gateway/ALB health checks configured

5. CI/CD pipeline (basic):
   - GitHub Actions workflow for backend:
     - Build Docker image on push to `main`
     - Push to ECR
     - Update Lambda/ECS with new image
   - Vercel handles frontend CI/CD automatically

6. Testing:
   - Can access deployed Next.js app via Vercel URL
   - Can log in via deployed frontend
   - Frontend can call deployed FastAPI health check endpoint
   - Protected endpoint works with JWT from deployed frontend
   - S3 upload/download works from deployed backend

7. Documentation updated:
   - Deployment URLs documented
   - Deployment process documented in README
   - Environment variable setup guide

---
