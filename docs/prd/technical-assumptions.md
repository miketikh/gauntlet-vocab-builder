# Technical Assumptions

## Repository Structure: Monorepo

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

## Service Architecture

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

## Testing Requirements

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

## Additional Technical Assumptions and Requests

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
