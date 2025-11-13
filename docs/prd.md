# Personalized Vocabulary Recommendation Engine - Product Requirements Document (PRD)

**Project:** Personalized Vocabulary Recommendation Engine for Middle School Students
**Organization:** Flourish Schools
**Version:** 1.0
**Date:** 2025-11-12
**Author:** John (Product Manager)

---

## Goals and Background Context

### Goals

- Automate vocabulary gap identification for middle school educators, reducing manual analysis time
- Provide personalized, grade-appropriate vocabulary recommendations (grades 6-12) based on student writing samples and transcripts
- Enable educators to track student vocabulary progression over time with clear visualizations
- Build a privacy-compliant system that securely stores student data while maintaining educator access
- Deliver subject-aware recommendations (ELA, Math, Science, Social Studies) that fit student writing contexts
- Track adoption of recommended vocabulary in subsequent student work to measure effectiveness

### Background Context

Middle school educators face a significant challenge in personalizing vocabulary development for students. Manual analysis of student writing and conversation transcripts is time-consuming and often fails to provide targeted recommendations aligned with each student's proficiency level. This lack of personalized vocabulary instruction can hinder language acquisition and academic performance.

The Personalized Vocabulary Recommendation Engine addresses this gap by leveraging AI to automatically analyze student text input, build dynamic vocabulary profiles, and generate grade-appropriate word recommendations. By using Common Core vocabulary standards and grade-level word lists (6th-12th grade), the system provides recommendations that educators trust and students can realistically adopt. The system will track vocabulary usage over time, providing insights into student growth and the effectiveness of recommendations.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-11-12 | 1.0 | Initial PRD draft | John (PM) |

---

## Requirements

### Functional Requirements

**Student & Educator Management**
- **FR1:** System shall support educator authentication with role-based access control, allowing educators to access only their own students' data
- **FR2:** System shall allow educators to create student profiles with pseudonymized identifiers (display names) and grade level (6-8)
- **FR3:** System shall associate each student with a single educator account

**Document Management**
- **FR4:** System shall accept text input in the form of essays, writing samples, and conversation transcripts
- **FR5:** System shall allow educators to upload documents for students with required metadata: title and subject (ELA, Math, Science, Social Studies)
- **FR6:** System shall store uploaded documents securely in S3 with encryption at rest
- **FR7:** System shall support multiple document uploads per student over time

**Vocabulary Analysis**
- **FR8:** System shall extract and lemmatize unique words from each uploaded document
- **FR9:** System shall map extracted words to grade-level vocabulary lists (grades 6-12) sourced from Common Core standards
- **FR10:** System shall calculate a vocabulary profile for each document showing distribution of words by grade level (e.g., 70% grade 6, 25% grade 7, 5% grade 8)
- **FR11:** System shall compute an average vocabulary grade level for each student based on their documents

**Recommendation Generation**
- **FR12:** System shall identify vocabulary gaps by finding contexts where students use lower-grade words
- **FR13:** System shall generate personalized word recommendations using LangChain and OpenAI API to suggest higher-grade alternatives from the grade-level word lists
- **FR14:** System shall filter recommendations by document subject, suggesting subject-appropriate vocabulary
- **FR15:** System shall allow customizable recommendation counts (default: 10 words, range: 5-20)
- **FR16:** Each recommendation shall include: recommended word, current grade level, student's current usage pattern, example sentence in context, and rationale for recommendation

**Usage Tracking**
- **FR17:** System shall track when students adopt recommended vocabulary in subsequent documents
- **FR18:** System shall calculate recommendation adoption rate as a percentage of recommended words successfully used
- **FR19:** System shall update recommendation status ('pending', 'adopted', 'not_used') based on usage tracking

**Progress Tracking & Insights**
- **FR20:** System shall store historical vocabulary analyses for each student to enable trend analysis
- **FR21:** System shall visualize vocabulary progression over time with grade level distribution charts (pie/bar) and progress line graphs
- **FR22:** System shall display subject-specific progress when multiple subjects are present
- **FR23:** System shall generate AI-powered insights using LangChain to provide actionable recommendations for educators based on student progress patterns

**Educator Dashboard**
- **FR24:** System shall provide a dashboard showing overview of all students with key metrics (current grade level, document count, recent progress)
- **FR25:** System shall provide detailed student pages showing: student info, uploaded documents, current vocabulary profile, subject-filtered recommendations, progress visualizations, and AI-generated insights
- **FR26:** System shall allow educators to view and filter recommendations by subject area

### Non-Functional Requirements

**Performance**
- **NFR1:** Document analysis shall complete within 30 seconds for documents up to 5,000 words
- **NFR2:** Dashboard shall load student list within 2 seconds for up to 100 students
- **NFR3:** API endpoints shall respond within 500ms for standard queries (excluding AI processing)

**Security & Privacy**
- **NFR4:** All student data shall be pseudonymized, with no personally identifiable information (PII) stored in plain text
- **NFR5:** All data at rest shall be encrypted using Supabase encryption and S3 server-side encryption
- **NFR6:** All data in transit shall use HTTPS/TLS encryption
- **NFR7:** System shall implement role-based access control ensuring educators can only access their own students' data
- **NFR8:** System shall validate and sanitize all user inputs to prevent SQL injection and XSS attacks

**Scalability**
- **NFR9:** System shall handle at least 50 concurrent educators without performance degradation
- **NFR10:** System shall support storage of at least 10,000 documents without performance impact
- **NFR11:** Database queries shall be optimized with appropriate indexes for common access patterns

**Reliability & Availability**
- **NFR12:** System shall have 99% uptime during school hours (6 AM - 6 PM local time)
- **NFR13:** System shall implement error handling with graceful degradation and user-friendly error messages
- **NFR14:** System shall implement retry logic for transient AI API failures

**Data Management**
- **NFR15:** System shall maintain data integrity with foreign key constraints and transaction management
- **NFR16:** Word list data shall be version-controlled and updatable without system downtime

**Testing**
- **NFR17:** System shall have unit tests covering core vocabulary analysis logic with >80% code coverage
- **NFR18:** System shall have integration tests for all API endpoints
- **NFR19:** System shall have end-to-end tests for critical user flows (document upload, recommendation generation)

**Deployment & Operations**
- **NFR20:** Frontend (Next.js) shall deploy to Vercel with automatic deployments from main branch
- **NFR21:** Backend (FastAPI) shall deploy to AWS (ECS or Lambda) with containerization via Docker
- **NFR22:** PostgreSQL database shall deploy to Supabase with encryption and RLS enabled
- **NFR23:** System shall use AWS free-tier resources where feasible to minimize costs

**AI Integration**
- **NFR24:** System shall use LangChain for AI orchestration to enable model interoperability
- **NFR25:** System shall support switching between OpenAI and OpenRouter API providers without code changes
- **NFR26:** AI API calls shall have timeout limits (30 seconds) to prevent hanging requests

---

## User Interface Design Goals

### Overall UX Vision

The interface should prioritize **clarity and efficiency** for time-constrained educators. The design should feel professional and trustworthy (appropriate for educational context) while remaining approachable and easy to navigate. Key principles:

- **Progressive disclosure:** Show summary views by default, allow drill-down into details
- **Data-driven insights front and center:** Visualizations and key metrics should be immediately visible, not buried in tabs
- **Minimal friction for core workflows:** Document upload and student creation should be fast (<3 clicks from dashboard)
- **Trust through transparency:** Show how recommendations were generated, don't black-box the AI
- **Educator empowerment:** Provide controls (filters, customization) without overwhelming with options

### Key Interaction Paradigms

**Card-based browsing:** Student dashboard uses cards for scannable overview with key stats visible at a glance

**Drag-and-drop uploads:** Document upload supports drag-and-drop for quick batch additions

**Inline filtering:** Recommendations and progress views have inline subject filters (tabs or dropdowns) to avoid context switching

**Contextual actions:** Primary actions (upload document, view details) appear on hover/focus for cleaner interface

**Real-time feedback:** Show progress indicators during document analysis, use optimistic UI updates where possible

**Data visualization as primary interface:** Charts and graphs are interactive (hover for details, click to filter), not just static displays

### Core Screens and Views

**Login Screen**
- Supabase Auth UI integration with:
  - Email/password sign-in
  - Google OAuth option ("Sign in with Google" button)
  - Password reset flow (Supabase magic link)
- Clean, professional branding
- Future: Additional OAuth providers (Microsoft, Apple) if needed

**Main Dashboard** (Educator Home)
- Student grid/list with cards showing:
  - Student display name
  - Current grade level
  - Current vocabulary grade level
  - Recent progress indicator (↑↓→)
  - Document count
- "Add New Student" CTA button prominently placed
- Quick stats header (total students, avg improvement, etc.)
- User menu with sign-out option

**Create Student Page**
- Simple form: display name, grade level (6-8 dropdown)
- Immediate redirect to student detail page after creation

**Student Detail Page** (Most complex view)
- **Header:** Student name, grade level, overall vocabulary stats
- **Section 1: Upload Documents**
  - Drag-drop zone or file picker
  - Subject selector (ELA, Math, Science, Social Studies)
  - Title input
  - Upload button (triggers FastAPI analysis)
  - List of previously uploaded documents (date, title, subject)
