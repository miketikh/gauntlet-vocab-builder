# Grade-Level Vocabulary Data for Personalized Vocabulary Recommendation Engine

## Overview

This directory contains grade-level vocabulary lists (grades 6-12) compiled from authoritative academic sources for use in the Personalized Vocabulary Recommendation Engine.

**Generated:** 2025-11-12
**Total Words:** 1,620 (distributed across 7 grade levels)
**Sources:** New General Service List (NGSL) 1.2 + Academic Word List (AWL)

## Directory Structure

```
language-docs/
├── raw/                          # Original source data
│   ├── ngsl-complete.json       # 2,809 NGSL words with frequency data
│   ├── awl-partial.json         # 120 AWL words (sublists 1-2)
│   ├── NGSL_12_stats.csv        # Original NGSL CSV
│   └── common-core/             # Common Core ELA Standards PDFs
│       └── ELA_Standards_Complete.pdf
├── processed/                    # Intermediate processing files
├── final/                        # Grade-level vocabulary files (READY TO USE)
│   ├── grade-6.json             # 300 words
│   ├── grade-7.json             # 300 words
│   ├── grade-8.json             # 360 words
│   ├── grade-9.json             # 360 words
│   ├── grade-10.json            # 200 words
│   ├── grade-11.json            # 100 words
│   └── grade-12.json            # 0 words
├── scripts/                      # Processing scripts
│   ├── parse_ngsl.py            # Parse NGSL CSV to JSON
│   ├── parse_awl_complete.py    # Parse AWL data
│   ├── generate_grade_levels.py # Assign words to grades
│   └── enrich_vocabulary.py     # Add definitions/examples
└── README.md                     # This file
```

## Data Sources

### 1. New General Service List (NGSL) 1.2
- **Source:** Browne, C., Culligan, B., and Phillips, J.
- **Description:** 2,809 high-frequency words for general English
- **Coverage:** 92% of most general English texts
- **License:** Creative Commons Attribution-ShareAlike 4.0
- **Website:** https://www.newgeneralservicelist.com/
- **Used:** Top 1,500 words (by frequency rank)

### 2. Academic Word List (AWL)
- **Source:** Victoria University of Wellington - Averil Coxhead
- **Description:** 570 word families frequently appearing in academic texts
- **Coverage:** ~10% of academic texts
- **Website:** https://www.wgtn.ac.nz/lals/resources/academicwordlist
- **Used:** 120 words (sublists 1-2)

### 3. Common Core State Standards (Future Enhancement)
- **Source:** CCSSO (Council of Chief State School Officers)
- **Status:** Downloaded, not yet processed
- **Purpose:** Validate vocabulary appropriateness per grade

## File Format

Each grade-level file (`grade-6.json` through `grade-12.json`) follows this structure:

```json
{
  "grade": 6,
  "words": [
    {
      "word": "analyze",
      "definition": "examine something carefully to understand it",
      "example": "Students will analyze the author's argument in the essay.",
      "subjects": ["ELA", "Science"],
      "frequency_rank": 450,
      "sources": ["NGSL", "AWL-sublist-1"]
    }
  ],
  "metadata": {
    "total_words": 300,
    "last_updated": "2025-11-12",
    "sources": ["NGSL-1.2", "AWL"]
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `word` | string | The vocabulary word (lemmatized) |
| `definition` | string | Student-friendly definition (5-15 words) |
| `example` | string | Grade-appropriate example sentence |
| `subjects` | array | Applicable subjects: `["ELA", "Math", "Science", "Social Studies", "General"]` |
| `frequency_rank` | number | NGSL rank (lower = more frequent). Only for NGSL words. |
| `sources` | array | Origin: `["NGSL"]` or `["AWL-sublist-X"]` or both |

## Grade-Level Distribution

| Grade | Word Count | Primary Source | Characteristics |
|-------|------------|----------------|-----------------|
| 6 | 300 | NGSL (rank 1-300) | High-frequency, foundational words |
| 7 | 300 | NGSL (rank 301-600) | Common everyday vocabulary |
| 8 | 360 | NGSL (rank 601-900) + AWL sublist 1 | Academic vocabulary introduction |
| 9 | 360 | NGSL (rank 901-1200) + AWL sublist 2 | Intermediate academic words |
| 10 | 200 | NGSL (rank 1201-1400) + AWL sublist 2 | Advanced vocabulary |
| 11 | 100 | NGSL (rank 1401-1500) | College-prep vocabulary |
| 12 | 0 | - | (Reserved for future expansion) |

## Methodology

### Grade-Level Assignment

Words were assigned to grades based on:

1. **Frequency Analysis** (NGSL)
   - Rank 1-300 → Grade 6
   - Rank 301-600 → Grade 7
   - Rank 601-900 → Grade 8
   - Etc.

2. **Academic Complexity** (AWL)
   - Sublist 1 (most frequent) → Grades 7-8
   - Sublist 2 → Grades 9-10
   - Higher sublists → Grades 11-12

3. **Cognitive Demand**
   - Syllable count
   - Abstract vs. concrete concepts
   - Typical curriculum placement

### Subject Classification

Words were tagged with subject area(s) based on typical domain usage:
- **Math:** equation, calculate, ratio, graph, data
- **Science:** hypothesis, experiment, molecule, energy
- **Social Studies:** government, economy, culture, region
- **ELA:** Most academic and general vocabulary
- **General:** Cross-curricular words

## Usage in Application

These files are ready for import into the application database as per **Epic 3, Story 3.1**:

```python
# Example import script
import json

