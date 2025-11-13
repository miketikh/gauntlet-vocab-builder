#!/usr/bin/env python3
"""
Import Grade-Level Vocabulary Data
Loads JSON word lists from language-docs/final/ and imports into Supabase grade_words table.

Usage:
    python scripts/import_vocab_data.py                 # Import all grades
    python scripts/import_vocab_data.py --grade 8       # Import specific grade
    python scripts/import_vocab_data.py --clear         # Clear table before import
    python scripts/import_vocab_data.py --dry-run       # Preview without inserting
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path to import from api modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select, create_engine
from models.database import GradeWord
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create engine directly to avoid importing problematic database.py
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable is not set")
    sys.exit(1)

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


def load_grade_json(file_path: Path) -> Dict[str, Any]:
    """Load and parse a grade-level JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        sys.exit(1)


def normalize_word(word: str) -> str:
    """Normalize word to lowercase for consistency."""
    return word.strip().lower()


def extract_subject(subjects: List[str]) -> str:
    """
    Extract primary subject from subjects list.
    Defaults to 'ELA' if not specified or if 'ELA' is in the list.
    """
    if not subjects:
        return "ELA"

    # Prefer ELA if present
    if "ELA" in subjects:
        return "ELA"

    # Filter out 'General' and return first specific subject
    specific_subjects = [s for s in subjects if s != "General"]
    if specific_subjects:
        return specific_subjects[0]

    return "ELA"


def transform_word_data(word_data: Dict[str, Any], grade_level: int) -> Dict[str, Any]:
    """
    Transform JSON word data to match GradeWord model fields.

    Input format:
    {
        "word": "abundant",
        "definition": "[Definition for abundant - to be enriched]",
        "example": "[Example sentence using 'abundant' for grade 6 - to be enriched]",
        "subjects": ["General", "ELA"],
        "sources": ["Vocabulary.com"]
    }

    Output format (for GradeWord model):
    {
        "word": "abundant",
        "grade_level": 6,
        "definition": "[Definition for abundant - to be enriched]",
        "example": "[Example sentence using 'abundant' for grade 6 - to be enriched]",
        "subject": "ELA",
        "frequency_rank": None
    }
    """
    return {
        "word": normalize_word(word_data["word"]),
        "grade_level": grade_level,
        "definition": word_data.get("definition", ""),
        "example": word_data.get("example"),
        "subject": extract_subject(word_data.get("subjects", [])),
        "frequency_rank": word_data.get("frequency_rank"),
    }


def validate_word_data(word_data: Dict[str, Any], grade_level: int) -> bool:
    """
    Validate that word data has all required fields.
    Returns True if valid, False otherwise.
    """
    if not word_data.get("word"):
        print(f"Warning: Missing word field in grade {grade_level}")
        return False

    if not word_data.get("definition"):
        print(f"Warning: Missing definition for word '{word_data.get('word')}' in grade {grade_level}")
        return False

    return True


def check_duplicate(session: Session, word: str, grade_level: int, subject: str) -> bool:
    """
    Check if a word already exists for the given grade level and subject.
    Returns True if duplicate exists, False otherwise.
    """
    statement = select(GradeWord).where(
        GradeWord.word == word,
        GradeWord.grade_level == grade_level,
        GradeWord.subject == subject
    )
    existing = session.exec(statement).first()
    return existing is not None