- **Section 2: Current Vocabulary Profile**
  - Pie chart or bar chart showing grade-level distribution
  - Average grade level prominently displayed
  - Based on most recent analysis
- **Section 3: Recommendations**
  - Subject filter tabs/dropdown
  - Count selector (5, 10, 15, 20)
  - Table/list view with columns:
    - Word
    - Grade level
    - Current usage (what student says now)
    - Example sentence
    - Subject tag
  - Expandable rows for full rationale/context
- **Section 4: Progress Over Time**
  - Line graph showing vocabulary grade level progression
  - Toggle for subject-specific views
  - Display recommendation adoption rate
  - AI-generated insights box (narrative text)

**Settings Page** (Phase 2+)
- Educator profile settings (name, email - managed by Supabase)
- Account management (password change via Supabase)

### Accessibility: WCAG AA

**Target compliance level:** WCAG 2.1 Level AA

**Key requirements:**
- Sufficient color contrast ratios (4.5:1 for text)
- Keyboard navigation for all interactive elements
- Screen reader compatibility with semantic HTML and ARIA labels
- Focus indicators visible on all interactive elements
- Form labels and error messages clearly associated
- Charts have text alternatives and data tables

### Branding

**Style:** Clean, modern, professional educational tool aesthetic

**Tone:** Trustworthy, empowering, approachable (not playful/gamified for educator interface)

**Visual approach:**
- Simple, uncluttered layouts with generous whitespace
- Professional typography (clear, readable sans-serif)
- Data visualization as primary visual interest (no decorative graphics)
- Muted, professional color palette suitable for educational context
- Use shadcn/ui component library for consistent, accessible components

### Target Device and Platforms: Web Responsive

**Primary target:** Desktop/laptop browsers (educators typically work on computers for planning)

**Secondary target:** Tablet (iPads common in schools for educator use)

**Responsive breakpoints:**
- Desktop (1280px+): Full multi-column layouts
- Tablet (768px-1279px): Adjusted layouts, some sections stack
- Mobile (320px-767px): Fully stacked layout, optimized for viewing (not primary use case)

**Browser support:**
- Modern evergreen browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)

**Technical approach:**
- Tailwind CSS for responsive utilities
- shadcn/ui component library (already integrated in existing Next.js setup)
- Mobile-first CSS with progressive enhancement for larger screens
- Touch-friendly targets (44px minimum) for tablet support

---

## Technical Assumptions

### Repository Structure: Monorepo

```
vocab-builder/
├── web/                    # Next.js frontend
│   ├── app/               # App router (Next.js 13+)
│   ├── components/        # shadcn/ui components
│   ├── lib/               # Utilities, Supabase client
│   └── ...
├── api/                   # FastAPI Python backend
│   ├── main.py            # FastAPI app entry point
│   ├── routers/           # API route handlers
│   ├── services/          # Vocab analysis, AI logic
│   ├── models/            # Pydantic models
│   └── requirements.txt
├── docs/                  # Documentation, PRD, architecture
├── scripts/               # Utility scripts, word list compilation
└── data/                  # Grade-level word lists (to be compiled)
```

**Rationale:** Monorepo keeps frontend and backend code in sync, simplifies deployment coordination, and enables shared types/constants.

### Service Architecture

**Hybrid Architecture: Next.js Frontend + Supabase + FastAPI Backend**

**Component breakdown:**

1. **Next.js Frontend (Vercel)**
   - User interface and presentation layer
   - Supabase authentication integration
   - Direct Supabase queries for simple CRUD (students, documents list)
   - API calls to FastAPI for AI processing

2. **Supabase (Database + Auth)**
   - PostgreSQL database hosting
   - Built-in authentication (email/password + Google OAuth)
   - Row-Level Security (RLS) for educator data isolation
   - Real-time subscriptions (optional future enhancement)
   - RESTful API for basic CRUD operations

3. **FastAPI Backend (AWS Lambda or ECS)**
   - Vocabulary analysis engine
   - Recommendation generation (LangChain + OpenAI)
   - Document processing and NLP logic
   - Usage tracking calculations
   - AI-generated insights
   - Communicates with Supabase using service role key for database access
   - Verifies Supabase JWT tokens for authenticated requests

4. **AWS S3**
   - Document file storage (essays, transcripts)
   - Encrypted at rest
   - Accessed via pre-signed URLs

**Data flow example (Document Upload):**
```
1. Educator uploads document via Next.js
2. Next.js uploads file to S3 (pre-signed URL)
3. Next.js creates document record in Supabase (via Supabase client)
4. Next.js calls FastAPI: POST /api/analyze with document ID
5. FastAPI fetches document from S3
6. FastAPI performs vocab analysis (NLP + AI)
7. FastAPI writes results to Supabase (vocab_analyses, recommendations tables)
8. Next.js polls or receives callback when analysis complete
9. UI updates with new recommendations
```

**Rationale:**
- **Supabase handles auth complexity** - Eliminates need to build auth system in Python
- **FastAPI focuses on AI/ML** - Keeps Python backend doing what it does best
- **Clear separation of concerns** - Frontend (presentation), Supabase (data + auth), FastAPI (analysis)
- **Scalable** - Each component can scale independently

### Testing Requirements

**Test Coverage Strategy:**

**Unit Tests (>80% coverage goal):**
- **Python/FastAPI:**
  - Vocabulary analysis logic (word extraction, lemmatization, grade-level mapping)
  - Recommendation generation algorithms
  - Usage tracking calculations
  - Data validation and sanitization
  - Tool: pytest

- **Next.js:**
  - Component rendering (React Testing Library)
  - Utility functions
  - Data transformations
  - Tool: Jest + React Testing Library

**Integration Tests:**
- **FastAPI endpoints:**
  - Test all API routes with mock data
  - Test Supabase integration (using test database)
  - Test S3 integration (using localstack or minio)
  - Tool: pytest with TestClient

- **Supabase integration:**
  - Test RLS policies
  - Test authentication flows
  - Tool: Supabase test utilities

**End-to-End Tests (Critical flows only):**
- Educator login → create student → upload document → view recommendations
- Document upload triggers analysis and displays results
- Tool: Playwright or Cypress

**Manual Testing Requirements:**
- AI-generated recommendations quality review (human evaluation)
- UI/UX usability testing with mock educators
- Cross-browser compatibility checks

**Test Environment:**
- Separate Supabase project for staging/testing
- Mock OpenAI API responses for deterministic tests
- Seeded test data (sample students, documents, word lists)

**Rationale:**
- Full testing pyramid ensures reliability in educational context
- High unit test coverage for core analysis logic (bugs here = bad recommendations)
- Integration tests catch Supabase/FastAPI integration issues
- E2E tests for critical flows only (expensive to maintain)
- Manual testing for AI quality (hard to automate subjective quality assessment)

### Additional Technical Assumptions and Requests

**Programming Languages & Frameworks:**
- **Frontend:** TypeScript + Next.js 14+ (App Router) + React 18+
- **Backend:** Python 3.11+ + FastAPI
- **Styling:** Tailwind CSS + shadcn/ui components (already set up)
- **Database:** PostgreSQL 15+ (via Supabase)

**Authentication & Authorization:**
- **Provider:** Supabase Auth
- **Methods:** Email/password (primary), Google OAuth (secondary)
- **Session management:** Supabase handles JWT tokens, refresh tokens
- **Frontend auth:** @supabase/auth-helpers-nextjs
- **Backend auth:** Verify Supabase JWT tokens in FastAPI middleware
- **Row-Level Security:** Supabase RLS policies ensure educators only access their students

**AI & NLP Stack:**
- **Orchestration:** LangChain (Python)
- **LLM Provider:** OpenAI (initially), switchable to OpenRouter via LangChain config
- **NLP Libraries:** spaCy or NLTK for tokenization and lemmatization
- **Embeddings:** Optional (not in MVP, but LangChain supports if needed later)

**Data Storage:**
- **Structured data:** Supabase PostgreSQL
  - Students, educators, documents metadata, analyses, recommendations
  - RLS policies for data isolation
- **Unstructured data:** AWS S3
  - Document files (essays, transcripts)
  - Server-side encryption enabled
- **Reference data:** Grade-level word lists
  - JSON files in `/data` directory (version controlled)
  - Loaded into `grade_words` table on initialization

**Deployment:**
- **Frontend:** Vercel (automatic deployments from `main` branch)
- **Backend:** AWS Lambda (containerized FastAPI) or ECS Fargate
  - Docker container for Python dependencies
  - Environment variables for Supabase URL, keys, OpenAI key
- **Database:** Supabase (managed PostgreSQL hosting)
- **Storage:** AWS S3 (same region as FastAPI for low latency)
- **CI/CD:** GitHub Actions
  - Lint, test, build on PR
  - Deploy to staging on merge to `develop`
  - Deploy to production on merge to `main`

**Environment Variables:**
```
# Frontend (.env.local)
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_API_URL=...  # FastAPI endpoint

# Backend (.env)
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...  # For backend database access
OPENAI_API_KEY=...
# OR
OPENROUTER_API_KEY=...
AWS_S3_BUCKET=...
AWS_REGION=...
```

**Key Libraries:**
- **Next.js:**
  - `@supabase/auth-helpers-nextjs` - Auth integration
  - `@supabase/supabase-js` - Supabase client
  - `recharts` - Data visualization
  - `zod` - Runtime type validation

