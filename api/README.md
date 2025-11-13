# Vocab Builder API

FastAPI backend for the Personalized Vocabulary Recommendation Engine using SQLModel ORM.

## Architecture

- **Framework:** FastAPI (Python 3.9+)
- **ORM:** SQLModel (SQLAlchemy + Pydantic)
- **Database:** Supabase PostgreSQL
- **Migrations:** Alembic
- **Type Safety:** End-to-end types via OpenAPI → TypeScript codegen

## Setup

### 1. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your configuration:
# - DATABASE_URL: PostgreSQL connection string (use Supabase pooler)
# - SUPABASE_URL: Your Supabase project URL
# - SUPABASE_SERVICE_ROLE_KEY: For auth and storage operations
# - AWS credentials: For S3 document storage
```

**Important:** Use the Supabase **Session mode (pooler)** connection string:
```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-us-east-2.pooler.supabase.com:6543/postgres
```

### 4. Run database migrations

```bash
# Generate initial migration (if not already done)
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

See `alembic/README.md` for detailed migration documentation.

### 5. Run development server

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **OpenAPI JSON:** http://localhost:8000/openapi.json
- **Docs:** http://localhost:8000/docs (Swagger UI)
- **ReDoc:** http://localhost:8000/redoc

## Project Structure

```
api/
├── main.py              # FastAPI app entry point
├── models/              # SQLModel database models + Pydantic schemas
│   ├── database.py      # Table models, enums, API schemas
│   └── __init__.py
├── services/            # Business logic
│   └── database.py      # Database session, queries, helpers
├── routers/             # API route handlers (future)
├── alembic/             # Database migrations
│   ├── versions/        # Migration files
│   ├── env.py           # Alembic configuration
│   └── README.md        # Migration guide
├── alembic.ini          # Alembic config file
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Python project config
└── .env                 # Environment variables (not committed)
```

## Database Management with Alembic

### Quick Commands

```bash
# Create a new migration (autogenerate from models)
alembic revision --autogenerate -m "Description"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current migration status
alembic current

# View migration history
alembic history
```

### Workflow

1. **Modify models** in `models/database.py`
2. **Generate migration:** `alembic revision --autogenerate -m "Add new field"`
3. **Review migration** in `alembic/versions/`
4. **Apply migration:** `alembic upgrade head`
5. **Commit both** model changes and migration file

**For detailed instructions, see `alembic/README.md`**

## SQLModel Database Models

Models are defined in `models/database.py`:

- **Educator:** Teacher/educator accounts
- **Student:** Student profiles (linked to educators)
- **Document:** Uploaded student documents (stored in S3)
- **GradeWord:** Grade-appropriate vocabulary word lists

Each model includes:
- Table model (for database)
- Public response model (for API responses)
- Create model (for POST requests)
- Update model (for PATCH requests)

Example:
```python
from models.database import Student, StudentCreate, StudentPublic
from services.database import get_session
from sqlmodel import Session, select

# Create student
student = Student(
    educator_id=1,
    name="John Doe",
    grade_level=8
)
session.add(student)
session.commit()

# Query students
statement = select(Student).where(Student.educator_id == 1)
students = session.exec(statement).all()
```

## Type Safety with Frontend

The frontend generates TypeScript types from the OpenAPI schema:

### Backend (FastAPI)
1. Define SQLModel models with Pydantic validation
2. Use `response_model` in route decorators
3. FastAPI auto-generates OpenAPI JSON at `/openapi.json`

### Frontend (Next.js)
1. Start API: `cd api && uvicorn main:app --reload`
2. Generate types: `cd web && npm run generate:api-types`
3. Import: `import { apiClient } from '@/lib/api-client'`
4. Use type-safe API calls

See `web/lib/api-client.ts` for usage examples.

## Text Processing and Vocabulary Analysis

### Overview

The vocabulary analysis system provides NLP-powered text processing to extract, analyze, and categorize vocabulary from student documents. It uses spaCy for linguistic processing and maps words to grade-level standards.

