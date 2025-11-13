#!/usr/bin/env python3
"""
Parse the New General Service List (NGSL) 1.2 from CSV into structured JSON.
The NGSL contains 2,809 high-frequency words for general English.
"""

import json
import csv


def parse_ngsl():
    """Parse NGSL CSV data into structured JSON format."""

    words = []

    # Read the CSV file
    csv_path = "../raw/NGSL_12_stats.csv"

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            word_entry = {
                "word": row['Lemma'].strip(),
                "sfi_rank": int(row['SFI Rank']),
                "sfi_score": float(row['SFI']),
                "frequency_per_million": float(row['Adjusted Frequency per Million (U)']),
                "source": "NGSL"
            }

            words.append(word_entry)

    return {
        "name": "New General Service List (NGSL) 1.2",
        "description": "2,809 high-frequency words for general English and daily life",
        "source": "Browne, C., Culligan, B., and Phillips, J.",
        "version": "1.2",
        "total_words": len(words),
        "words": words
    }


if __name__ == "__main__":
    ngsl_data = parse_ngsl()

    # Save to JSON file
    output_path = "../raw/ngsl-complete.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ngsl_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Parsed {ngsl_data['total_words']} NGSL words")
    print(f"✓ Saved to {output_path}")

    # Print sample
    print(f"\nSample words:")
    for word in ngsl_data['words'][:5]:
        print(f"  {word['sfi_rank']}. {word['word']} (freq: {word['frequency_per_million']:.0f}/million)")
