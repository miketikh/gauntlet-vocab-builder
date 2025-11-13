# Vocabulary Grade-Level Assignment - Methodology Analysis

**Date:** 2025-11-12
**Issue:** Current word lists use frequency-based assignment (backwards methodology)

---

## The Problem with Current Approach

### What Was Done (INCORRECT)
The `generate_grade_levels.py` script assigned words by **frequency rank** from NGSL:
- Rank 1-300 (most common) → Grade 6
- Rank 1401-1500 (less common) → Grade 11

### Why This is Wrong
**Frequency ≠ Difficulty**

High-frequency words are usually the SIMPLEST:
- Rank 1-300: "the", "a", "is", "and", "you", "have", "go"
- Rank 1400+: "gift", "gold", "guest", "actual", "afraid"

Result: Basic everyday words are assigned to high school grades!

### Example Comparison

| Current (Wrong) | Should Be (Right) |
|----------------|-------------------|
| **Grade 11:** gift, gold, guest, actual, afraid, cup | **Grade 6:** abundant, authentic, dedicate, perceive, prominent |
| **Grade 6:** the, a, of, to, and, in, is | **Grade 11:** acquiesce, ambiguous, paradigm, scrutinize |

---

## Correct Methodology: What Makes a Word "Grade-Appropriate"?

### 1. **Cognitive/Semantic Complexity**
- **Abstract vs Concrete:** "dog" (concrete, easy) vs "integrity" (abstract, hard)
- **Precision/Nuance:** "big" vs "substantial" vs "immense"
- **Polysemy:** Single meaning vs multiple meanings

### 2. **Age of Acquisition (AoA)**
- When children typically learn the word
- Research databases available (Kuperman 2012 - 44k words)
- Strong predictor of processing difficulty

### 3. **Academic Register**
- **Tier 1:** Basic everyday words (cat, run, blue) - SKIP
- **Tier 2:** High-utility academic words (analyze, evaluate, demonstrate) - TARGET
- **Tier 3:** Domain-specific (photosynthesis, hypotenuse) - INCLUDE

### 4. **Morphological Complexity**
- Syllable count
- Affixes (prefixes/suffixes)
- Root word complexity
- **Grade 6:** 1-2 syllables, simple roots
- **Grade 11:** 3+ syllables, Latin/Greek roots

### 5. **Curriculum Alignment**
- What grades actually teach
- Standardized test vocabulary (SAT prep starts ~10th grade)
- Subject-specific vocabulary introduction

---

## Available Data Sources (Better Than What We Used)

### ✅ **1. Vocabulary.com Grade Lists**
- **Quality:** Curated by education experts
- **Coverage:** 125+ words per grade (6-12)
- **Methodology:** Student data + commonly taught texts
- **Example (Grade 6):** abundant, authentic, dedicate, efficient, forfeit, inevitable, perceive, prominent, rigorous, unanimous

**Sample Grade 6 words:** abundant, authentic, beneficial, bewilder, boycott, complexity, consecutive, contemplate, controversy, cultivate, dedicate, deteriorate, devastate, efficient, elaborate, evaluate, excel, exempt, fatigue, forfeit, hypothesis, immature, inevitable, intention, interpret, intervene, intricate, loathe, makeshift, meager, mischievous, momentum, mournful, nurture, optimistic, overwhelm, perceive, persevere, persistent, precision, prediction, prejudice, prominent, pulverize, reassure, rebellion, reckless, refrain, reluctant, reminisce, represent, resolve, rigorous, sabotage, scarce, serene, solitude, stealthy, subsequent, sufficient, symbol, sympathetic, tentative, treacherous, trudge, unanimous, unique, unruly, urgent, verify, waver

### ✅ **2. GreatSchools Academic Vocabulary Lists**
- **Quality:** Grade-level curated lists (1-12)
- **Coverage:** 50-100 words per grade
- **Alignment:** Common Core aligned
- **Links:** Has individual pages per grade

### ✅ **3. Age of Acquisition (AoA) Database - Kuperman 2012**
- **Quality:** Research-backed, empirical
- **Coverage:** 44,000 English words
- **Methodology:** Crowdsourced ratings (Amazon Mechanical Turk)
- **Data:** Mean age learned, standard deviation, part of speech
- **Link:** https://norare.clld.org/contributions/Kuperman-2012-AoA