- **FastAPI:**
  - `langchain` - AI orchestration
  - `openai` - OpenAI API client
  - `spacy` or `nltk` - NLP processing
  - `supabase-py` - Supabase Python client
  - `boto3` - AWS S3 client
  - `pydantic` - Data validation

**Word List Compilation:**
- **Source:** Common Core vocabulary standards (grades 6-12)
- **Format:** JSON files with structure:
  ```json
  {
    "grade": 8,
    "subject": "ELA",
    "words": [
      {
        "word": "analyze",
        "definition": "examine in detail",
        "example": "Analyze the author's argument",
        "frequency_rank": 1245
      }
    ]
  }
  ```
- **Storage:** `/data/word-lists/` directory (version controlled)
- **Import:** Script to load JSON into Supabase `grade_words` table
- **Responsibility:** Developer will compile from various sources and provide in expected format

**API Design:**
- **RESTful conventions** for FastAPI endpoints
- **JSON request/response** bodies
- **Consistent error responses** with proper HTTP status codes
- **API documentation:** FastAPI auto-generates OpenAPI/Swagger docs

**Code Quality:**
- **Linting:** ESLint (TypeScript), Ruff or Black (Python)
- **Type checking:** TypeScript strict mode, mypy (Python)
- **Pre-commit hooks:** Format, lint, type check before commit
- **Code reviews:** Required for all PRs

**Logging & Monitoring:**
- **Application logs:** Structured JSON logging (FastAPI)
- **Error tracking:** Sentry or similar (Phase 2)
- **Performance monitoring:** Vercel Analytics (frontend), CloudWatch (backend)
- **AI API usage tracking:** Log token consumption for cost monitoring

**Cost Management:**
- **Supabase:** Free tier (500MB DB, 50K MAU, 2GB bandwidth)
- **Vercel:** Free tier (100GB bandwidth, unlimited deployments for personal projects)
- **AWS Lambda:** Free tier (1M requests/month, 400K GB-seconds compute)
- **S3:** Free tier (5GB storage, 20K GET requests, 2K PUT requests)
- **OpenAI API:** Pay-as-you-go (monitor usage, set budget alerts)
- **Estimate:** <$50/month for pilot deployment with ~50 educators

---

## Epic List

### Epic 1: Foundation & Authentication
**Goal:** Establish project infrastructure (monorepo, Next.js, FastAPI, Supabase) with working authentication, enabling educators to securely log in and access an empty dashboard ready for future features.

### Epic 2: Student Management & Document Upload
**Goal:** Enable educators to create and manage student profiles, upload documents (essays/transcripts) with subject metadata to S3, and view their uploaded document library per student.

### Epic 3: Vocabulary Analysis Engine
**Goal:** Build the core NLP pipeline that analyzes uploaded documents, extracts vocabulary, maps words to grade levels using compiled Common Core word lists, and generates vocabulary profiles showing grade-level distribution for each student.

### Epic 4: Personalized Recommendations
**Goal:** Implement AI-powered recommendation engine using LangChain and OpenAI to generate subject-aware, grade-appropriate vocabulary suggestions based on student writing, displaying actionable recommendations in the educator dashboard.

### Epic 5: Progress Tracking & Insights
**Goal:** Enable historical vocabulary tracking, visualize student progress over time with interactive charts, detect adoption of recommended words in subsequent writing, and generate AI-powered insights for educators.

---

## Epic 1: Foundation & Authentication

**Expanded Goal:**
Establish the technical foundation for the Personalized Vocabulary Recommendation Engine by setting up the monorepo structure, initializing Next.js and FastAPI projects, configuring Supabase for authentication and database hosting, and implementing secure educator login. This epic delivers a working authentication system where educators can register, log in via email/password or Google OAuth, and access an authenticated dashboard, validating the core infrastructure before feature development begins.

### Story 1.1: Initialize Monorepo and Project Structure

As a **developer**,
I want **a monorepo with Next.js and FastAPI projects initialized with proper tooling**,
so that **the team has a consistent development environment and can begin building features**.

#### Acceptance Criteria:

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

### Story 1.2: Set Up Supabase Project and Core Database Schema

As a **developer**,
I want **a Supabase project with core database tables and RLS policies configured**,
so that **we have a secure, hosted PostgreSQL database ready for application data**.

#### Acceptance Criteria:

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

### Story 1.3: Implement Educator Authentication in Next.js

As an **educator**,
I want **to register and log in using email/password or Google OAuth**,
so that **I can securely access my personalized dashboard**.

#### Acceptance Criteria:

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

### Story 1.4: Create Authenticated Educator Dashboard (Empty State)

As an **educator**,
I want **to see a personalized dashboard after logging in**,
so that **I can access student management features** (even if empty initially).

#### Acceptance Criteria:

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

### Story 1.5: Set Up FastAPI with Supabase JWT Verification

As a **developer**,
I want **FastAPI to verify Supabase JWT tokens for authenticated requests**,
so that **backend API endpoints are secure and only accessible to authenticated educators**.

#### Acceptance Criteria:

1. Dependencies installed in FastAPI:
   - `supabase-py` (Supabase Python client)
   - `python-jose[cryptography]` (JWT verification)
   - `python-dotenv` (environment variables)