### Setup NLP Libraries

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Download spaCy language model:**
```bash
python -m spacy download en_core_web_sm
```

### Components

#### 1. Text Extraction (`services/text_extraction.py`)

Extracts text from various file formats:
- **PDF files** - Using pypdf library
- **DOCX files** - Using python-docx library
- **TXT files** - With automatic encoding detection

Features:
- Automatic file type detection
- Graceful error handling for corrupt files
- Text cleaning and normalization
- Support for multiple text encodings

Example usage:
```python
from services.text_extraction import extract_text_from_file

# Extract from file bytes
with open("document.pdf", "rb") as f:
    content = f.read()

text = extract_text_from_file(content, file_type="pdf")
```

#### 2. Word Processing (`services/word_processing.py`)

NLP processing using spaCy:
- **Tokenization** - Split text into words
- **Lemmatization** - Convert to base form (running → run)
- **POS tagging** - Part-of-speech analysis
- **Stop word filtering** - Remove common words (the, and, is)
- **Word frequency** - Count word occurrences

Features:
- Cached spaCy model (loaded once, reused)
- Batch processing for efficiency
- Configurable filtering options
- Word normalization for lookup

Example usage:
```python
from services.word_processing import (
    extract_words_from_text,
    calculate_word_frequency,
    get_word_statistics
)

# Extract unique words
words = extract_words_from_text(text)

# Get word frequencies
freq = calculate_word_frequency(text)
# Returns: {"word": 5, "analyze": 3, ...}

# Get statistics
stats = get_word_statistics(text)
# Returns: {"total_words": 100, "unique_words": 75, ...}
```

#### 3. Vocabulary Analysis (`services/vocabulary_analysis.py`)

Grade-level vocabulary analysis:
- Maps words to grade levels (6-12)
- Categorizes words relative to student's grade
- Calculates vocabulary profiles
- Generates recommendations

Features:
- Batch database queries for efficiency
- Category classification (below/at/above/unknown)
- Grade distribution calculation
- Challenging word identification

Example usage:
```python
from services.vocabulary_analysis import analyze_vocabulary
from services.database import get_session

session = next(get_session())

profile = analyze_vocabulary(
    text=document_text,
    student_grade_level=8,
    session=session
)

print(f"Average grade level: {profile.statistics.average_grade_level}")
print(f"Challenging words: {len(profile.challenging_words)}")
```

##### Grade-Level Mapping Algorithm

The vocabulary analysis engine uses a sophisticated algorithm to map words to grade levels and categorize them relative to each student:

**1. Word Extraction and Normalization**
- Text is processed through spaCy NLP pipeline
- Words are tokenized and lemmatized (e.g., "running" → "run")
- Stop words, punctuation, and short words (<3 chars) are filtered
- Word frequencies are calculated

**2. Grade-Level Lookup**
- All unique words are queried from `grade_words` table in a single batch query
- For words appearing at multiple grade levels, the **lowest grade** is used (most accessible interpretation)
- For words in multiple subjects, **ELA** is preferred when available
- Unknown words (not in database) are tracked separately

**3. Word Categorization Relative to Student Grade**

Each word is categorized based on its grade level compared to the student's grade level:

| Category | Rule | Example (Grade 8 student) |
|----------|------|---------------------------|
| **BELOW** | Word is 2+ grades below student | Grade 6 or lower words |
| **AT_LEVEL** | Word is within 1 grade of student | Grade 7, 8, or 9 words |
| **ABOVE** | Word is 2+ grades above student | Grade 10+ words |
| **UNKNOWN** | Word not found in database | Specialized vocabulary, proper nouns |

**Categorization Logic:**
```python
grade_diff = word_grade - student_grade

if grade_diff <= -2:    # 2+ below
    category = BELOW
elif -1 <= grade_diff <= 1:  # Within 1 grade
    category = AT_LEVEL
else:  # grade_diff >= 2  # 2+ above
    category = ABOVE
```

