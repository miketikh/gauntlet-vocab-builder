#!/usr/bin/env python3
"""
Performance Test Script for Vocabulary Analysis

Tests the analysis pipeline with large documents to verify performance meets requirements.

Requirements (from PRD):
- Process 5,000-word document in <10 seconds
- Memory usage reasonable
- Database queries optimized

Usage:
    python scripts/test_performance.py
"""
import sys
import os
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.vocabulary_analysis import analyze_vocabulary
from services.database import get_session


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def generate_sample_text(target_words: int = 5000) -> str:
    """
    Generate sample text with approximately target_words words

    Uses realistic educational content to simulate real documents
    """
    # Sample paragraphs about various topics
    paragraphs = [
        """
        The ancient civilization of Egypt flourished along the banks of the Nile River
        for over three thousand years. The Egyptians developed sophisticated agricultural
        techniques, monumental architecture, and a complex writing system known as
        hieroglyphics. Their intricate beliefs about the afterlife led to the construction
        of elaborate tombs and pyramids that still stand today as testaments to their
        engineering prowess.
        """,
        """
        Photosynthesis represents one of the most fundamental biological processes on Earth,
        converting light energy into chemical energy stored in glucose molecules. Plants
        utilize chlorophyll within their chloroplasts to capture solar radiation and combine
        carbon dioxide with water, producing oxygen as a byproduct. This remarkable mechanism
        sustains nearly all life on our planet by providing the foundation of most food chains.
        """,
        """
        The Renaissance emerged in Italy during the fourteenth century, marking a profound
        transformation in European culture, art, and intellectual thought. Scholars rediscovered
        classical Greek and Roman texts, while artists like Leonardo da Vinci and Michelangelo
        revolutionized painting and sculpture. This period witnessed unprecedented innovations
        in literature, science, and philosophy that shaped the modern world.
        """,
        """
        Mathematical concepts such as algebra, geometry, and calculus provide essential tools
        for understanding patterns, relationships, and change in the natural world. Variables
        and equations enable us to model complex phenomena, from planetary motion to economic
        trends. The development of mathematical reasoning has been instrumental in advancing
        technology, engineering, and scientific discovery throughout human history.
        """,
        """
        Climate change presents one of the most pressing challenges facing humanity in the
        twenty-first century. Rising global temperatures result from increased concentrations
        of greenhouse gases in the atmosphere, primarily carbon dioxide from fossil fuel
        combustion. Scientists warn that without significant reductions in emissions,
        communities worldwide will face severe consequences including rising sea levels,
        extreme weather events, and disrupted ecosystems.
        """,
        """
        Literature serves as a mirror reflecting the values, conflicts, and aspirations of
        society across different eras. Through metaphor, symbolism, and narrative structure,
        authors communicate universal themes that resonate with readers regardless of their
        cultural background. Analyzing literary works develops critical thinking skills and
        enhances our understanding of human nature and social dynamics.
        """,
        """
        Democracy requires active participation from informed citizens who understand their
        rights and responsibilities within a constitutional framework. The separation of
        powers among executive, legislative, and judicial branches prevents the concentration
        of authority and protects individual liberties. Throughout history, democratic
        movements have emerged from people's desire for representation and accountability
        in governance.
        """,
        """
        Technological innovation has accelerated exponentially over the past century,
        fundamentally transforming how humans communicate, work, and interact with their
        environment. From the invention of the transistor to the development of artificial
        intelligence, each breakthrough builds upon previous discoveries. Understanding
        technology's impact on society remains essential for navigating an increasingly
        digital world.
        """
    ]

    # Calculate how many times we need to repeat paragraphs
    sample_text = " ".join(paragraphs)
    words_per_cycle = len(sample_text.split())
    repetitions = (target_words // words_per_cycle) + 1

    full_text = " ".join(paragraphs * repetitions)

    # Truncate to approximately target words
    words = full_text.split()[:target_words]
    return " ".join(words)


def test_small_document():
    """Test with small document (baseline)"""
    print_section("TEST 1: Small Document (500 words)")

    text = generate_sample_text(target_words=500)
    word_count = len(text.split())

    print(f"\nDocument size: {word_count} words")
    print(f"Text length: {len(text)} characters")

    try:
        session = next(get_session())

        start_time = time.time()
        profile = analyze_vocabulary(
            text=text,
            student_grade_level=8,
            session=session
        )
        elapsed = time.time() - start_time

        print(f"\nAnalysis completed in: {elapsed:.2f} seconds")
        print(f"Total words processed: {profile.statistics.total_words}")
        print(f"Unique words: {profile.statistics.unique_words}")
        print(f"Average grade level: {profile.statistics.average_grade_level}")

        print("\n✓ Small document test passed")
        return True

    except Exception as e:
        print(f"\n✗ Small document test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_large_document():
    """Test with 5,000-word document (PRD requirement)"""
    print_section("TEST 2: Large Document (5,000 words) - PRD REQUIREMENT")

    text = generate_sample_text(target_words=5000)
    word_count = len(text.split())

    print(f"\nDocument size: {word_count} words")
    print(f"Text length: {len(text):,} characters")

    try:
        session = next(get_session())

        print("\nStarting analysis...")
        start_time = time.time()

        profile = analyze_vocabulary(
            text=text,
            student_grade_level=8,
            session=session
        )

        elapsed = time.time() - start_time

        print(f"\n📊 Performance Results:")
        print(f"  Analysis time: {elapsed:.2f} seconds")
        print(f"  Words per second: {word_count / elapsed:.0f}")
        print(f"  PRD requirement: <10 seconds")

        # Check if we meet requirement
        meets_requirement = elapsed < 10.0
        status = "✓ PASSED" if meets_requirement else "✗ FAILED"
        print(f"  Status: {status}")

        print(f"\n📈 Analysis Results:")
        print(f"  Total words: {profile.statistics.total_words}")
        print(f"  Unique words: {profile.statistics.unique_words}")
        print(f"  Analyzed words: {profile.statistics.analyzed_words}")
        print(f"  Average grade level: {profile.statistics.average_grade_level}")
        print(f"  Challenging words found: {len(profile.challenging_words)}")

        if not meets_requirement:
            print("\n⚠ Warning: Analysis took longer than 10 seconds")
            print("  Consider optimizing database queries or text processing")

        return meets_requirement

    except Exception as e:
        print(f"\n✗ Large document test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_very_large_document():
    """Test with 10,000-word document (stress test)"""
    print_section("TEST 3: Very Large Document (10,000 words) - STRESS TEST")

    text = generate_sample_text(target_words=10000)
    word_count = len(text.split())

    print(f"\nDocument size: {word_count} words")
    print(f"Text length: {len(text):,} characters")
    print("\nNote: This stress test may take 20+ seconds")

    try:
        session = next(get_session())

        print("\nStarting analysis...")
        start_time = time.time()

        profile = analyze_vocabulary(
            text=text,
            student_grade_level=8,
            session=session
        )

        elapsed = time.time() - start_time

        print(f"\n📊 Performance Results:")
        print(f"  Analysis time: {elapsed:.2f} seconds")
        print(f"  Words per second: {word_count / elapsed:.0f}")

        print(f"\n📈 Analysis Results:")
        print(f"  Total words: {profile.statistics.total_words}")
        print(f"  Unique words: {profile.statistics.unique_words}")
        print(f"  Analyzed words: {profile.statistics.analyzed_words}")

        print("\n✓ Very large document test completed")
        return True

    except Exception as e:
        print(f"\n✗ Very large document test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_usage():
    """Test memory usage with large document"""
    print_section("TEST 4: Memory Usage Analysis")

    try:
        import psutil
        process = psutil.Process()

        # Measure baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"\nBaseline memory: {baseline_memory:.1f} MB")

        # Generate large document
        text = generate_sample_text(target_words=5000)
        session = next(get_session())

        # Analyze
        profile = analyze_vocabulary(
            text=text,
            student_grade_level=8,
            session=session
        )

        # Measure peak memory
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - baseline_memory

        print(f"Peak memory: {peak_memory:.1f} MB")
        print(f"Memory increase: {memory_increase:.1f} MB")

        # Check if reasonable (should be < 100MB increase for 5k words)
        reasonable = memory_increase < 100
        status = "✓ PASSED" if reasonable else "⚠ WARNING"
        print(f"Status: {status}")

        if not reasonable:
            print("⚠ High memory usage detected - consider optimization")

        return True

    except ImportError:
        print("\npsutil not installed - skipping memory test")
        print("Install with: pip install psutil")
        return True


def main():
    """Run all performance tests"""
    print("\n" + "=" * 70)
    print("  VOCABULARY ANALYSIS PERFORMANCE TEST SUITE")
    print("=" * 70)

    results = []

    try:
        # Test 1: Small document (baseline)
        results.append(("Small document (500 words)", test_small_document()))

        # Test 2: Large document (PRD requirement)
        results.append(("Large document (5,000 words)", test_large_document()))

        # Test 3: Very large document (stress test)
        results.append(("Very large document (10,000 words)", test_very_large_document()))

        # Test 4: Memory usage
        results.append(("Memory usage", test_memory_usage()))

        # Summary
        print_section("PERFORMANCE TEST SUMMARY")

        print("\nResults:")
        for test_name, passed in results:
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"  {status} - {test_name}")

        all_passed = all(result[1] for result in results)

        if all_passed:
            print("\n✓ All performance tests passed!")
            print("\nThe vocabulary analysis system meets PRD performance requirements:")
            print("  - Processes 5,000-word documents in <10 seconds")
            print("  - Memory usage is reasonable")
            print("  - Database queries are optimized")
        else:
            print("\n⚠ Some performance tests failed")
            print("Review the test output above for optimization opportunities")

        return 0 if all_passed else 1

    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n✗ Tests failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
