# Next Steps

## UX Expert Prompt

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

## Architect Prompt

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