**4. Statistical Calculations**

- **Average Grade Level**: Mean of all analyzed words' grade levels (excludes unknown words)
- **Grade Distribution**: Percentage of words at each grade level (6-12)
- **Category Counts**: Number of words in each category (below/at/above/unknown)
- **Unknown Percentage**: Ratio of unknown words to total unique words

**5. Challenging Words Identification**

Words categorized as ABOVE (2+ grades above student) are:
- Sorted by grade level (highest first)
- Then sorted by frequency (most common first)
- Limited to top 20 for display
- Include definitions and examples when available

**6. Performance Optimizations**

- **Batch Queries**: All words looked up in single SQL query using `WHERE word IN (...)`
- **spaCy Model Caching**: NLP model loaded once and reused across requests
- **Efficient Data Structures**: Uses Counter and dict for O(1) lookups
- **Target Performance**: 5,000-word document analyzed in <10 seconds

**7. Example Analysis Output**

For a Grade 8 student analyzing a history passage:

```python
{
    "student_grade_level": 8,
    "statistics": {
        "total_words": 523,
        "unique_words": 245,
        "analyzed_words": 220,
        "unknown_words": 25,
        "unknown_percentage": 0.102,
        "average_grade_level": 8.2,
        "below_grade_count": 80,   # Grade 6 and below
        "at_grade_count": 120,      # Grade 7, 8, 9
        "above_grade_count": 20     # Grade 10+
    },
    "grade_distribution": {
        "grade_6": 0.15,
        "grade_7": 0.20,
        "grade_8": 0.30,
        "grade_9": 0.18,
        "grade_10": 0.10,
        "grade_11": 0.05,
        "grade_12": 0.02
    },
    "challenging_words": [
        {
            "word": "sovereignty",
            "grade_level": 11,
            "frequency": 3,
            "definition": "supreme power or authority"
        }
    ]
}
```

### Analysis Models

Pydantic models in `models/analysis.py`:

- **WordAnalysisResult** - Analysis for individual word
- **VocabularyProfile** - Complete document analysis
- **VocabularyStatistics** - Statistical summary
- **GradeDistribution** - Word distribution across grades
- **WordCategory** - Enum (below/at/above/unknown)

### Testing

Run the test script to verify functionality:

```bash
# Activate virtual environment
source venv/bin/activate

# Run test script
python scripts/test_text_processing.py
```

The test script validates:
- Text extraction from various formats
- Word tokenization and frequency analysis
- Vocabulary grade-level mapping
- Complete analysis pipeline

### Performance Considerations

- **spaCy model caching** - Model loaded once and reused
- **Batch database queries** - All words looked up in single query
- **Target performance** - 5,000-word document in <10 seconds
- **Memory limits** - Consider chunking for very large documents

### Error Handling

The system handles:
- Unsupported file types → `UnsupportedFileTypeError`
- Corrupt files → `TextExtractionError`
- Empty documents → Validation error
- Encoding issues → Automatic fallback
- Missing spaCy model → Clear installation instructions

### Integration with API

Services are ready for Story 3.4 (Document Analysis Endpoint):
- All functions accept proper parameters
- Type hints throughout for IDE support
- Proper error responses
- Async-ready design

## LangChain and OpenAI Integration

### Overview

The vocabulary recommendation system uses LangChain with OpenAI's GPT models to generate personalized, AI-powered vocabulary recommendations. The system analyzes student writing and suggests appropriate higher-grade vocabulary words.

### Setup

1. **Install AI libraries:**
```bash
pip install -r requirements.txt
```

The following packages are included:
- `langchain>=0.1.0` - AI orchestration framework
- `langchain-openai>=0.0.2` - OpenAI integration for LangChain
- `langchain-core>=0.1.0` - Core LangChain components
- `openai>=1.10.0` - OpenAI Python client

2. **Configure API key:**

Add your OpenAI API key to `.env`:
```bash
OPENAI_API_KEY=sk-proj-...
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.3
```

