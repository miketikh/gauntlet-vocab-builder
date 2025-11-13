# Epic 5: Progress Tracking & Insights

**Expanded Goal:**
Enable historical vocabulary tracking, visualize student progress over time with interactive charts showing grade-level trends, detect and track adoption of recommended words in subsequent student writing, calculate recommendation effectiveness metrics, and generate AI-powered narrative insights to help educators understand patterns and make informed teaching decisions. This epic transforms raw data into actionable intelligence, demonstrating vocabulary growth and the impact of recommendations.

## Story 5.1: Implement Historical Vocabulary Tracking

As an **educator**,
I want **to see how each student's vocabulary level changes over time**,
so that **I can track their growth and identify trends**.

### Acceptance Criteria:

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

## Story 5.2: Build Interactive Progress Visualization

As an **educator**,
I want **to see an interactive chart showing vocabulary progress over time**,
so that **I can quickly visualize student growth patterns**.

### Acceptance Criteria:

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

## Story 5.3: Implement Recommendation Adoption Tracking

As an **educator**,
I want **to see which recommended words students have started using in their writing**,
so that **I can measure the effectiveness of vocabulary recommendations**.

### Acceptance Criteria:

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

## Story 5.4: Display Adoption Metrics and Success Rate

As an **educator**,
I want **to see metrics on how many recommended words students are adopting**,
so that **I can understand the impact of vocabulary recommendations**.

### Acceptance Criteria:

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

## Story 5.5: Generate AI-Powered Insights and Recommendations

As an **educator**,
I want **AI-generated insights about each student's vocabulary development**,
so that **I can understand patterns and receive actionable teaching recommendations**.

### Acceptance Criteria:

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

## Story 5.6: Add Comparative Analytics (Class-Level View)

As an **educator**,
I want **to see aggregate statistics across all my students**,
so that **I can identify which students need more support and track overall class progress**.

### Acceptance Criteria:

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
