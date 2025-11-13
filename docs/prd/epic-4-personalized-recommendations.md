# Epic 4: Personalized Recommendations

**Expanded Goal:**
Implement the AI-powered recommendation engine that analyzes student vocabulary gaps, identifies contexts where students use lower-grade words, and generates personalized, subject-aware vocabulary suggestions using LangChain and OpenAI. This epic delivers the core product value proposition - automated, intelligent vocabulary recommendations tailored to each student's current proficiency level and writing contexts.

## Story 4.1: Set Up LangChain and OpenAI Integration

As a **developer**,
I want **LangChain configured with OpenAI API for AI-powered text analysis**,
so that **we can generate intelligent vocabulary recommendations**.

### Acceptance Criteria:

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

## Story 4.2: Build Recommendation Generation Service

As a **developer**,
I want **a service that uses LangChain to analyze student text and generate vocabulary recommendations**,
so that **we can suggest appropriate higher-grade words in context**.

### Acceptance Criteria:

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

## Story 4.3: Create Recommendations API Endpoint

As an **educator**,
I want **the system to automatically generate vocabulary recommendations after analyzing a document**,
so that **I can see personalized word suggestions for each student**.

### Acceptance Criteria:

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

## Story 4.4: Display Recommendations on Student Detail Page

As an **educator**,
I want **to view personalized vocabulary recommendations for each student**,
so that **I can guide their vocabulary development with specific, actionable suggestions**.

### Acceptance Criteria:

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

## Story 4.5: Implement Customizable Recommendation Settings

As an **educator**,
I want **to customize recommendation generation settings**,
so that **I can tailor suggestions to specific learning goals or focus areas**.

### Acceptance Criteria:

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

## Story 4.6: Add Bulk Recommendation Generation (Optional Enhancement)

As an **educator**,
I want **to generate recommendations for all my students at once**,
so that **I can efficiently prepare vocabulary guidance for my entire class**.

### Acceptance Criteria:

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
