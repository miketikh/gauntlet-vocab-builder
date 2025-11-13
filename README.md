# Vocab Builder

**Personalized Vocabulary Recommendation Engine for Middle School Students**

An AI-powered platform that analyzes student writing and conversation transcripts to provide personalized, grade-appropriate vocabulary recommendations for middle school educators.

## Project Structure

This is a monorepo containing both frontend and backend applications:

```
vocab-builder/
├── web/              # Next.js frontend (deployed to Vercel)
├── api/              # FastAPI backend (deployed to AWS)
├── docs/             # Documentation and PRD
│   ├── prd/         # Product Requirements Document (sharded)
│   └── ...
├── .bmad-core/       # BMAD agent configuration
└── README.md         # This file
```

## Quick Start

### Frontend (Next.js)

```bash
cd web
pnpm install
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

See [`web/README.md`](web/README.md) for more details (if available).

### Backend (FastAPI)

```bash
cd api
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Configure your environment variables
uvicorn main:app --reload --port 8000
```

API available at [http://localhost:8000](http://localhost:8000)
API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

See [`api/README.md`](api/README.md) for more details.

## Tech Stack

### Frontend
- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS + shadcn/ui
- **Auth:** Supabase Auth
- **Deployment:** Vercel

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.11+
- **Database:** Supabase (PostgreSQL)
- **Storage:** AWS S3
- **AI/NLP:** LangChain + OpenAI
- **Deployment:** AWS Lambda/ECS

## Documentation

- **[PRD](docs/prd/)** - Product Requirements Document (sharded by epic)
- **[Project Requirements](docs/project_requirements_and_overview.md)** - Original requirements from Flourish Schools
- **[Project Notes](docs/project_thoughts_and_ideas.md)** - Initial brainstorming and ideas

## Development Workflow

### Running Both Services

**Terminal 1 (Frontend):**
```bash
cd web && pnpm dev
```

**Terminal 2 (Backend):**
```bash
cd api && source venv/bin/activate && uvicorn main:app --reload
```

### Environment Variables

Both `/web` and `/api` require environment configuration:

- **Frontend:** Copy `web/.env.local.example` to `web/.env.local`
- **Backend:** Copy `api/.env.example` to `api/.env`

See respective directories for required variables.

## Contributing

This project follows an epic-based development approach. See the [PRD](docs/prd/) for the full product specification and epic breakdown.

### Epic Overview

1. **Epic 1:** Foundation & Authentication
2. **Epic 2:** Student Management & Document Upload
3. **Epic 3:** Vocabulary Analysis Engine
4. **Epic 4:** Personalized Recommendations
5. **Epic 5:** Progress Tracking & Insights

## License

Private project for Flourish Schools.

## Contact

For questions or issues, please contact the development team.
