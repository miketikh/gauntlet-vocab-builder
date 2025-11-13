"""
Vocabulary Analysis Service
Analyzes vocabulary and maps words to grade levels
"""
from typing import Dict, List, Optional, Set
from collections import Counter
import logging
from sqlmodel import Session, select

from models.database import GradeWord
from models.analysis import (
    WordAnalysisResult,
    WordCategory,
    VocabularyProfile,
    VocabularyStatistics,
    GradeDistribution
)
from services.word_processing import (
    extract_words_from_text,
    calculate_word_frequency
)


logger = logging.getLogger(__name__)


class VocabularyAnalysisError(Exception):
    """Raised when vocabulary analysis fails"""
    pass


def map_words_to_grades(
    words: List[str],
    session: Session
) -> Dict[str, Dict]:
    """
    Map words to their grade levels by querying the database

    Args:
        words: List of words to look up
        session: Database session

    Returns:
        Dictionary mapping word to grade info:
        {
            "word": {
                "grade_level": 8,
                "definition": "...",
                "example": "...",
                "subject": "ELA"
            }
        }
    """
    if not words:
        return {}

    # Convert to lowercase and remove duplicates
    unique_words = list(set(word.lower() for word in words))

    # Query database for all words at once (batch query for efficiency)
    statement = select(GradeWord).where(GradeWord.word.in_(unique_words))
    results = session.exec(statement).all()

    # Build lookup dictionary
    word_map = {}
    for grade_word in results:
        word_key = grade_word.word.lower()

        # If word already exists, keep the lowest grade level (most accessible)
        if word_key in word_map:
            if grade_word.grade_level < word_map[word_key]["grade_level"]:
                word_map[word_key] = {
                    "grade_level": grade_word.grade_level,
                    "definition": grade_word.definition,
                    "example": grade_word.example,
                    "subject": grade_word.subject
                }
        else:
            word_map[word_key] = {
                "grade_level": grade_word.grade_level,
                "definition": grade_word.definition,
                "example": grade_word.example,
                "subject": grade_word.subject
            }

    logger.info(f"Mapped {len(word_map)} out of {len(unique_words)} words to grade levels")
    return word_map


def categorize_word(
    word_grade: Optional[int],
    student_grade: int
) -> WordCategory:
    """
    Categorize a word relative to student's grade level

    Args:
        word_grade: Grade level of the word (or None if unknown)
        student_grade: Student's current grade level

    Returns:
        WordCategory indicating difficulty relative to student
    """
    if word_grade is None:
        return WordCategory.UNKNOWN

    if word_grade < student_grade:
        return WordCategory.BELOW
    elif word_grade == student_grade:
        return WordCategory.AT
    else:  # word_grade > student_grade
        return WordCategory.ABOVE


def calculate_grade_distribution(
    word_grades: List[int]
) -> GradeDistribution:
    """
    Calculate percentage distribution of words across grade levels

    Args:
        word_grades: List of grade levels for analyzed words

    Returns:
        GradeDistribution with percentages for each grade
    """
    if not word_grades:
        return GradeDistribution(
            grade_6=0.0, grade_7=0.0, grade_8=0.0, grade_9=0.0,
            grade_10=0.0, grade_11=0.0, grade_12=0.0
        )

    # Count words per grade
    grade_counts = Counter(word_grades)
    total = len(word_grades)

    # Calculate percentages
    distribution = {}
    for grade in range(6, 13):
        count = grade_counts.get(grade, 0)
        distribution[grade] = round(count / total, 4) if total > 0 else 0.0

    return GradeDistribution.from_dict(distribution)


def calculate_average_grade_level(
    word_grades: List[int]
) -> Optional[float]:
    """
    Calculate weighted average grade level

    Args:
        word_grades: List of grade levels for analyzed words

    Returns:
        Average grade level or None if no words analyzed
    """
    if not word_grades:
        return None

    return round(sum(word_grades) / len(word_grades), 1)