2. Environment variables configured:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_JWT_SECRET` (from Supabase project settings)

3. Supabase client initialized in FastAPI:
   - Client configured with service role key
   - Can perform database operations

4. Authentication middleware implemented:
   - Extracts JWT from `Authorization: Bearer <token>` header
   - Verifies JWT signature using Supabase JWT secret
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

### Story 1.6: Set Up AWS S3 Bucket for Document Storage

As a **developer**,
I want **an S3 bucket configured for secure document storage**,
so that **uploaded student documents (essays, transcripts) can be stored and retrieved safely**.

#### Acceptance Criteria:

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

### Story 1.7: Deploy Frontend to Vercel and Backend to AWS

As a **developer**,
I want **the Next.js app deployed to Vercel and FastAPI deployed to AWS**,
so that **the application is accessible online and we have a production-like environment for testing**.

#### Acceptance Criteria:

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
   - `SUPABASE_JWT_SECRET`
   - `AWS_S3_BUCKET`
   - `AWS_REGION`
   - OpenAI/OpenRouter keys (for later use)

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

## Epic 2: Student Management & Document Upload

**Expanded Goal:**
Enable educators to create and manage student profiles with pseudonymized identifiers, upload student documents (essays, transcripts) to secure cloud storage with subject metadata, and view their complete document library organized by student. This epic delivers the core data collection workflow, allowing educators to build their student portfolio before analysis features are available.

### Story 2.1: Create Student Profile Form

As an **educator**,
I want **to create new student profiles with basic information**,
so that **I can organize and track vocabulary development for each of my students**.

#### Acceptance Criteria:

1. "Add New Student" page (`/students/new`) implemented with form:
   - Display name input (text field, required)
   - Grade level selector (dropdown: 6, 7, 8, required)
   - Form validation (display name not empty, grade level selected)
   - "Create Student" button
   - "Cancel" button (returns to dashboard)
   - Uses shadcn/ui form components

2. Form submission:
   - Creates record in `students` table via Supabase client
   - Associates student with logged-in educator (educator_id)
   - Generates unique UUID for student
   - Sets created_at timestamp

3. Success handling:
   - Redirects to student detail page after creation
   - Shows success toast notification

4. Error handling:
   - Displays error message if creation fails
   - Validation errors shown inline
   - Network errors handled gracefully

5. Testing:
   - Can create student with valid data
   - Cannot submit with empty display name
   - Cannot submit without selecting grade level
   - Student appears in database with correct educator_id
   - RLS prevents creating students for other educators

### Story 2.2: Display Student List on Dashboard

As an **educator**,
I want **to see all my students in a grid/list on the dashboard**,
so that **I can quickly access individual student details and track my roster**.

#### Acceptance Criteria:

1. Dashboard (`/dashboard`) updated to fetch and display students:
   - Queries `students` table filtered by educator_id
   - Displays student cards in responsive grid (3-4 columns on desktop, 1-2 on tablet/mobile)
   - Each card shows:
     - Student display name
     - Grade level
     - Placeholder for vocabulary stats (show "No data yet")
     - Document count (initially 0)
     - "View Details" button/link

2. Empty state handling:
   - Shows "No students yet" message if no students
   - "Add New Student" button prominently displayed

3. Card interactions:
   - Click anywhere on card navigates to student detail page
   - Hover effect for visual feedback
   - Uses shadcn/ui Card component

4. Loading state:
   - Shows skeleton loaders while fetching students
   - Handles slow network gracefully

5. Real-time updates (optional enhancement):
   - Dashboard refreshes when returning from student creation
   - Or use Supabase real-time subscriptions

6. Testing:
   - Dashboard shows all students for logged-in educator
   - Dashboard does not show students from other educators (RLS)
   - Empty state displays when no students exist
   - Can navigate to student detail page from card
   - Newly created student appears in list

### Story 2.3: Create Student Detail Page Structure

As an **educator**,
I want **a dedicated page for each student showing their information and document library**,
so that **I can manage all student-specific data in one place**.

#### Acceptance Criteria:

1. Student detail page (`/students/[id]`) created with:
   - Dynamic route using student ID
   - Fetches student data from Supabase
   - 404 page if student not found or belongs to different educator

2. Page layout includes sections:
   - **Header:** Student display name, grade level, back button to dashboard
   - **Upload Documents section:** Placeholder for upload form (Epic 2.4)
   - **Documents Library section:** List of uploaded documents (initially empty)
   - **Vocabulary Profile section:** Placeholder showing "Upload documents to see vocabulary analysis"
   - **Recommendations section:** Placeholder showing "Analysis coming soon"

3. Documents Library (empty state):
   - Message: "No documents yet. Upload an essay or transcript to get started."
   - Styled table/list ready for document rows

4. Navigation:
   - Back button returns to dashboard
   - Breadcrumbs: Dashboard > [Student Name]

5. Responsive layout:
   - Desktop: Multi-column layout
   - Mobile: Stacked sections

6. Testing:
   - Can navigate to student detail page from dashboard
   - Page displays correct student information
   - Cannot access other educators' students (RLS + route protection)
   - Shows appropriate empty states

### Story 2.4: Implement Document Upload with S3 Integration

As an **educator**,
I want **to upload student documents (essays, transcripts) with subject classification**,
so that **the system can analyze their vocabulary and generate recommendations**.

#### Acceptance Criteria:

1. Upload form added to student detail page with:
   - Document title input (text field, required)
   - Subject selector (dropdown: ELA, Math, Science, Social Studies, required)
   - File picker (accepts .txt, .pdf, .docx)
   - Drag-and-drop zone for file upload
   - "Upload" button
   - File size limit (5MB)
   - Uses shadcn/ui form components

2. Upload workflow (frontend):
   - Validates file type and size
   - Shows upload progress indicator
   - Calls FastAPI endpoint to get pre-signed S3 URL
   - Uploads file directly to S3 using pre-signed URL
   - Calls FastAPI to create document record

3. FastAPI endpoints created:
   - `POST /api/students/{student_id}/documents/upload-url`
     - Generates pre-signed S3 upload URL
     - Returns URL and S3 key
     - Verifies educator owns student (JWT + database check)
   - `POST /api/students/{student_id}/documents`
     - Creates document record in Supabase
     - Stores: student_id, title, subject, content_s3_key, uploaded_at
     - Returns document metadata

4. File storage:
   - Files uploaded to S3 with key format: `{educator_id}/{student_id}/{uuid}.{ext}`
   - S3 server-side encryption enabled
   - Metadata tags: student_id, educator_id, subject

5. Success/error handling:
   - Success: Document appears in library immediately, shows success toast
   - Error: Clear error messages (file too large, unsupported type, network error)
   - Failed uploads don't create orphaned S3 files or database records

6. Testing:
   - Can upload .txt file with valid metadata
   - File appears in S3 bucket with correct key
   - Document record created in database
   - Cannot upload file >5MB
   - Cannot upload unsupported file type
   - Upload progress indicator works
   - Cannot upload document for other educator's students

### Story 2.5: Display Uploaded Documents Library

As an **educator**,
I want **to see a list of all documents I've uploaded for each student**,
so that **I can track what has been analyzed and manage document history**.

#### Acceptance Criteria:

1. Documents Library section on student detail page updated to display:
   - Table/list of documents fetched from `documents` table
   - Columns: Title, Subject, Upload Date, Actions
   - Sorted by upload date (newest first)
   - Empty state if no documents

2. Each document row shows:
   - Document title
   - Subject badge/tag (color-coded: ELA=blue, Math=green, Science=purple, Social Studies=orange)
   - Upload date (formatted as "MMM DD, YYYY" or relative like "2 days ago")
   - Download button (generates pre-signed URL)
   - Delete button (optional for MVP)

3. Download functionality:
   - Click download button calls FastAPI endpoint
   - `GET /api/documents/{document_id}/download`
     - Verifies educator owns document
     - Generates pre-signed S3 URL (15-minute expiration)
     - Returns URL or redirects to URL
   - Browser downloads file

4. Document count displayed:
   - Student card on dashboard shows accurate document count
   - Updates when new documents uploaded

5. Responsive design:
   - Desktop: Full table with all columns
   - Mobile: Stacked cards with key info

6. Testing:
   - Uploaded documents appear in library
   - Can download uploaded document
   - Downloaded file matches uploaded file (content verification)
   - Cannot download documents for other educators' students
   - Document count accurate on dashboard

### Story 2.6: Add Document Deletion (Optional Cleanup)

As an **educator**,
I want **to delete uploaded documents that are no longer needed**,
so that **I can manage my document library and remove mistakes or duplicates**.

#### Acceptance Criteria:

1. Delete button added to each document in library:
   - Trash icon or "Delete" text button
   - Positioned in Actions column

2. Confirmation dialog:
   - Click delete shows confirmation modal
   - Message: "Are you sure you want to delete '[Document Title]'? This action cannot be undone."
   - "Cancel" and "Confirm Delete" buttons
   - Uses shadcn/ui Dialog component

3. Delete workflow:
   - Calls FastAPI endpoint: `DELETE /api/documents/{document_id}`
   - Verifies educator owns document
   - Deletes document record from database
   - Deletes file from S3
   - Returns success response

4. UI updates:
   - Document removed from library immediately (optimistic update)
   - Success toast notification
   - Document count decrements

5. Error handling:
   - If delete fails, restore document in UI
   - Show error message

6. Cascade considerations:
   - If document has associated vocab_analyses or recommendations, delete those too (cascade delete)
   - Or prevent deletion if analyses exist (business decision)

7. Testing:
   - Can delete document
   - Document removed from database
   - File removed from S3
   - Cannot delete other educators' documents
   - Document count updates correctly
   - Deleting last document shows empty state

---

## Epic 3: Vocabulary Analysis Engine

**Expanded Goal:**
Build the core NLP and vocabulary analysis pipeline that processes uploaded documents, extracts and lemmatizes vocabulary, maps words to grade-level standards using compiled Common Core word lists, calculates vocabulary profiles showing grade-level distribution, and displays these insights to educators. This epic delivers the first automated analysis capability, transforming raw text into actionable vocabulary intelligence.

### Story 3.1: Compile and Import Grade-Level Word Lists

As a **developer**,
I want **grade-level word lists (6th-12th grade) compiled from Common Core standards and loaded into the database**,
so that **the analysis engine can map student vocabulary to grade levels**.

#### Acceptance Criteria:

1. Grade-level word lists compiled and formatted:
   - JSON files created in `/data/word-lists/` directory
   - One file per grade level: `grade-6.json`, `grade-7.json`, ..., `grade-12.json`
   - Structure per file:
     ```json
     {
       "grade": 6,
       "words": [
         {
           "word": "analyze",
           "definition": "examine in detail",
           "example": "Analyze the author's argument",
           "subjects": ["ELA"],
           "frequency_rank": 1245
         }
       ]
     }
     ```
   - Minimum 100 words per grade level (target: 300-500)
   - Words sourced from Common Core standards, Academic Word List, or equivalent

2. Database table ready:
   - `grade_words` table schema updated if needed
   - Columns: id, word, grade_level, subject, definition, example_sentence, frequency_rank

3. Import script created (`scripts/import_word_lists.py`):
   - Reads JSON files from `/data/word-lists/`
   - Inserts words into `grade_words` table via Supabase client
   - Handles duplicates (skip or update)
   - Logs import progress and errors

4. Script execution:
   - Run script locally to populate database
   - Verify word count per grade level
   - Create index on `word` column for fast lookups

5. Documentation:
   - README in `/data/word-lists/` explaining sources and format
   - Script usage instructions

6. Testing:
   - Can run import script successfully
   - Database contains expected word counts per grade
   - Can query words by grade level
   - Can query words by subject
   - No duplicate words per grade level

### Story 3.2: Build Text Processing and Word Extraction Service

As a **developer**,
I want **a FastAPI service that extracts and lemmatizes unique words from document text**,
so that **student vocabulary can be accurately analyzed regardless of word forms**.

#### Acceptance Criteria:

1. NLP library installed and configured:
   - Install `spacy` and download English model (`en_core_web_sm` or `en_core_web_md`)
   - Or install `nltk` with WordNet lemmatizer
   - Configure in FastAPI `services/text_processing.py`

2. Text processing service implements functions:
   - `extract_text_from_file(s3_key)` - Retrieves document from S3, extracts text
     - Supports .txt (direct read)
     - Supports .pdf (using `PyPDF2` or `pdfplumber`)
     - Supports .docx (using `python-docx`)
   - `tokenize(text)` - Splits text into words
   - `lemmatize(tokens)` - Converts words to base form (running → run, better → good)
   - `filter_words(tokens)` - Removes stopwords, punctuation, numbers
   - `extract_unique_words(text)` - Full pipeline returning list of unique lemmatized words

3. Word extraction logic:
   - Converts text to lowercase
   - Lemmatizes all words
   - Filters out:
     - Common stopwords (the, and, is, etc.)
     - Punctuation
     - Numbers
     - Words shorter than 3 characters
   - Returns unique words only (set)
   - Maintains word count for frequency analysis (optional)

4. Error handling:
   - Handles corrupted files gracefully
   - Handles unsupported file formats
   - Logs errors with context

5. Performance:
   - Processes 5,000-word document in <10 seconds
   - Uses caching for spaCy/NLTK models (don't reload on every request)

6. Testing:
   - Unit tests with sample text documents
   - Verify "running" lemmatizes to "run"
   - Verify stopwords removed
   - Verify unique words extracted correctly
   - Test with .txt, .pdf, .docx files
   - Handles empty documents
   - Handles documents with only stopwords

### Story 3.3: Implement Grade-Level Mapping Logic

As a **developer**,
I want **to map extracted student vocabulary to grade levels using the word lists**,
so that **we can determine what grade level each student is performing at**.

#### Acceptance Criteria:

1. Grade-level mapping service created (`services/vocab_analysis.py`):
   - Function `map_word_to_grade(word)`:
     - Queries `grade_words` table for word
     - Returns grade level if found, else None
     - Uses lemmatized form for lookup

2. Vocabulary profiling function:
   - `calculate_vocab_profile(unique_words)`:
     - Maps each word to grade level
     - Counts words per grade level
     - Calculates distribution (percentage per grade)
     - Returns:
       ```python
       {
         "total_words": 150,
         "unique_words": 120,
         "grade_distribution": {
           6: 0.70,  # 70% of words are grade 6
           7: 0.20,
           8: 0.05,
           9: 0.03,
           10: 0.02
         },
         "average_grade_level": 6.5,
         "unmapped_words": 15,  # Words not in our lists
         "unmapped_percentage": 0.125
       }
       ```

3. Average grade level calculation:
   - Weighted average: sum(grade * percentage) for all grades
   - Rounds to 1 decimal place

4. Handling unmapped words:
   - Words not found in `grade_words` excluded from grade calculation
   - Tracked separately (may indicate advanced vocabulary or proper nouns)
   - Consider defaulting to grade 12 or excluding entirely (business decision)

5. Performance optimization:
   - Batch query for all words at once (not one-by-one)
   - Use in-memory cache for frequent words
   - Target: Process 100 unique words in <1 second

6. Testing:
   - Unit tests with known word sets
   - Verify grade distribution calculations
   - Verify average grade level accuracy
   - Test with all words mapped (100% coverage)
   - Test with some unmapped words (realistic scenario)
   - Verify performance with large word lists (500+ words)

### Story 3.4: Create Document Analysis Endpoint

As an **educator**,
I want **the system to automatically analyze uploaded documents and calculate vocabulary profiles**,
so that **I can see each student's current vocabulary level without manual effort**.

#### Acceptance Criteria:

1. Analysis endpoint created:
   - `POST /api/documents/{document_id}/analyze`
   - Requires authentication (educator owns document)
   - Triggers full analysis pipeline
   - Returns analysis results

2. Analysis pipeline orchestration:
   - Fetch document metadata from database (title, subject, S3 key)
   - Extract text from S3 file
   - Extract unique words using text processing service
   - Calculate vocabulary profile using grade mapping service
   - Store results in `vocab_analyses` table:
     - document_id, analyzed_at, total_words, unique_words, grade_level_distribution (JSONB), average_grade_level
   - Update document record with `analyzed: true` flag (optional)
   - Return analysis results to frontend

3. Automatic analysis trigger (optional enhancement):
   - After document upload (Story 2.4), automatically call analyze endpoint
   - Or trigger analysis asynchronously (background job)
   - Show "Analyzing..." status in UI

4. Error handling:
   - Handle missing documents
   - Handle corrupted files
   - Handle analysis failures (log error, store partial results)
   - Return meaningful error messages

5. Response format:
   ```json
   {
     "analysis_id": "uuid",
     "document_id": "uuid",
     "total_words": 523,
     "unique_words": 245,
     "grade_distribution": {
       "6": 0.68,
       "7": 0.22,
       "8": 0.07,
       "9": 0.03
     },
     "average_grade_level": 6.6,
     "analyzed_at": "2025-11-12T14:30:00Z"
   }
   ```

6. Testing:
   - Can trigger analysis for uploaded document
   - Analysis results stored in database
   - Analysis completes within 30 seconds for 5,000-word document
   - Cannot analyze other educators' documents
   - Handles various document formats (.txt, .pdf, .docx)
   - Re-analyzing same document creates new analysis record (historical tracking)

### Story 3.5: Display Vocabulary Profile on Student Detail Page

As an **educator**,
I want **to see a visual representation of each student's vocabulary grade level**,
so that **I can quickly understand their current proficiency and track their progress**.

#### Acceptance Criteria:

1. Vocabulary Profile section on student detail page updated with:
   - Fetches latest `vocab_analyses` record for student (most recent across all documents)
   - Or aggregates across all documents (design decision)

2. Displays key metrics:
   - **Average Grade Level:** Large, prominent number (e.g., "6.6")
   - **Total Words Analyzed:** Count across all documents
   - **Unique Words:** Count of unique vocabulary
   - **Last Analyzed:** Date of most recent analysis

3. Grade Distribution Visualization:
   - **Option A:** Pie chart showing percentage per grade level
   - **Option B:** Horizontal bar chart showing distribution
   - Uses Recharts or similar library
   - Interactive (hover shows exact percentages)
   - Color-coded by grade level

4. Subject-specific breakdown (optional enhancement):
   - Toggle or filter to see vocabulary by subject
   - "ELA vocabulary: 7.2, Math vocabulary: 6.1"

5. Empty state:
   - If no analyses exist, show: "Upload and analyze a document to see vocabulary profile"

6. Loading state:
   - Shows skeleton/spinner while fetching analysis data
   - Shows "Analyzing..." if analysis in progress

7. Responsive design:
   - Chart scales appropriately on mobile/tablet

8. Testing:
   - Profile displays after document analyzed
   - Metrics accurate based on database values
   - Chart renders correctly with real data
   - Empty state shows when no analyses
   - Profile updates when new document analyzed

### Story 3.6: Add Analysis Status and Progress Indicators

As an **educator**,
I want **to see the status of document analysis (pending, in progress, complete)**,
so that **I know when vocabulary profiles are ready to view**.

#### Acceptance Criteria:

1. Document status tracking:
   - Add `analysis_status` column to `documents` table (enum: 'pending', 'analyzing', 'completed', 'failed')
   - Default: 'pending' on upload
   - Update to 'analyzing' when analysis starts
   - Update to 'completed' when analysis finishes
   - Update to 'failed' if analysis errors

2. Status display in documents library:
   - Badge/chip showing status next to each document
   - Color-coded:
     - Pending: Gray
     - Analyzing: Blue with spinner
     - Completed: Green with checkmark
     - Failed: Red with error icon
   - Uses shadcn/ui Badge component

3. Real-time updates (optional):
   - Frontend polls for status updates during analysis
   - Or uses Supabase real-time subscriptions
   - Status badge updates without page refresh

4. Retry mechanism for failed analyses:
   - "Retry Analysis" button for failed documents
   - Calls analyze endpoint again

5. Analysis queue visibility (optional):
   - If multiple documents uploaded at once, show queue position
   - "Analyzing 2 of 5 documents..."

6. Testing:
   - Status updates correctly through analysis lifecycle
   - Badge displays correct status and styling
   - Failed analysis can be retried
   - Multiple document analyses handled correctly

---

## Epic 4: Personalized Recommendations

**Expanded Goal:**
Implement the AI-powered recommendation engine that analyzes student vocabulary gaps, identifies contexts where students use lower-grade words, and generates personalized, subject-aware vocabulary suggestions using LangChain and OpenAI. This epic delivers the core product value proposition - automated, intelligent vocabulary recommendations tailored to each student's current proficiency level and writing contexts.

### Story 4.1: Set Up LangChain and OpenAI Integration

As a **developer**,
I want **LangChain configured with OpenAI API for AI-powered text analysis**,
so that **we can generate intelligent vocabulary recommendations**.

#### Acceptance Criteria:

1. Dependencies installed in FastAPI:
   - `langchain`
   - `openai`
   - `langchain-openai` (OpenAI integration for LangChain)

2. Environment variables configured:
   - `OPENAI_API_KEY` or `OPENROUTER_API_KEY`
   - `LLM_MODEL` (e.g., "gpt-4o-mini" or "gpt-4")
   - `LLM_TEMPERATURE` (default: 0.3 for consistency)

3. LangChain client initialized (`services/ai_service.py`):
   - `ChatOpenAI` configured with API key and model
   - Switchable to OpenRouter by changing base URL:
     ```python
     llm = ChatOpenAI(
         model=settings.LLM_MODEL,
         openai_api_key=settings.OPENAI_API_KEY,
         openai_api_base=settings.OPENAI_API_BASE  # For OpenRouter
     )
     ```

4. Basic test function:
   - `test_llm_connection()` - Sends simple prompt, verifies response
   - Health check endpoint: `GET /api/health/ai` - Tests LLM connectivity

5. Error handling:
   - API key validation
   - Rate limit handling (retry logic)
   - Timeout configuration (30 seconds)
   - Fallback behavior if API unavailable

6. Cost tracking (basic):
   - Log token usage for each API call
   - Estimate costs based on model pricing

7. Testing:
   - Can initialize LangChain client
   - Can send prompt and receive response
   - Health check endpoint works
   - Invalid API key returns meaningful error
   - Timeout works correctly

### Story 4.2: Build Recommendation Generation Service

As a **developer**,
I want **a service that uses LangChain to analyze student text and generate vocabulary recommendations**,
so that **we can suggest appropriate higher-grade words in context**.

#### Acceptance Criteria:

1. Recommendation service created (`services/recommendation_service.py`):
   - Function `generate_recommendations(student_id, document_id, count=10, subject=None)`

2. Recommendation generation logic:
   - Fetch student's vocabulary profile (average grade level)
   - Fetch document text and subject
   - Fetch student's current vocabulary (words they already use)
   - Fetch available higher-grade words from `grade_words` (target: student's grade + 1 or 2)
   - Filter by subject if specified

3. LangChain prompt template:
   ```python
   prompt = ChatPromptTemplate.from_template("""
   You are a vocabulary education expert for middle school students.

   Student's current vocabulary level: Grade {current_grade}
   Document subject: {subject}
   Student's text excerpt:
   {text_excerpt}

   Available higher-grade words for this subject:
   {available_words}

   Task: Identify {count} places where the student uses simple or repetitive words/phrases
   and could use more sophisticated vocabulary from the available words list.

   For each recommendation, provide:
   1. current_usage: The exact phrase or word the student currently uses
   2. recommended_word: A more sophisticated word from the available list
   3. recommended_grade: The grade level of the recommended word
   4. context: A brief explanation of where this would fit
   5. example_sentence: An example sentence using the recommended word in the student's context
   6. rationale: Why this word is appropriate for this student

   Output as JSON array.
   """)
   ```

4. LangChain chain creation:
   - Create `LLMChain` with prompt and ChatOpenAI
   - Parse JSON response
   - Validate response format

5. Output format:
   ```python
   [
     {
       "current_usage": "very good",
       "recommended_word": "excellent",
       "recommended_grade": 7,
       "context": "describing quality of work",
       "example_sentence": "The scientist's research was excellent.",
       "rationale": "Natural step up from 'very good', commonly used in academic writing"
     },
     ...
   ]
   ```

6. Filtering and validation:
   - Ensure recommended words exist in `grade_words` table
   - Ensure recommended grade > student's current grade
   - Deduplicate recommendations (no repeated words)
   - Limit to requested count

7. Error handling:
   - Handle LLM API failures gracefully
   - Handle malformed JSON responses
   - Return partial results if possible
   - Log errors with context

8. Testing:
   - Unit tests with mock LLM responses
   - Integration tests with real API calls (rate-limited)
   - Verify JSON parsing
   - Verify recommendations are contextually appropriate (manual review)
   - Test with different subjects
   - Test with different grade levels

### Story 4.3: Create Recommendations API Endpoint

As an **educator**,
I want **the system to automatically generate vocabulary recommendations after analyzing a document**,
so that **I can see personalized word suggestions for each student**.

#### Acceptance Criteria:

1. Endpoint created:
   - `POST /api/students/{student_id}/recommendations/generate`
   - Parameters:
     - `document_id` (optional - if provided, base recommendations on this document)
     - `count` (optional, default: 10)
     - `subject` (optional - filter to specific subject)
   - Requires authentication (educator owns student)

2. Endpoint logic:
   - Call `generate_recommendations()` service
   - Store recommendations in `recommendations` table:
     - student_id, word, recommended_grade_level, subject, context, student_current_usage, example_sentence, rationale, recommended_at, status ('pending')
   - Return recommendations as JSON

3. Database schema for recommendations table:
   - Ensure all fields from Story 4.2 output format are captured
   - Index on student_id for fast queries
   - Index on subject for filtering

4. Automatic trigger option:
   - After document analysis completes (Epic 3), automatically generate recommendations
   - Or manual trigger only (educator clicks "Generate Recommendations" button)

5. Deduplication logic:
   - Don't recommend words the student already uses proficiently
   - Don't recommend same word multiple times
   - Check for existing pending recommendations and don't duplicate

6. Response format:
   ```json
   {
     "recommendations": [
       {
         "id": "uuid",
         "word": "excellent",
         "grade_level": 7,
         "subject": "ELA",
         "current_usage": "very good",
         "context": "describing quality",
         "example_sentence": "...",
         "rationale": "...",
         "status": "pending"
       }
     ],
     "count": 10,
     "student_current_grade": 6.5
   }
   ```

7. Rate limiting consideration:
   - LLM calls are expensive - consider limiting to N recommendations per day
   - Or batch process overnight for all students

8. Testing:
   - Can generate recommendations for student
   - Recommendations stored in database
   - Cannot generate for other educators' students
   - Recommendations appropriate for grade level (manual review)
   - Handles API failures gracefully
   - Respects count parameter
   - Filters by subject correctly

### Story 4.4: Display Recommendations on Student Detail Page

As an **educator**,
I want **to view personalized vocabulary recommendations for each student**,
so that **I can guide their vocabulary development with specific, actionable suggestions**.

#### Acceptance Criteria:

1. Recommendations section on student detail page updated:
   - Fetches recommendations from database for current student
   - Displays in table/card layout
   - Shows "Generate Recommendations" button if no recommendations exist

2. Recommendations display includes:
   - **Word:** The recommended vocabulary word (prominent)
   - **Grade Level:** Badge showing grade (e.g., "Grade 7")
   - **Subject:** Subject tag (color-coded)
   - **Current Usage:** What student currently says
   - **Example Sentence:** How to use the word
   - **Rationale:** Why this word is recommended (expandable/tooltip)
   - **Status:** Badge (pending/adopted/not used - for Epic 5)

3. Filtering controls:
   - **Subject filter:** Tabs or dropdown (All, ELA, Math, Science, Social Studies)
   - **Count selector:** Dropdown to choose how many to display (5, 10, 15, 20)
   - Filter persists in URL params or local state

4. Interactions:
   - Expandable rows for full rationale/context
   - "Generate More" button to create additional recommendations
   - Recommendations sorted by grade level (lowest to highest) or by subject

5. Empty state:
   - "No recommendations yet. Analyze a document and generate recommendations."
   - CTA button: "Generate Recommendations"

6. Loading state:
   - "Generating recommendations..." with spinner
   - Progress indicator if generation takes >5 seconds

7. Responsive design:
   - Desktop: Full table with all columns
   - Mobile: Stacked cards with key info

8. Testing:
   - Recommendations display after generation
   - Subject filter works correctly
   - Count selector changes display count
   - Can expand rows for full details
   - Empty state shows appropriately
   - "Generate More" creates additional recommendations

### Story 4.5: Implement Customizable Recommendation Settings

As an **educator**,
I want **to customize recommendation generation settings**,
so that **I can tailor suggestions to specific learning goals or focus areas**.

#### Acceptance Criteria:

1. Settings UI added to student detail page or recommendations section:
   - "Customize Recommendations" button opens modal/drawer
   - Settings form with options:
     - **Number of recommendations:** Slider or input (5-20)
     - **Target grade level:** Dropdown (student's grade + 1, +2, +3)
     - **Subject focus:** Multi-select (ELA, Math, Science, Social Studies, or All)
     - **Difficulty preference:** Radio buttons (Conservative: +1 grade, Moderate: +2, Challenging: +3)

2. Settings persistence:
   - Store preferences in database (per student or per educator)
   - Table: `recommendation_settings` (student_id or educator_id, settings JSONB)
   - Load settings when generating recommendations

3. Apply settings to generation:
   - Pass settings to `generate_recommendations()` service
   - Modify prompt based on preferences
   - Filter word lists based on target grade and subject

4. Default settings:
   - If no custom settings, use defaults:
     - Count: 10
     - Target grade: student's current + 1
     - Subjects: All
     - Difficulty: Moderate

5. Reset option:
   - "Reset to Defaults" button in settings modal

6. Testing:
   - Can customize settings via UI
   - Settings saved to database
   - Settings applied when generating recommendations
   - Recommendations match specified criteria (grade level, subject, count)
   - Reset to defaults works correctly

### Story 4.6: Add Bulk Recommendation Generation (Optional Enhancement)

As an **educator**,
I want **to generate recommendations for all my students at once**,
so that **I can efficiently prepare vocabulary guidance for my entire class**.

#### Acceptance Criteria:

1. Dashboard "Generate All Recommendations" button:
   - Positioned prominently on dashboard
   - Triggers batch generation for all students with analyzed documents

2. Batch generation logic:
   - Endpoint: `POST /api/educators/recommendations/generate-all`
   - Iterates through all educator's students
   - Generates recommendations for each (using default or saved settings)
   - Runs asynchronously (background job)

3. Background job implementation:
   - Use Celery, RQ, or similar task queue (optional complexity)
   - Or simple async processing in FastAPI
   - Stores job ID and progress

4. Progress tracking:
   - Frontend polls for progress: `GET /api/jobs/{job_id}`
   - Returns: `{status: 'running', progress: '5/20 students', completed: false}`
   - Shows progress bar in UI

5. Notification on completion:
   - Toast notification when all recommendations generated
   - Or email notification (optional)

6. Error handling:
   - If generation fails for some students, continue with others
   - Log errors, show summary of successes/failures

7. Testing:
   - Can trigger bulk generation
   - Progress tracked correctly
   - All students get recommendations
   - Partial failures handled gracefully
   - Large batches (50+ students) complete successfully

---

## Epic 5: Progress Tracking & Insights

**Expanded Goal:**
Enable historical vocabulary tracking, visualize student progress over time with interactive charts showing grade-level trends, detect and track adoption of recommended words in subsequent student writing, calculate recommendation effectiveness metrics, and generate AI-powered narrative insights to help educators understand patterns and make informed teaching decisions. This epic transforms raw data into actionable intelligence, demonstrating vocabulary growth and the impact of recommendations.

### Story 5.1: Implement Historical Vocabulary Tracking

As an **educator**,
I want **to see how each student's vocabulary level changes over time**,
so that **I can track their growth and identify trends**.

#### Acceptance Criteria:

1. Historical data storage:
   - Ensure `vocab_analyses` table retains all analyses (don't overwrite)
   - Each document gets its own analysis record
   - Add composite index on (student_id, analyzed_at) for time-series queries

2. Progress data endpoint:
   - `GET /api/students/{student_id}/progress`
   - Returns time-series data:
     ```json
     {
       "student_id": "uuid",
       "data_points": [
         {
           "date": "2025-11-01",
           "average_grade_level": 6.2,
           "document_id": "uuid",
           "document_title": "Essay 1",
           "unique_words": 120
         },
         {
           "date": "2025-11-08",
           "average_grade_level": 6.5,
           "document_id": "uuid",
           "document_title": "Essay 2",
           "unique_words": 145
         }
       ],
       "overall_trend": "improving",  # or "stable", "declining"
       "grade_level_change": +0.3
     }
     ```

3. Trend calculation:
   - Compare first analysis to latest analysis
   - Calculate: `latest_grade - first_grade`
   - Determine trend: improving (>0.2), stable (-0.2 to +0.2), declining (<-0.2)

4. Aggregation options:
   - By time period (weekly, monthly)
   - By subject (show progress in ELA vs. Math separately)

5. Minimum data requirement:
   - Require at least 2 analyses to show progress (otherwise show "Not enough data")

6. Testing:
   - Endpoint returns correct historical data
   - Trend calculation accurate
   - Handles students with 1 document (no trend yet)
   - Handles students with 20+ documents (pagination or limit)
   - Subject filtering works

### Story 5.2: Build Interactive Progress Visualization

As an **educator**,
I want **to see an interactive chart showing vocabulary progress over time**,
so that **I can quickly visualize student growth patterns**.

#### Acceptance Criteria:

1. Progress chart component created:
   - Uses Recharts library (LineChart)
   - X-axis: Date/time
   - Y-axis: Average grade level (6.0-12.0 scale)
   - Data points: Each document analysis
   - Line connecting points showing trend

2. Chart features:
   - **Hover/tooltip:** Shows exact grade level, date, document title
   - **Reference line:** Student's target grade level (their actual grade)
   - **Color coding:** Line color changes based on trend (green=improving, blue=stable, red=declining)
   - **Responsive:** Scales for mobile/tablet

3. Additional visualizations:
   - **Stacked area chart (optional):** Shows grade distribution over time
   - **Vocabulary growth:** Line showing unique word count over time

4. Subject toggle:
   - Dropdown to filter by subject
   - "All Subjects" shows combined data
   - Individual subjects show subject-specific progress

5. Integration on student detail page:
   - Progress section displays chart below recommendations
   - Auto-updates when new document analyzed

6. Empty state:
   - "Upload at least 2 documents to see progress over time"
   - Placeholder chart with sample data

7. Performance:
   - Chart renders smoothly with 50+ data points
   - Uses data downsampling if needed

8. Testing:
   - Chart displays with real data
   - Hover tooltips work correctly
   - Subject filter updates chart
   - Chart responsive on different screen sizes
   - Handles edge cases (1 data point, 100+ data points)

### Story 5.3: Implement Recommendation Adoption Tracking

As an **educator**,
I want **to see which recommended words students have started using in their writing**,
so that **I can measure the effectiveness of vocabulary recommendations**.

#### Acceptance Criteria:

1. Adoption detection logic:
   - When new document is analyzed (Epic 3), check for pending recommendations
   - Function `detect_word_adoption(student_id, document_id)`:
     - Fetch all pending recommendations for student
     - Fetch extracted words from new document analysis
     - Match recommended words to document words (lemmatized comparison)
     - If match found, mark recommendation as 'adopted'

2. Database updates:
   - Update `recommendations.status` from 'pending' to 'adopted'
   - Create record in `word_usage_tracking` table:
     - recommendation_id, document_id, used=true, detected_at (timestamp)

3. Adoption detection integration:
   - Automatically run after document analysis (Epic 3, Story 3.4)
   - Part of analysis pipeline workflow

4. Handling false positives:
   - Only mark as adopted if word appears 2+ times in document (configurable threshold)
   - Or requires word in meaningful context (LLM verification - optional complexity)

5. Retroactive adoption check:
   - If recommendations generated after documents uploaded, check past documents
   - Endpoint: `POST /api/students/{student_id}/check-adoption`

6. Testing:
   - Recommended word appearing in new document marked as adopted
   - Recommendation status updated correctly
   - Usage tracking record created
   - Works with lemmatized forms (recommend "analyze", student uses "analyzing")
   - Doesn't match unrelated words (false positives)

### Story 5.4: Display Adoption Metrics and Success Rate

As an **educator**,
I want **to see metrics on how many recommended words students are adopting**,
so that **I can understand the impact of vocabulary recommendations**.

#### Acceptance Criteria:

1. Adoption metrics calculated:
   - Function `calculate_adoption_rate(student_id)`:
     ```python
     {
       "total_recommendations": 30,
       "adopted": 12,
       "pending": 15,
       "not_used": 3,
       "adoption_rate": 0.40,  # 40%
       "average_time_to_adopt": "14 days"  # Optional
     }
     ```

2. Endpoint created:
   - `GET /api/students/{student_id}/adoption-metrics`
   - Returns metrics as JSON

3. Dashboard display:
   - Student card on dashboard shows adoption rate badge
   - "40% adopted" in green
   - Hover for breakdown

4. Student detail page display:
   - Adoption metrics section shows:
     - **Total recommendations:** 30
     - **Words adopted:** 12 (40%)
     - **Still learning:** 15 (50%)
     - **Not yet used:** 3 (10%)
   - Visual representation (progress bar or donut chart)

5. Recommendation list updates:
   - Status badge on each recommendation (pending/adopted/not used)
   - Adopted recommendations highlighted in green
   - Pending in gray
   - Not used after 30 days in yellow (needs reinforcement)

6. Filtering by status:
   - Filter recommendations by status on student detail page
   - "Show Adopted Words" to celebrate progress
   - "Show Pending Words" for focused practice

7. Testing:
   - Metrics calculated correctly
   - Dashboard shows accurate adoption rates
   - Recommendation status badges display correctly
   - Filters work on student detail page

### Story 5.5: Generate AI-Powered Insights and Recommendations

As an **educator**,
I want **AI-generated insights about each student's vocabulary development**,
so that **I can understand patterns and receive actionable teaching recommendations**.

#### Acceptance Criteria:

1. Insights generation service:
   - Function `generate_student_insights(student_id)` using LangChain
   - Fetches:
     - Vocabulary progress data (grade level trend)
     - Adoption metrics (success rate)
     - Subject-specific performance
     - Recent documents and analyses

2. LangChain prompt for insights:
   ```python
   prompt = ChatPromptTemplate.from_template("""
   You are an expert vocabulary education consultant.

   Student Data:
   - Started at grade level: {initial_grade}
   - Current grade level: {current_grade}
   - Actual grade: {student_grade}
   - Progress trend: {trend}
   - Recommendation adoption rate: {adoption_rate}
   - Subjects analyzed: {subjects}
   - Vocabulary strengths: {strengths}
   - Vocabulary gaps: {gaps}

   Generate 3-4 concise, actionable insights for the educator:
   1. Overall progress assessment
   2. Subject-specific observations (if applicable)
   3. Recommended focus areas
   4. Specific teaching strategies or interventions

   Keep each insight to 1-2 sentences. Be specific and actionable.
   Format as bullet points.
   """)
   ```

3. Insights endpoint:
   - `POST /api/students/{student_id}/insights/generate`
   - Stores generated insights in `student_insights` table:
     - student_id, insights (JSONB or text), generated_at
   - Returns insights as JSON

4. Insights display on student detail page:
   - "Insights" section added
   - Shows AI-generated bullet points
   - "Regenerate Insights" button
   - Last updated timestamp

5. Example insights output:
   ```
   - Strong progress in ELA vocabulary (+0.8 grade levels), but Math vocabulary
     remains below grade level. Consider using math-specific word practice.
   - High adoption rate (65%) indicates student is receptive to recommendations.
     Continue current approach.
   - Student excels with analytical words but struggles with descriptive adjectives.
     Focus next recommendations on descriptive vocabulary.
   - Consider introducing grade 8 words - student has mastered grade 7 vocabulary
     across multiple documents.
   ```

6. Caching and refresh:
   - Cache insights for 7 days
   - Auto-regenerate if significant new data (3+ new documents)
   - Manual regenerate button

7. Testing:
   - Can generate insights for student with sufficient data
   - Insights relevant and actionable (manual review)
   - Insights update when regenerated
   - Handles students with minimal data gracefully
   - LLM API failures handled gracefully

### Story 5.6: Add Comparative Analytics (Class-Level View)

As an **educator**,
I want **to see aggregate statistics across all my students**,
so that **I can identify which students need more support and track overall class progress**.

#### Acceptance Criteria:

1. Class-level analytics endpoint:
   - `GET /api/educators/analytics`
   - Returns aggregate metrics:
     ```json
     {
       "total_students": 25,
       "average_grade_level": 6.8,
       "grade_distribution": {
         "below_grade": 8,    # Students below their actual grade
         "at_grade": 12,      # Within 0.5 of grade level
         "above_grade": 5     # Above their grade
       },
       "average_adoption_rate": 0.52,
       "total_documents_analyzed": 150,
       "top_performers": [...],  # Students with highest growth
       "needs_support": [...]     # Students declining or stagnant
     }
     ```

2. Dashboard analytics section:
   - Header card on dashboard showing:
     - Total students
     - Class average vocabulary grade
     - Average adoption rate
     - Quick stats

3. Student comparison view:
   - Table showing all students with key metrics:
     - Name, Current grade level, Progress trend, Adoption rate, Last activity
   - Sortable columns
   - Color-coded indicators (green=above grade, yellow=at grade, red=below)

4. Filtering and sorting:
   - Filter by: Above/At/Below grade level, Subject performance
   - Sort by: Name, Grade level, Progress, Adoption rate

5. Identify outliers:
   - Highlight students needing attention (red flag icon)
   - Highlight high performers (star icon)

6. Export functionality (optional):
   - "Export to CSV" button
   - Downloads class analytics for record-keeping

7. Testing:
   - Analytics calculated correctly across all students
   - Comparison view displays accurately
   - Sorting and filtering work
   - Identifies outliers correctly
   - Export produces valid CSV (if implemented)

---

## Out of Scope for MVP

To clarify project boundaries, the following items are explicitly **OUT of scope** for the MVP release:

- Real-time speech-to-text transcription (assumes educators provide pre-processed text documents)
- Direct integration with Learning Management Systems (Google Classroom, Canvas, Schoology)
- Student-facing interface (MVP is educator-only dashboard)
- Mobile native applications (iOS/Android apps - web responsive only)
- Gamification features for students (badges, leaderboards, points)
- Multi-language support (English vocabulary only in MVP)
- Automated email/push notifications (manual review workflow only)
- Bulk data import from existing systems (manual student/document entry)
- Advanced analytics (cohort analysis, longitudinal studies - basic progress tracking only)
- Custom vocabulary word list creation by educators (uses pre-compiled Common Core lists only)

---

## Checklist Results Report

### Executive Summary

- **Overall PRD Completeness:** 95%
- **MVP Scope Appropriateness:** Just Right
- **Readiness for Architecture Phase:** Ready
- **Most Critical Gaps:**
  - Word list compilation methodology needs more specificity (addressed as developer responsibility)
  - Out-of-scope items now explicitly listed above
  - Stakeholder approval process not defined

### Category Analysis

| Category                         | Status  | Critical Issues |
| -------------------------------- | ------- | --------------- |
| 1. Problem Definition & Context  | PASS    | None - clear problem statement, target users, success metrics |
| 2. MVP Scope Definition          | PASS    | Well-bounded MVP, clear feature prioritization through epic structure |
| 3. User Experience Requirements  | PASS    | Comprehensive UI/UX goals, accessibility WCAG AA, platform targets clear |
| 4. Functional Requirements       | PASS    | 26 FRs covering all core functionality, specific and testable |
| 5. Non-Functional Requirements   | PASS    | 26 NFRs with specific performance targets, security, scalability |
| 6. Epic & Story Structure        | PASS    | 5 epics, 31 stories, properly sequenced with clear acceptance criteria |
| 7. Technical Guidance            | PASS    | Detailed tech stack, Supabase + FastAPI architecture, clear constraints |
| 8. Cross-Functional Requirements | PASS    | Database schema, S3 integration, LangChain setup all documented |
| 9. Clarity & Communication       | PASS    | Well-structured, consistent terminology, clear rationale throughout |

### Final Decision

✅ **READY FOR ARCHITECT**

The PRD and epics are comprehensive, properly structured, and ready for architectural design.

**Strengths:**
- Clear problem definition with specific target users
- Well-scoped MVP with logical epic progression
- Comprehensive functional and non-functional requirements
- Detailed story breakdown with testable acceptance criteria
- Technical stack decisions made and justified
- Security and privacy considerations well-addressed

**Next Steps:**
1. Hand off to architect for detailed architecture design
2. Architect creates system architecture diagram, database schema, API specifications
3. Begin Epic 1 implementation after architecture review

---

## Next Steps

### UX Expert Prompt

```
I need you to create detailed UX/UI designs for the Personalized Vocabulary Recommendation Engine based on the attached PRD (docs/prd.md).