**Supported Models:**
- `gpt-4o-mini` (recommended) - Cost-effective, fast responses
- `gpt-4` - More capable but expensive
- `gpt-4-turbo` - Balance of speed and capability

**Configuration Options:**
- `LLM_MODEL` - Model to use (default: gpt-4o-mini)
- `LLM_TEMPERATURE` - Creativity vs consistency (0.0-1.0, default: 0.3)
- `LLM_TIMEOUT` - Request timeout in seconds (default: 30)
- `LLM_MAX_RETRIES` - Max retry attempts (default: 3)

### Components

#### 1. LLM Service (`services/llm.py`)

The LLM service provides a singleton pattern for accessing the ChatOpenAI instance with automatic configuration from environment variables.

**Key Features:**
- Singleton pattern for efficient model reuse
- Automatic environment variable loading
- Comprehensive error handling
- Token usage tracking
- Cost estimation

**Usage Example:**
```python
from services.llm import get_llm, test_llm_connection

# Get configured LLM instance
llm = get_llm()

# Test connection
result = await test_llm_connection()
if result["success"]:
    print(f"Connected! Using {result['model']}")
else:
    print(f"Error: {result['error']}")
```

**Error Handling:**
The service handles common errors gracefully:
- **Authentication Error** - Invalid API key
- **Rate Limit Error** - Too many requests (automatic retry with exponential backoff)
- **Timeout Error** - Request took too long
- **API Error** - General OpenAI API issues

#### 2. Prompt Templates (`prompts/recommendations.py`)

Structured prompt templates for generating vocabulary recommendations:

**Available Templates:**
- `RECOMMENDATION_PROMPT` - Generate vocabulary recommendations
- `VOCABULARY_GAP_ANALYSIS_PROMPT` - Analyze text for improvement opportunities
- `SUBJECT_SPECIFIC_PROMPT` - Subject-focused recommendations
- `SIMPLE_TEST_PROMPT` - Connection testing

**Example Usage:**
```python
from prompts.recommendations import RECOMMENDATION_PROMPT, format_word_list

# Format data for prompt
available_words = format_word_list([
    {"word": "analyze", "grade": 7, "definition": "examine in detail"},
    {"word": "evaluate", "grade": 8, "definition": "assess value or quality"}
])

# Format prompt with student data
messages = RECOMMENDATION_PROMPT.format_messages(
    student_grade=8,
    avg_grade_level=7.2,
    subject="Science",
    challenging_words="...",
    available_words=available_words,
    count=5
)

# Invoke LLM
response = await llm.ainvoke(messages)
```

#### 3. Recommendation Models (`models/recommendations.py`)

Pydantic models for type-safe recommendation handling:

**Key Models:**
- `VocabularyRecommendation` - Single word recommendation
- `RecommendationRequest` - Request parameters
- `RecommendationSet` - Collection of recommendations
- `RecommendationResponse` - API response format
- `VocabularyGapAnalysis` - Text improvement opportunities

**Example:**
```python
from models.recommendations import VocabularyRecommendation

recommendation = VocabularyRecommendation(
    word="analyze",
    recommended_grade=7,
    current_usage="look at",
    definition="to examine something carefully and in detail",
    example_sentence="Scientists analyze data to find patterns.",
    rationale="Essential vocabulary for scientific inquiry."
)
```

#### 4. Token Tracking and Cost Estimation

Monitor token usage and estimate costs:

```python
from services.llm import token_tracker, estimate_cost

# Track usage
token_tracker.add_usage(prompt_tokens=150, completion_tokens=75)

# Get statistics
stats = token_tracker.get_stats("gpt-4o-mini")
print(f"Total cost: ${stats['estimated_cost_usd']:.6f}")

# Estimate individual request cost
cost = estimate_cost(
    prompt_tokens=150,
    completion_tokens=75,
    model="gpt-4o-mini"
)
```