def analyze_vocabulary(
    text: str,
    student_grade_level: int,
    session: Session,
    min_word_length: int = 3
) -> VocabularyProfile:
    """
    Main vocabulary analysis function

    Analyzes text to:
    - Extract and count words
    - Map words to grade levels
    - Categorize words relative to student's grade
    - Calculate statistics and distributions

    Args:
        text: Text to analyze
        student_grade_level: Student's current grade level (6-12)
        session: Database session for querying grade_words
        min_word_length: Minimum word length to consider (default: 3)

    Returns:
        VocabularyProfile with complete analysis

    Raises:
        VocabularyAnalysisError: If analysis fails
    """
    try:
        # Step 1: Extract words and calculate frequencies
        logger.info("Extracting words from text")
        word_frequency = calculate_word_frequency(text, min_length=min_word_length)

        if not word_frequency:
            raise VocabularyAnalysisError("No words found in text after processing")

        total_words = sum(word_frequency.values())
        unique_words = len(word_frequency)

        logger.info(f"Found {total_words} total words, {unique_words} unique")

        # Step 2: Map words to grade levels
        logger.info("Mapping words to grade levels")
        word_map = map_words_to_grades(list(word_frequency.keys()), session)

        # Step 3: Analyze each word
        word_details: List[WordAnalysisResult] = []
        challenging_words: List[WordAnalysisResult] = []
        analyzed_grades: List[int] = []

        # Category counters
        below_count = 0
        at_count = 0
        above_count = 0
        unknown_count = 0

        for word, frequency in word_frequency.items():
            word_lower = word.lower()
            grade_info = word_map.get(word_lower)

            if grade_info:
                grade_level = grade_info["grade_level"]
                analyzed_grades.append(grade_level)
            else:
                grade_level = None

            # Categorize word
            category = categorize_word(grade_level, student_grade_level)

            # Update counters
            if category == WordCategory.BELOW:
                below_count += 1
            elif category == WordCategory.AT:
                at_count += 1
            elif category == WordCategory.ABOVE:
                above_count += 1
            else:
                unknown_count += 1

            # Create word analysis result
            result = WordAnalysisResult(
                word=word,
                frequency=frequency,
                grade_level=grade_level,
                definition=grade_info.get("definition") if grade_info else None,
                example=grade_info.get("example") if grade_info else None,
                subject=grade_info.get("subject") if grade_info else None,
                category=category
            )

            word_details.append(result)

            # Add to challenging words if above grade level
            if category == WordCategory.ABOVE:
                challenging_words.append(result)

        # Sort challenging words by grade level (highest first), then by frequency
        challenging_words.sort(key=lambda x: (-x.grade_level if x.grade_level else 0, -x.frequency))

        # Step 4: Calculate statistics
        analyzed_count = len(analyzed_grades)
        unknown_percentage = unknown_count / unique_words if unique_words > 0 else 0.0

        statistics = VocabularyStatistics(
            total_words=total_words,
            unique_words=unique_words,
            analyzed_words=analyzed_count,
            unknown_words=unknown_count,
            unknown_percentage=round(unknown_percentage, 4),
            average_grade_level=calculate_average_grade_level(analyzed_grades),
            below_grade_count=below_count,
            at_grade_count=at_count,
            above_grade_count=above_count
        )

        # Step 5: Calculate grade distribution
        grade_distribution = calculate_grade_distribution(analyzed_grades)

        # Step 6: Build and return profile
        profile = VocabularyProfile(
            student_grade_level=student_grade_level,
            statistics=statistics,
            grade_distribution=grade_distribution,
            challenging_words=challenging_words[:20],  # Limit to top 20 challenging words
            word_details=word_details
        )

        logger.info(
            f"Analysis complete: {analyzed_count} words analyzed, "
            f"avg grade level: {statistics.average_grade_level}"
        )

        return profile

    except Exception as e:
        logger.error(f"Vocabulary analysis failed: {str(e)}", exc_info=True)
        raise VocabularyAnalysisError(f"Failed to analyze vocabulary: {str(e)}") from e


def get_words_by_category(
    profile: VocabularyProfile,
    category: WordCategory,
    limit: Optional[int] = None
) -> List[WordAnalysisResult]:
    """
    Get words from a specific category

    Args:
        profile: VocabularyProfile to filter
        category: Category to filter by
        limit: Optional limit on number of words

    Returns:
        List of words in the specified category
    """
    words = [w for w in profile.word_details if w.category == category]

    # Sort by frequency (most common first)
    words.sort(key=lambda x: -x.frequency)

    if limit:
        words = words[:limit]

    return words


def get_subject_breakdown(
    profile: VocabularyProfile
) -> Dict[str, int]:
    """
    Get breakdown of words by subject area

    Args:
        profile: VocabularyProfile to analyze

    Returns:
        Dictionary mapping subject to count
    """
    subject_counts = Counter(
        word.subject for word in profile.word_details
        if word.subject is not None
    )

    return dict(subject_counts)


def compare_to_grade_standard(
    profile: VocabularyProfile
) -> Dict[str, any]:
    """
    Compare student's vocabulary to grade-level standards

    Args:
        profile: VocabularyProfile to evaluate

    Returns:
        Dictionary with comparison insights
    """
    stats = profile.statistics
    student_grade = profile.student_grade_level

    # Calculate performance indicators
    proficiency_score = 0.0
    if stats.analyzed_words > 0:
        # Weight categories: below=0.5, at=1.0, above=1.5
        weighted_sum = (
            stats.below_grade_count * 0.5 +
            stats.at_grade_count * 1.0 +
            stats.above_grade_count * 1.5
        )
        proficiency_score = round(weighted_sum / stats.analyzed_words, 2)

    # Determine performance level
    if stats.average_grade_level is None:
        performance = "unknown"
    elif stats.average_grade_level < student_grade - 1:
        performance = "below"
    elif stats.average_grade_level > student_grade + 1:
        performance = "advanced"
    else:
        performance = "on_level"

    return {
        "student_grade": student_grade,
        "average_grade_level": stats.average_grade_level,
        "performance": performance,
        "proficiency_score": proficiency_score,
        "challenging_word_count": len(profile.challenging_words),
        "recommendations": generate_recommendations(profile)
    }


def generate_recommendations(
    profile: VocabularyProfile
) -> List[str]:
    """
    Generate simple recommendations based on analysis

    Args:
        profile: VocabularyProfile to evaluate

    Returns:
        List of recommendation strings
    """
    recommendations = []
    stats = profile.statistics

    # Check if needs vocabulary support
    if stats.average_grade_level and stats.average_grade_level < profile.student_grade_level - 1:
        recommendations.append(
            "Consider providing vocabulary support - many words are below grade level"
        )

    # Check if being challenged
    if stats.above_grade_count < stats.analyzed_words * 0.1:  # Less than 10% challenging
        recommendations.append(
            "Consider introducing more grade-appropriate challenging vocabulary"
        )

    # Check if too challenging
    if stats.above_grade_count > stats.analyzed_words * 0.3:  # More than 30% challenging
        recommendations.append(
            "Material may be quite challenging - consider vocabulary pre-teaching"
        )

    # Check unknown words
    if stats.unknown_percentage > 0.3:  # More than 30% unknown
        recommendations.append(
            "Many words not in standard lists - may include specialized or advanced vocabulary"
        )

    if not recommendations:
        recommendations.append("Vocabulary usage appears appropriate for grade level")

    return recommendations