Focus on:

1. **Educator Dashboard** - Design a clean, data-driven interface showing:
   - Student cards with key metrics (current vocab grade level, progress trend, document count)
   - Quick stats header (total students, class average, adoption rate)
   - Clear CTAs for adding students and generating recommendations

2. **Student Detail Page** - The most complex view with sections for:
   - Document upload (drag-and-drop, subject selection)
   - Vocabulary profile visualization (grade distribution chart, average grade level)
   - Recommendations table (filterable by subject, expandable rows for context)
   - Progress over time (line chart showing vocabulary growth)
   - AI-generated insights

3. **Login/Auth Flow** - Simple, professional login with Supabase Auth (email/password + Google OAuth)

4. **Key Interactions**:
   - Document upload → analysis status → results display
   - Recommendation filtering by subject
   - Progress chart interactivity (hover for details)

**Design Principles:**
- Professional educational tool aesthetic (not playful - think Google Classroom, Canvas)
- Data visualization as primary visual interest
- Progressive disclosure (summary → drill-down)
- WCAG AA accessibility compliance
- Use shadcn/ui components for consistency

**Deliverables:**
- Wireframes for 3-4 core screens
- Component specifications (cards, tables, charts, forms)
- Interaction patterns (hover states, loading states, error states)
- Responsive layout guidance (desktop, tablet, mobile)