def import_grade_words(
    grade_level: int,
    data_dir: Path,
    session: Session,
    dry_run: bool = False
) -> tuple[int, int, int]:
    """
    Import words for a specific grade level.

    Returns:
        tuple: (imported_count, duplicate_count, invalid_count)
    """
    json_file = data_dir / f"grade-{grade_level}.json"

    if not json_file.exists():
        print(f"Warning: No file found for grade {grade_level} at {json_file}")
        return (0, 0, 0)

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Processing grade {grade_level}...")

    # Load JSON data
    data = load_grade_json(json_file)
    words_data = data.get("words", [])

    if not words_data:
        print(f"Warning: No words found in {json_file}")
        return (0, 0, 0)

    print(f"Found {len(words_data)} words in file")

    imported_count = 0
    duplicate_count = 0
    invalid_count = 0

    # Track duplicates within the same file
    seen_in_file = set()

    for word_data in words_data:
        # Validate word data
        if not validate_word_data(word_data, grade_level):
            invalid_count += 1
            continue

        # Transform data to match model
        transformed = transform_word_data(word_data, grade_level)

        # Check for duplicates within the same file
        word_key = (transformed["word"], transformed["subject"])
        if word_key in seen_in_file:
            duplicate_count += 1
            continue
        seen_in_file.add(word_key)

        # Check for duplicates in database
        if check_duplicate(session, transformed["word"], grade_level, transformed["subject"]):
            duplicate_count += 1
            continue

        # Insert into database
        if not dry_run:
            grade_word = GradeWord(**transformed)
            session.add(grade_word)

        imported_count += 1

        # Progress reporting every 50 words
        if imported_count % 50 == 0:
            print(f"  Imported {imported_count}/{len(words_data)} words...")

    if not dry_run:
        session.commit()

    print(f"{'[DRY RUN] ' if dry_run else ''}Grade {grade_level} complete:")
    print(f"  - Imported: {imported_count}")
    print(f"  - Duplicates skipped: {duplicate_count}")
    print(f"  - Invalid records: {invalid_count}")

    return (imported_count, duplicate_count, invalid_count)


def clear_grade_words_table(session: Session, dry_run: bool = False):
    """Clear all records from grade_words table."""
    if dry_run:
        count = len(session.exec(select(GradeWord)).all())
        print(f"[DRY RUN] Would delete {count} records from grade_words table")
    else:
        # Delete all records
        statement = select(GradeWord)
        records = session.exec(statement).all()
        count = len(records)

        for record in records:
            session.delete(record)
        session.commit()

        print(f"Deleted {count} records from grade_words table")


def main():
    """Main import function."""
    parser = argparse.ArgumentParser(
        description="Import grade-level vocabulary data into Supabase"
    )
    parser.add_argument(
        "--grade",
        type=int,
        choices=range(6, 13),
        help="Import specific grade level only (6-12)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear grade_words table before import"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview import without actually inserting data"
    )

    args = parser.parse_args()

    # Determine data directory path
    script_dir = Path(__file__).parent
    api_dir = script_dir.parent
    project_root = api_dir.parent
    data_dir = project_root / "language-docs" / "final"

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        sys.exit(1)

    print("=" * 60)
    print("Grade-Level Vocabulary Import Script")
    print("=" * 60)
    print(f"Data directory: {data_dir}")

    if args.dry_run:
        print("\n*** DRY RUN MODE - No data will be inserted ***\n")

    # Create database session
    with Session(engine) as session:
        # Clear table if requested
        if args.clear:
            confirm = "yes" if args.dry_run else input(
                "Are you sure you want to clear the grade_words table? (yes/no): "
            )
            if confirm.lower() == "yes":
                clear_grade_words_table(session, args.dry_run)
            else:
                print("Clear operation cancelled")
                return

        # Determine which grades to import
        if args.grade:
            grades = [args.grade]
        else:
            grades = range(6, 13)  # 6-12

        # Import data
        total_imported = 0
        total_duplicates = 0
        total_invalid = 0

        for grade in grades:
            imported, duplicates, invalid = import_grade_words(
                grade, data_dir, session, args.dry_run
            )
            total_imported += imported
            total_duplicates += duplicates
            total_invalid += invalid

        # Summary
        print("\n" + "=" * 60)
        print("Import Summary")
        print("=" * 60)
        print(f"Total words imported: {total_imported}")
        print(f"Total duplicates skipped: {total_duplicates}")
        print(f"Total invalid records: {total_invalid}")

        if args.dry_run:
            print("\n*** This was a DRY RUN - no data was inserted ***")
        else:
            print("\n*** Import complete! ***")

        # Verify counts in database
        if not args.dry_run:
            print("\nDatabase verification:")
            for grade in grades:
                statement = select(GradeWord).where(GradeWord.grade_level == grade)
                count = len(session.exec(statement).all())
                print(f"  Grade {grade}: {count} words")


if __name__ == "__main__":
    main()
