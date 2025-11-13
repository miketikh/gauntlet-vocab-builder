# Project notes

Stories
- educator - receive list of words tailored to each students proficiency level to efficiently enhance their language skills
- student - be challenged with new vocabulary words that I can realistically learn and use effectively, so that I can improve my language proficiency

Reqs
- receive text input, build profile of current vocab
    - what kind of input? Should we generate examples of essays, conversation transcripts, etc?
- Ai identify gaps in vocabulary and suggest words to learn based on level
- Dynamic list of recommended words for educators to review

- Should have dashboard to review recommendations and track progress
- Ability to integrate with existing platforms (probably skip)

- Gamified vocab challenges
  - spaced repetition with pgoress tracking? Anki integration? Or quizzlet?
- Customizable recommendation settings for educators

- data and privacy compliance

- technical
  - prefer python + aws, but likely flexible. Frontend can do nextjs, python backend for AI functionality?

- assumed data
    - converstaion transcripts and writing samples
      - will have to generate these

## Ideas

Word difficulty:
Approach 1: Word Frequency + Semantic Similarity (My Top Pick for POC)
Core idea: Combine word frequency rankings with semantic relationships

Use word frequency databases like COCA (Corpus of Contemporary American English) - words ranked by how common they are
Analyze student's vocabulary to find their "frequency tier" (are they using top 5k words? top 10k?)
When they use simple/common words, find semantically similar but less frequent alternatives
Example: Student uses "very good" (high frequency) → suggest "excellent" (medium freq) → "exemplary" (lower freq)

Why this works: Frequency is a proxy for difficulty - rarer words tend to be more sophisticated. Plus you're building on words they already understand (semantic similarity).
Tools:

Word embeddings (OpenAI API has embeddings, or use sentence-transformers)
COCA frequency lists or WordNet
Could even use Claude API to find sophisticated synonyms at specific difficulty levels

Approach 2: Grade-Level Word Lists + Contextual Gaps
Core idea: Map their vocabulary to grade levels and scaffold up

Use existing grade-level word lists (Common Core, Lexile, Academic Word List)
Profile student: "They're using 70% grade 6 words, 25% grade 7, 5% grade 8"
Identify gaps: find grade 7-8 words that fit contexts where they're using grade 6 words
Prioritize words that would be useful across multiple contexts they write about

Resources:

Academic Word List (AWL) - 570 word families common in academic texts
Common Core vocabulary standards by grade
Lexile word frequency/grade level mappings

Approach 3: "Replacement Patterns" Analysis
Core idea: Find where they use multiple words where one sophisticated word would work

Analyze their writing for patterns like:

"very good" → "excellent"
"a lot of" → "numerous" / "abundant"
"said loudly" → "exclaimed"


This is the most immediately useful for them since it shows clear application

Implementation:

Use LLM (Claude) to analyze their text and identify these opportunities
Build a personalized list of "words to replace your current phrases"



