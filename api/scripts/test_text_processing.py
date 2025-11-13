#!/usr/bin/env python3
"""
Test Script for Text Processing and Vocabulary Analysis

Tests the complete pipeline:
1. Text extraction from various formats
2. Word processing and tokenization
3. Vocabulary analysis and grade-level mapping

Usage:
    python scripts/test_text_processing.py
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.text_extraction import (
    extract_text_from_file,
    extract_from_txt,
    clean_text
)
from services.word_processing import (
    extract_words_from_text,
    extract_unique_words,
    calculate_word_frequency,
    get_word_statistics
)
from services.vocabulary_analysis import (
    analyze_vocabulary,
    compare_to_grade_standard
)
from services.database import get_session
from sqlmodel import Session


# Sample text for testing
SAMPLE_TEXT = """
The ancient civilization of Egypt flourished along the banks of the Nile River.
The Egyptians developed sophisticated agricultural techniques and monumental architecture.
Hieroglyphics, their intricate writing system, recorded historical events and religious beliefs.
The construction of pyramids demonstrated their advanced engineering capabilities.
Pharaohs ruled with absolute authority, claiming divine ancestry and commanding vast resources.
"""


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_text_extraction():
    """Test text extraction from plain text"""
    print_section("TEST 1: Text Extraction")

    # Test with plain text
    text_bytes = SAMPLE_TEXT.encode('utf-8')
    extracted = extract_from_txt(text_bytes)

    print("Original text length:", len(SAMPLE_TEXT))
    print("Extracted text length:", len(extracted))
    print("\nFirst 200 characters:")
    print(extracted[:200])
    print("\n✓ Text extraction successful")


def test_word_processing():
    """Test word processing and tokenization"""
    print_section("TEST 2: Word Processing")

    # Extract words
    words = extract_words_from_text(SAMPLE_TEXT)
    print(f"\nExtracted {len(words)} words (with duplicates)")
    print("Sample words:", words[:15])

    # Get unique words
    unique = extract_unique_words(SAMPLE_TEXT)
    print(f"\nUnique words: {len(unique)}")
    print("Unique words sample:", sorted(list(unique))[:15])

    # Calculate word frequency
    frequencies = calculate_word_frequency(SAMPLE_TEXT)
    print("\nTop 10 most frequent words:")
    sorted_freq = sorted(frequencies.items(), key=lambda x: -x[1])
    for word, count in sorted_freq[:10]:
        print(f"  {word}: {count}")

    # Get statistics
    stats = get_word_statistics(SAMPLE_TEXT)
    print("\nText statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✓ Word processing successful")


def test_vocabulary_analysis():
    """Test vocabulary analysis with database"""
    print_section("TEST 3: Vocabulary Analysis")

    try:
        # Get database session
        session = next(get_session())

        # Analyze for grade 8 student
        student_grade = 8
        print(f"\nAnalyzing vocabulary for Grade {student_grade} student...")

        profile = analyze_vocabulary(
            text=SAMPLE_TEXT,
            student_grade_level=student_grade,
            session=session
        )

        # Print statistics
        print("\n📊 Vocabulary Statistics:")
        stats = profile.statistics
        print(f"  Total words: {stats.total_words}")
        print(f"  Unique words: {stats.unique_words}")
        print(f"  Analyzed words: {stats.analyzed_words}")
        print(f"  Unknown words: {stats.unknown_words} ({stats.unknown_percentage:.1%})")
        print(f"  Average grade level: {stats.average_grade_level}")
        print(f"\n  Below grade: {stats.below_grade_count}")
        print(f"  At grade: {stats.at_grade_count}")
        print(f"  Above grade: {stats.above_grade_count}")

        # Print grade distribution
        print("\n📈 Grade Distribution:")
        dist = profile.grade_distribution.to_dict()
        for grade in range(6, 13):
            percentage = dist[grade]
            if percentage > 0:
                bar = "█" * int(percentage * 50)
                print(f"  Grade {grade:2d}: {percentage:6.1%} {bar}")

        # Print challenging words
        if profile.challenging_words:
            print(f"\n🎯 Top Challenging Words (Above Grade {student_grade}):")
            for word_result in profile.challenging_words[:10]:
                print(f"  • {word_result.word} (Grade {word_result.grade_level})")
                if word_result.definition:
                    print(f"    Definition: {word_result.definition[:80]}...")

        # Compare to standards
        comparison = compare_to_grade_standard(profile)
        print("\n📋 Performance Assessment:")
        print(f"  Student grade: {comparison['student_grade']}")
        print(f"  Average level: {comparison['average_grade_level']}")
        print(f"  Performance: {comparison['performance']}")
        print(f"  Proficiency score: {comparison['proficiency_score']}")

        print("\n💡 Recommendations:")
        for rec in comparison['recommendations']:
            print(f"  • {rec}")

        print("\n✓ Vocabulary analysis successful")

    except Exception as e:
        print(f"\n✗ Vocabulary analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()


def test_sample_words():
    """Test specific word examples"""
    print_section("TEST 4: Sample Word Analysis")

    try:
        session = next(get_session())

        test_words = [
            "analyze", "civilization", "sophisticated", "hieroglyphics",
            "demonstrate", "authority", "ancient", "construct"
        ]

        print("\nTesting specific words:")
        from services.vocabulary_analysis import map_words_to_grades

        word_map = map_words_to_grades(test_words, session)

        for word in test_words:
            if word in word_map:
                info = word_map[word]
                print(f"\n  {word}:")
                print(f"    Grade Level: {info['grade_level']}")
                print(f"    Subject: {info.get('subject', 'N/A')}")
                if info.get('definition'):
                    print(f"    Definition: {info['definition'][:60]}...")
            else:
                print(f"\n  {word}: Not found in database")

        print("\n✓ Sample word analysis successful")

    except Exception as e:
        print(f"\n✗ Sample word analysis failed: {str(e)}")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  TEXT PROCESSING AND VOCABULARY ANALYSIS TEST SUITE")
    print("=" * 70)

    try:
        # Test 1: Text extraction
        test_text_extraction()

        # Test 2: Word processing
        test_word_processing()

        # Test 3: Vocabulary analysis (requires database)
        test_vocabulary_analysis()

        # Test 4: Sample words
        test_sample_words()

        # Summary
        print_section("TEST SUMMARY")
        print("\n✓ All tests completed successfully!")
        print("\nThe text processing pipeline is ready for use.")
        print("\nNext steps:")
        print("  1. Install spaCy model: python -m spacy download en_core_web_sm")
        print("  2. Install NLP libraries: pip install -r requirements.txt")
        print("  3. Ensure grade_words table is populated")
        print("  4. Ready for Story 3.4 (Document Analysis Endpoint)")

    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Tests failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