**Cost Reference (as of November 2024):**
- **gpt-4o-mini**: $0.150/1M input tokens, $0.600/1M output tokens
- **gpt-4**: $30.00/1M input tokens, $60.00/1M output tokens
- **gpt-4-turbo**: $10.00/1M input tokens, $30.00/1M output tokens

### Testing

Run the comprehensive LLM test suite:

```bash
# Activate virtual environment
source venv/bin/activate

# Run test script
python3 scripts/test_llm.py
```

**Test Coverage:**
1. Basic OpenAI connection test
2. Simple prompt/response test
3. Recommendation prompt template test
4. Error handling validation
5. Token tracking and cost estimation

**Sample Output:**
```
======================================================================
  Test 1: Basic OpenAI Connection
======================================================================

✓ OpenAI connection successful!
ℹ Model: gpt-4o-mini
ℹ Response: Connection successful!
ℹ Tokens used: 25

======================================================================
  Test 3: Recommendation Prompt Test
======================================================================

✓ Recommendation prompt test successful!
ℹ Response time: 2.34 seconds

  Recommendation 1:
    Word: analyze (Grade 7)
    Replaces: look at
    Definition: to examine something carefully and in detail
    Example: Scientists analyze data to find patterns in experiments.
    Rationale: Essential academic vocabulary for scientific inquiry.

ℹ Token usage:
  Prompt tokens: 245
  Completion tokens: 128
  Total tokens: 373
  Estimated cost: $0.000113
```

### Prompt Engineering Approach

Our prompts are designed with educational best practices:

**System Role:**
- Expert vocabulary educator
- Middle school specialization (grades 6-8)
- Focus on personalized, appropriate recommendations

**Input Context:**
- Student grade level and current vocabulary proficiency
- Subject matter (ELA, Math, Science, Social Studies)
- Words student currently struggles with
- Available higher-grade vocabulary words

**Output Requirements:**
- JSON format for easy parsing
- Clear definitions and examples
- Context-aware rationale
- Grade-level appropriateness validation

**Quality Controls:**
- Only recommend from provided word list
- Ensure 1+ grade level progression
- Subject-appropriate vocabulary
- Varied word types (nouns, verbs, adjectives)

### Alternative Provider Support (OpenRouter)

To use OpenRouter instead of OpenAI:

1. **Get OpenRouter API key:** https://openrouter.ai/

2. **Update `.env`:**
```bash
OPENAI_API_KEY=sk-or-v1-...  # OpenRouter key
OPENAI_API_BASE=https://openrouter.ai/api/v1
LLM_MODEL=anthropic/claude-3-5-sonnet  # Or any OpenRouter model
```

3. **No code changes needed** - The service automatically uses the base URL

**Supported OpenRouter Models:**
- `anthropic/claude-3-5-sonnet`
- `google/gemini-pro`
- `meta-llama/llama-3-70b-instruct`
- See OpenRouter docs for full model list

### Cost Monitoring

Monitor LLM usage and costs:

```python
from services.llm import token_tracker

# Get current session statistics
stats = token_tracker.get_stats("gpt-4o-mini")

print(f"Requests: {stats['total_requests']}")
print(f"Total tokens: {stats['total_tokens']}")
print(f"Estimated cost: ${stats['estimated_cost_usd']:.6f}")

# Reset tracker (e.g., at start of day)
token_tracker.reset()
```

**Best Practices:**
- Track token usage per recommendation generation
- Set budget alerts in OpenAI dashboard
- Use `gpt-4o-mini` for cost efficiency
- Batch recommendations when possible
- Monitor costs daily during development

### Performance Considerations

**Response Times (typical):**
- Simple connection test: <1 second
- Single recommendation: 2-3 seconds
- 10 recommendations: 3-5 seconds

**Optimization Tips:**
- Use singleton pattern (already implemented)
- Request multiple recommendations at once
- Set appropriate timeout values
- Implement caching for repeated queries
- Consider batch processing for large datasets

### Troubleshooting

**"OPENAI_API_KEY not set"**
- Add key to `.env` file
- Verify `.env` is in `/api` directory
- Check key format starts with `sk-proj-`

