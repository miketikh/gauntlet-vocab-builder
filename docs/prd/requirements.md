# Requirements

## Functional Requirements

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

## Non-Functional Requirements

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