**Tech Context:**
- Next.js with Tailwind CSS and shadcn/ui
- Recharts for data visualization
- Design should align with existing Next.js + shadcn setup
```

### Architect Prompt

```
I need you to create a comprehensive technical architecture for the Personalized Vocabulary Recommendation Engine based on the attached PRD (docs/prd.md).

The system uses a hybrid architecture:
- **Frontend:** Next.js 14+ (TypeScript, Tailwind, shadcn/ui) deployed to Vercel
- **Database + Auth:** Supabase (PostgreSQL with Row-Level Security, built-in auth)
- **Backend:** FastAPI (Python 3.11+) with LangChain for AI processing, deployed to AWS Lambda or ECS
- **Storage:** AWS S3 for document files
- **AI:** OpenAI API via LangChain (switchable to OpenRouter)

**Your tasks:**

1. **System Architecture Diagram**
   - Component relationships (Next.js ↔ Supabase ↔ FastAPI ↔ OpenAI/S3)
   - Data flows for key workflows (document upload → analysis → recommendations)
   - Authentication flow (Supabase JWT verification in FastAPI)

2. **Database Schema Design**
   - Detailed schema with all tables, columns, types, constraints
   - Row-Level Security (RLS) policies for data isolation
   - Indexes for performance (time-series queries, foreign keys)
   - Migration strategy (Alembic or Supabase migrations)

