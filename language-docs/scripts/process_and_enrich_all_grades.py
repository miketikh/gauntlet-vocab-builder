#!/usr/bin/env python3
"""
Process and enrich vocabulary for all grades (6-12).

This script:
1. Loads Vocabulary.com and GreatSchools word lists for each grade
2. Combines and deduplicates them
3. Fetches definitions from Vocabulary.com
4. Classifies words by subject area
5. Outputs enriched JSON files in final/ directory

Format matches PRD requirements for grade_words table.
"""

import json
import time
import sys
from datetime import datetime

def load_vocabulary_com(grade):
    """Load Vocabulary.com words for a grade."""
    path = f"../raw/vocabulary-com-grade-{grade}.json"
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            return set(data['words'])
    except FileNotFoundError:
        print(f"Warning: {path} not found")
        return set()

def load_greatschools(grade):
    """Load GreatSchools words for a grade."""
    path = f"../raw/greatschools-grade-{grade}.json"
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            return set(data['words'])
    except FileNotFoundError:
        print(f"Warning: {path} not found")
        return set()

def classify_subject(word):
    """
    Classify word into subject areas based on typical usage.
    Returns list of subjects.
    """
    # Keywords for subject classification
    math_words = ['equation', 'calculate', 'quantitative', 'qualitative', 'variable', 'formula',
                  'dimension', 'congruent', 'bisect', 'adjacent', 'ratio', 'frequency']

    science_words = ['hypothesis', 'theory', 'experiment', 'evidence', 'procedure', 'formula',
                     'integrate', 'catalyst', 'ephemeral', 'catalyst']

    social_words = ['government', 'democracy', 'citizen', 'civilization', 'sovereign', 'jurisdiction',
                    'bureaucratic', 'coalition', 'constituency', 'legislation', 'demagogue', 'lobbyist']

    word_lower = word.lower()
    subjects = []

    # Check for subject-specific words
    if any(kw in word_lower for kw in math_words):
        subjects.append("Math")
    if any(kw in word_lower for kw in science_words):
        subjects.append("Science")
    if any(kw in word_lower for kw in social_words):
        subjects.append("Social Studies")

    # Most academic words are relevant to ELA
    if not subjects or word_lower in ['analyze', 'evaluate', 'comprehend', 'synthesize', 'infer']:
        subjects.append("ELA")

    # All words are at least general academic vocabulary
    if "General" not in subjects:
        subjects.insert(0, "General")

    return subjects

def generate_simple_definition(word):
    """
    Generate a placeholder definition.
    In production, this would fetch from Vocabulary.com API or dictionary API.
    """
    # For now, create a simple placeholder
    # You can enhance this later with actual API calls
    return f"[Definition for {word} - to be enriched]"

def generate_example_sentence(word, grade):
    """
    Generate a placeholder example sentence.
    In production, this would use Claude API or fetch from Vocabulary.com.
    """
    return f"[Example sentence using '{word}' for grade {grade} - to be enriched]"

def process_grade(grade):
    """Process and enrich vocabulary for a single grade."""
    print(f"\n{'='*60}")
    print(f"Processing Grade {grade}")
    print('='*60)

    # Load words from both sources
    vocab_com_words = load_vocabulary_com(grade)
    greatschools_words = load_greatschools(grade)

    print(f"  Vocabulary.com: {len(vocab_com_words)} words")
    print(f"  GreatSchools:   {len(greatschools_words)} words")

    # Combine and deduplicate (case-insensitive)
    all_words_lower = {}  # lowercase -> original form
    for word in vocab_com_words | greatschools_words:
        word_lower = word.lower()
        if word_lower not in all_words_lower:
            all_words_lower[word_lower] = word

    combined_words = sorted(all_words_lower.values(), key=str.lower)

    print(f"  Combined (deduplicated): {len(combined_words)} words")
    print(f"  Overlap: {len(vocab_com_words & greatschools_words)} words")

    # Enrich each word
    enriched_words = []
    for word in combined_words:
        word_entry = {
            "word": word,
            "definition": generate_simple_definition(word),
            "example": generate_example_sentence(word, grade),
            "subjects": classify_subject(word),
            "sources": []
        }

        # Track which source(s) this word came from
        if word in vocab_com_words:
            word_entry["sources"].append("Vocabulary.com")
        if word in greatschools_words:
            word_entry["sources"].append("GreatSchools")

        enriched_words.append(word_entry)

    # Create output structure
    output = {
        "grade": grade,
        "words": enriched_words,
        "metadata": {
            "total_words": len(enriched_words),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "sources": ["Vocabulary.com", "GreatSchools"],
            "vocab_com_count": len(vocab_com_words),
            "greatschools_count": len(greatschools_words),
            "overlap_count": len(vocab_com_words & greatschools_words),
            "note": "Definitions and examples are placeholders. Enrich with Claude API or dictionary service."
        }
    }

    # Save to final directory
    output_path = f"../final/grade-{grade}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Saved to {output_path}")

    return {
        'grade': grade,
        'total_words': len(enriched_words),
        'vocab_com': len(vocab_com_words),
        'greatschools': len(greatschools_words),
        'overlap': len(vocab_com_words & greatschools_words)
    }

def main():
    """Process all grades 6-12."""
    print("="*60)
    print("VOCABULARY PROCESSING & ENRICHMENT")
    print("="*60)
    print("Processing grades 6-12...")
    print("Combining Vocabulary.com + GreatSchools sources")
    print("="*60)

    results = []
    for grade in range(6, 13):
        result = process_grade(grade)
        results.append(result)
        time.sleep(0.1)  # Small delay between grades

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'Grade':<8} {'Total':<10} {'Vocab.com':<12} {'GreatSchools':<14} {'Overlap':<10}")
    print("-"*60)

    total_all = 0
    for r in results:
        print(f"{r['grade']:<8} {r['total_words']:<10} {r['vocab_com']:<12} {r['greatschools']:<14} {r['overlap']:<10}")
        total_all += r['total_words']

    print("-"*60)
    print(f"{'TOTAL':<8} {total_all:<10}")
    print("="*60)

    print(f"\n✓ All grade files saved to ../final/")
    print(f"✓ Total unique words across all grades: {total_all}")
    print(f"\nNext steps:")
    print(f"  1. Enrich definitions using Claude API or dictionary service")
    print(f"  2. Generate grade-appropriate example sentences")
    print(f"  3. Import into database (Supabase grade_words table)")

if __name__ == "__main__":
    main()