### ✅ **4. Academic Word List (AWL) - We Have This!**
- **Quality:** Research-backed (Coxhead 2000)
- **Coverage:** 570 word families
- **Sublists:** Already ranked 1-10 by frequency in academic texts
- **Current Status:** We only used 120/570 words
- **Better Use:** Map sublists to grades based on academic progression

### 📄 **5. Common Core Vocabulary Standards**
- **Status:** We downloaded the PDF but didn't parse it
- **Location:** `language-docs/raw/common-core/ELA_Standards_Complete.pdf`
- **Value:** Official grade-level expectations

---

## Recommended New Approach

### Option A: Use Curated Sources (FASTEST, BEST QUALITY)
1. **Scrape Vocabulary.com lists** (125 words × 7 grades = 875 words)
2. **Scrape GreatSchools lists** (50-100 words × 7 grades = 350-700 words)
3. **Combine + deduplicate** → ~800-1000 high-quality words
4. **Enrich with definitions** using Claude API

**Pros:**
- Expert-curated, already grade-appropriate
- Used by actual teachers/students
- No algorithm errors
- Can implement today

**Cons:**
- Smaller dataset (~1000 words total)
- May have licensing/usage restrictions (check ToS)

### Option B: Build Algorithmic Classifier (RESEARCH PROJECT)
Use Age of Acquisition + other features to train a model:

**Features:**
- Age of Acquisition (Kuperman 2012)
- Syllable count
- Character length
- Part of speech
- Academic Word List membership
- Abstractness ratings (if available)
- Morphological complexity (prefix/suffix count)

**Training Data:**
- Vocabulary.com lists as ground truth
- GreatSchools lists
- Common Core vocabulary (once parsed)

**Pros:**
- Can scale to unlimited words
- Reproducible
- Can explain why words are assigned to grades

**Cons:**
- Requires ML/data science work
- Need training data first (back to Option A)
- Risk of misclassification

### Option C: Hybrid (RECOMMENDED)
1. **Start with curated sources** (Option A) for POC
2. **Extract Common Core vocabulary** from PDF
3. **Enrich with AWL** (map sublists to grades intelligently)
4. **Target:** 150-200 words per grade (×7 = 1000-1400 words)
5. **Later:** Build classifier (Option B) for expansion

---

## Comparison: Current vs Proper Vocabulary

### Current Grade 11 (WRONG - using frequency rank)
acquire, affair, afford, anybody, army, **cup**, **dear**, **gift**, **gold**, **guest**, bedroom, belong, bomb, border, branch, climb, complain, confidence, council, danger, dangerous, etc.

**Problem:** These are elementary-level words! "Cup", "dear", "gift", "gold" are K-2 vocabulary.

### Proper Grade 11 (from Vocabulary.com)
acquiesce, ambiguous, belligerent, benevolent, brevity, candor, collaborate, colloquial, complacent, comprehensive, condescending, contempt, deficient, diligent, eloquent, exemplary, feasible, formidable, hindsight, hypothetical, impartial, imperative, indifferent, inevitable, infamous, innovation, integrity, intuition, jurisdiction, lethargic, meticulous, negligent, obscure, obsolete, paradox, perception, preconceived, preclude, presumptuous, prioritize, profound, redundant, resilient, saturate, scrutinize, simultaneously, superficial, susceptible, transaction, unilateral, unprecedented, volatile

**Characteristics:** Abstract, 3+ syllables, academic register, SAT-prep level

---

## Implementation Plan

### Immediate Action (This Week)
1. **Scrape Vocabulary.com** grade-level lists (6-12)
2. **Scrape GreatSchools** individual grade pages
3. **Parse Common Core PDF** for explicit vocabulary
4. **Combine sources** with prioritization:
   - Vocab.com > GreatSchools > Common Core (order of authority)
5. **Generate new JSON files** with proper words

### Next Steps (After POC)
1. **Enrich definitions** using Claude API
2. **Add AWL words** intelligently (not just by frequency)
3. **Validate sample** (spot check 20 words per grade)
4. **Import to database**

### Future Enhancement
1. **Build AoA-based classifier** for expansion
2. **Add 3000+ more words** using the classifier
3. **Continuous validation** with teacher feedback

---

## Conclusion

**The fundamental error:** Using word frequency (how COMMON) instead of complexity (how HARD).

**The fix:** Use expert-curated grade-level lists from educational sources.

**Timeline:** Can have proper vocabulary lists in 1-2 hours of scraping work.

**Quality improvement:** Night and day difference - from nonsensical to pedagogically sound.