3. **API Specifications**
   - RESTful endpoints for FastAPI (vocabulary analysis, recommendations, insights)
   - Request/response schemas (Pydantic models)
   - Error handling patterns
   - Authentication middleware design

4. **S3 Integration Pattern**
   - Pre-signed URL generation strategy (client-side upload vs. server-side proxy)
   - File naming convention and folder structure
   - Security (bucket policies, encryption)

5. **LangChain Architecture**
   - Prompt templates for recommendation generation and insights
   - Chain composition (LLMChain, SequentialChain if needed)
   - Model configuration (OpenAI vs. OpenRouter switching)
   - Cost optimization strategies

6. **Testing Strategy**
   - Unit testing approach (pytest for backend, Jest for frontend)
   - Integration testing (Supabase test DB, mocked LLM responses)
   - E2E testing critical flows

7. **Deployment Architecture**
   - AWS Lambda vs. ECS decision (recommend one with rationale)
   - CI/CD pipeline (GitHub Actions)
   - Environment management (dev, staging, prod)
   - Monitoring and logging strategy

**Critical Design Decisions Needed:**
- Supabase RLS policy patterns for multi-tenant isolation
- FastAPI JWT verification implementation
- Recommendation de-duplication logic
- Progress tracking query optimization (time-series data)
- Error handling and retry logic for LLM API calls
- Cold start mitigation for AWS Lambda (if chosen)

**Deliverables:**
- Architecture document (docs/architecture.md)
- System architecture diagram
- Database schema with RLS policies
- API specification (OpenAPI/Swagger)
- Deployment guide
- Development environment setup guide

Reference the PRD's technical assumptions section for constraints and requirements.
```

---

**End of PRD**
