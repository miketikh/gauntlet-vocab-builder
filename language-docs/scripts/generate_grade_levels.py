#!/usr/bin/env python3
"""
Generate grade-level vocabulary files (6-12) with enriched word data.
Processes top 1,500 NGSL words + 120 AWL words.
"""

import json
from datetime import datetime

def assign_grade_level(word_data):
    """
    Assign appropriate grade level based on word characteristics.
    Returns grade level (6-12).
    """
    # For NGSL words - use frequency rank
    if word_data['source'] == 'NGSL':
        rank = word_data.get('sfi_rank', 0)
        if rank <= 300:
            return 6
        elif rank <= 600:
            return 7
        elif rank <= 900:
            return 8
        elif rank <= 1200:
            return 9
        elif rank <= 1400:
            return 10
        else:
            return 11

    # For AWL words - use sublist
    elif word_data['source'] == 'AWL':
        sublist = word_data.get('sublist', 1)
        if sublist == 1:
            return 8
        elif sublist == 2:
            return 9
        elif sublist <= 4:
            return 10
        elif sublist <= 7:
            return 11
        else:
            return 12

    return 8  # Default to grade 8

def classify_subjects(word):
    """
    Classify word into subject areas based on typical usage.
    Returns list of subjects.
    """
    # Math-related words
    math_words = ['add', 'subtract', 'multiply', 'divide', 'number', 'count', 'measure',
                  'calculate', 'equation', 'formula', 'ratio', 'percent', 'graph', 'data']

    # Science-related words
    science_words = ['experiment', 'hypothesis', 'observe', 'evidence', 'theory', 'chemical',
                     'energy', 'force', 'cell', 'molecule', 'organism', 'environment']

    # Social Studies-related words
    social_words = ['government', 'economy', 'culture', 'society', 'history', 'geography',
                    'community', 'citizen', 'policy', 'tradition', 'region']

    word_lower = word.lower()
    subjects = ["General"]  # All words are at least general

    if any(w in word_lower for w in math_words):
        subjects.append("Math")
    if any(w in word_lower for w in science_words):
        subjects.append("Science")
    if any(w in word_lower for w in social_words):
        subjects.append("Social Studies")

    # Most academic words are relevant to ELA
    if len(subjects) == 1:
        subjects.append("ELA")

    return subjects

def generate_definition(word):
    """
    Generate a simple definition placeholder.
    In production, this would use a dictionary API or AI.
    """
    return f"to {word}" if word.endswith('e') else f"the act of {word}ing"

def generate_example(word, grade):
    """
    Generate an example sentence placeholder.
    In production, this would use AI to generate contextual examples.
    """
    return f"Students in grade {grade} can {word} to understand the concept."

def load_ngsl(top_n=1500):
    """Load top N words from NGSL."""
    with open('../raw/ngsl-complete.json', 'r') as f:
        data = json.load(f)

    # Get top N by rank
    words = sorted(data['words'], key=lambda x: x['sfi_rank'])[:top_n]
    return words

def load_awl():
    """Load all AWL words."""
    with open('../raw/awl-partial.json', 'r') as f:
        data = json.load(f)
    return data['words']

def process_vocabulary():
    """Main processing function."""

    print("Loading vocabulary data...")
    ngsl_words = load_ngsl(1500)
    awl_words = load_awl()

    print(f"Loaded {len(ngsl_words)} NGSL words")
    print(f"Loaded {len(awl_words)} AWL words")

    # Initialize grade-level buckets
    grades = {i: [] for i in range(6, 13)}

    # Process NGSL words
    print("\nProcessing NGSL words...")
    for word_data in ngsl_words:
        word = word_data['word']
        grade = assign_grade_level(word_data)

        enriched = {
            "word": word,
            "definition": f"[Definition for {word}]",  # Placeholder
            "example": f"[Example sentence using {word}]",  # Placeholder
            "subjects": classify_subjects(word),
            "frequency_rank": word_data['sfi_rank'],
            "sources": ["NGSL"]
        }

        grades[grade].append(enriched)

    # Process AWL words
    print("Processing AWL words...")
    for word_data in awl_words:
        word = word_data['headword']
        grade = assign_grade_level(word_data)

        enriched = {
            "word": word,
            "definition": f"[Definition for {word}]",  # Placeholder
            "example": f"[Example sentence using {word}]",  # Placeholder
            "subjects": classify_subjects(word),
            "sources": [f"AWL-sublist-{word_data['sublist']}"]
        }

        grades[grade].append(enriched)

    # Generate output files
    print("\nGenerating grade-level files...")
    for grade, words in grades.items():
        # Sort words alphabetically
        words.sort(key=lambda x: x['word'])

        output = {
            "grade": grade,
            "words": words,
            "metadata": {
                "total_words": len(words),
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "sources": ["NGSL-1.2", "AWL"]
            }
        }

        output_path = f"../final/grade-{grade}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Grade {grade}: {len(words)} words → {output_path}")

    # Summary
    total = sum(len(words) for words in grades.values())
    print(f"\n✓ Generated 7 files with {total} total word entries")
    print(f"✓ Note: Definitions and examples are placeholders - need AI enrichment")

if __name__ == "__main__":
    process_vocabulary()
