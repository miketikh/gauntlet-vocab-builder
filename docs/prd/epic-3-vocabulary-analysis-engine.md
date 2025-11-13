# Epic 3: Vocabulary Analysis Engine

**Expanded Goal:**
Build the core NLP and vocabulary analysis pipeline that processes uploaded documents, extracts and lemmatizes vocabulary, maps words to grade-level standards using compiled Common Core word lists, calculates vocabulary profiles showing grade-level distribution, and displays these insights to educators. This epic delivers the first automated analysis capability, transforming raw text into actionable vocabulary intelligence.

## Story 3.1: Compile and Import Grade-Level Word Lists

As a **developer**,
I want **grade-level word lists (6th-12th grade) compiled from Common Core standards and loaded into the database**,
so that **the analysis engine can map student vocabulary to grade levels**.

### Acceptance Criteria:

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

## Story 3.2: Build Text Processing and Word Extraction Service

As a **developer**,
I want **a FastAPI service that extracts and lemmatizes unique words from document text**,
so that **student vocabulary can be accurately analyzed regardless of word forms**.

### Acceptance Criteria:

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

## Story 3.3: Implement Grade-Level Mapping Logic

As a **developer**,
I want **to map extracted student vocabulary to grade levels using the word lists**,
so that **we can determine what grade level each student is performing at**.

### Acceptance Criteria:

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

## Story 3.4: Create Document Analysis Endpoint

As an **educator**,
I want **the system to automatically analyze uploaded documents and calculate vocabulary profiles**,
so that **I can see each student's current vocabulary level without manual effort**.

### Acceptance Criteria:

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

## Story 3.5: Display Vocabulary Profile on Student Detail Page

As an **educator**,
I want **to see a visual representation of each student's vocabulary grade level**,
so that **I can quickly understand their current proficiency and track their progress**.

### Acceptance Criteria:

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

## Story 3.6: Add Analysis Status and Progress Indicators

As an **educator**,
I want **to see the status of document analysis (pending, in progress, complete)**,
so that **I know when vocabulary profiles are ready to view**.

### Acceptance Criteria:

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