for grade in range(6, 13):
    with open(f'language-docs/final/grade-{grade}.json') as f:
        data = json.load(f)

    for word_entry in data['words']:
        # Insert into grade_words table
        insert_word(
            word=word_entry['word'],
            grade_level=grade,
            subject=word_entry['subjects'],
            definition=word_entry['definition'],
            example_sentence=word_entry['example'],
            frequency_rank=word_entry.get('frequency_rank')
        )
```

## Current Status

✅ **Complete:**
- Folder structure created
- NGSL data downloaded and parsed (2,809 words)
- AWL data scraped and parsed (120 words from sublists 1-2)
- Common Core PDF downloaded
- Grade-level assignment algorithm implemented
- 7 grade-level JSON files generated
- Subject classification applied
- Data structure matches PRD requirements

⚠️ **Partial/Placeholder:**
- **Definitions:** Most are placeholders. Sample enrichments provided for ~7 words.
- **Example Sentences:** Most are placeholders.
- **AWL Coverage:** Only 120/570 words (sublists 1-2). Full AWL data was scraped but not fully parsed.

🔮 **Future Enhancements:**
1. **AI Enrichment:** Use Claude API or similar to generate all definitions and examples
2. **Full AWL:** Parse remaining 450 AWL words (sublists 3-10)
3. **Common Core Extraction:** Extract explicit vocabulary from PDF
4. **Validation:** Cross-reference with actual curriculum standards
5. **Expansion:** Add synonyms, antonyms, word forms
6. **Quality Check:** Manual review of grade appropriateness

## Scripts

### `parse_ngsl.py`
Converts NGSL CSV to structured JSON.

```bash
cd language-docs/scripts
python3 parse_ngsl.py
```

### `generate_grade_levels.py`
Assigns words to grades and generates final JSON files.

```bash
cd language-docs/scripts
python3 generate_grade_levels.py
```

### `enrich_vocabulary.py`
Fills in definitions and examples (currently uses placeholders).

```bash
cd language-docs/scripts
python3 enrich_vocabulary.py
```

## Next Steps for Production

1. **Enrich Definitions & Examples:**
   - Integrate Claude API or dictionary API
   - Batch process all 1,620 words
   - Generate age-appropriate definitions and examples

2. **Complete AWL Parsing:**
   - Extract all 570 AWL words from scraped data
   - Re-run grade assignment

3. **Database Import:**
   - Create Supabase import script
   - Populate `grade_words` table
   - Add indexes for performance

4. **Validation:**
   - Sample 50 words per grade
   - Verify appropriateness
   - Adjust algorithm if needed

## Citations

Please cite the original sources when using this data:

**NGSL:**
Browne, C., Culligan, B., & Phillips, J. (2013). New General Service List. Retrieved from https://www.newgeneralservicelist.com/

**AWL:**
Coxhead, A. (2000). A New Academic Word List. TESOL Quarterly, 34(2), 213-238.

**License:** This compiled dataset is provided for educational purposes. Original sources maintain their respective licenses (NGSL: CC BY-SA 4.0, AWL: Educational use).

---

**Questions or Issues?** Contact the development team or refer to `/docs/prd/epic-3-vocabulary-analysis-engine.md`