**"Authentication failed"**
- Verify API key is valid and active
- Check OpenAI account has credits
- Ensure no extra whitespace in key

**"Rate limit exceeded"**
- Wait before retrying (exponential backoff implemented)
- Upgrade OpenAI plan for higher limits
- Consider using OpenRouter for load balancing

**"Request timeout"**
- Increase `LLM_TIMEOUT` in `.env`
- Check network connectivity
- Reduce recommendation count per request

**"Invalid JSON response"**
- LLM sometimes adds markdown formatting
- Parser handles code blocks automatically
- Contact support if issues persist

### Next Steps

This setup enables:
- **Story 4.2**: Recommendation generation service
- **Story 4.3**: API endpoints for recommendations
- **Story 4.4**: Frontend recommendation display

The LLM service is ready for integration with vocabulary analysis and student data.

## Data Import Scripts

### Import Grade-Level Vocabulary Data

Import pre-compiled vocabulary word lists for grades 6-12 into the `grade_words` table:

```bash
# Activate virtual environment first
source venv/bin/activate

# Import all grades (6-12)
python scripts/import_vocab_data.py

# Import specific grade only
python scripts/import_vocab_data.py --grade 8

# Preview import without inserting data (dry-run)
python scripts/import_vocab_data.py --dry-run

# Clear table before import
python scripts/import_vocab_data.py --clear
```

**Data Source:** `/language-docs/final/grade-{6-12}.json`

**Features:**
- Validates and transforms JSON data to match GradeWord model
- Handles duplicates (skips existing word+grade+subject combinations)
- Normalizes words to lowercase
- Maps subjects (defaults to "ELA")
- Progress reporting during import
- Database verification after import

**Import Statistics:**
- Grade 6: 182 words
- Grade 7: 222 words
- Grade 8: 213 words
- Grade 9: 203 words
- Grade 10: 208 words
- Grade 11: 208 words
- Grade 12: 209 words
- **Total: 1,445 words**

The script can be re-run without duplicating data. Use `--clear` to reset the table if needed.

## Development

### Running tests

```bash
pytest
```

### Code formatting

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy .
```

### Adding new endpoints

1. Define route in `main.py` or create router in `routers/`
2. Use SQLModel models for request/response
3. Add `session: Session = Depends(get_session)` for database access
4. FastAPI will auto-generate OpenAPI schema
5. Frontend can regenerate types to get new endpoints

Example:
```python
@app.get("/api/students/{student_id}", response_model=StudentPublic)
async def get_student(
    student_id: int,
    session: Session = Depends(get_session)
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
```

## Environment Variables

Required environment variables (see `.env.example`):

- `DATABASE_URL`: PostgreSQL connection string (Supabase pooler)
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: For admin operations
- `AWS_S3_BUCKET`: S3 bucket name for document storage
- `AWS_REGION`: AWS region
- `AWS_ACCESS_KEY_ID`: AWS credentials
- `AWS_SECRET_ACCESS_KEY`: AWS credentials

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

## Troubleshooting

### "Can't connect to database"
- Check DATABASE_URL is correct
- Ensure you're using the **pooler** connection string (port 6543)
- Verify Supabase project is running

### "Table does not exist"
- Run migrations: `alembic upgrade head`
- Check migration status: `alembic current`

### "OpenAPI types out of sync"
- Regenerate frontend types: `cd web && npm run generate:api-types`
- Ensure FastAPI is running on port 8000

### "Import errors for models"
- Check you're in virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## Migration from Drizzle

This project was refactored from Drizzle (Node.js) to SQLModel (Python):
- ❌ Removed: `node_modules/`, `package.json`, `drizzle/`, `db/`
- ✅ Added: SQLModel models, Alembic migrations
- ✅ Benefit: Pure Python stack, better type integration with FastAPI
- ✅ Frontend: OpenAPI → TypeScript type generation

See git history for details on the migration.
