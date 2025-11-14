"""
Recommendation Service
Generates personalized vocabulary recommendations using LangChain and OpenAI
"""
import json
import logging
import requests
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from openai import OpenAIError

from services.llm import get_llm, token_tracker
from services import s3
from services.text_extraction import extract_text_from_file, TextExtractionError
from models.database import (
    Student,
    Document,
    GradeWord,
    AnalysisResult,
)

logger = logging.getLogger(__name__)


class RecommendationGenerationError(Exception):
    """Raised when recommendation generation fails"""
    pass


def get_student_vocabulary_profile(student_id: int, session: Session) -> Dict[str, Any]:
    """
    Get student's vocabulary profile from most recent analysis

    Args:
        student_id: Student ID
        session: Database session

    Returns:
        Dictionary with student's vocabulary statistics
    """
    # Get the most recent analysis result for this student
    statement = (
        select(AnalysisResult)
        .join(Document)
        .where(Document.student_id == student_id)
        .order_by(AnalysisResult.analyzed_at.desc())
    )
    latest_analysis = session.exec(statement).first()

    if latest_analysis:
        return {
            "average_grade_level": latest_analysis.average_grade_level or 0.0,
            "student_grade_level": latest_analysis.student_grade_level,
            "current_words": latest_analysis.word_details,
        }

    # If no analysis exists, get student's grade level
    student = session.get(Student, student_id)
    if student:
        return {
            "average_grade_level": float(student.grade_level),
            "student_grade_level": student.grade_level,
            "current_words": [],
        }

    raise RecommendationGenerationError(f"Student {student_id} not found")


def get_document_text(document_id: int, session: Session) -> tuple[str, str]:
    """
    Get document text and subject

    Args:
        document_id: Document ID
        session: Database session

    Returns:
        Tuple of (text_excerpt, subject)
    """
    document = session.get(Document, document_id)

    if not document:
        raise RecommendationGenerationError(f"Document {document_id} not found")

    try:
        # Download file from S3 using presigned URL
        download_url = s3.generate_presigned_download_url(document.s3_key)
        response = requests.get(download_url, timeout=60)
        response.raise_for_status()
        file_content = response.content

        # Extract text
        full_text = extract_text_from_file(
            file_content,
            file_type=document.file_type.value
        )

        # Limit to first 2000 characters for context
        text_excerpt = full_text[:2000]

        return text_excerpt, document.subject or "General"

    except Exception as e:
        logger.warning(f"Failed to extract document text: {e}")
        # Return empty excerpt if extraction fails
        return "", document.subject or "General"


def get_higher_grade_words(
    student_grade: int,
    subject: Optional[str],
    session: Session,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get available higher-grade words from grade_words table

    Args:
        student_grade: Student's current grade level
        subject: Optional subject filter
        session: Database session
        limit: Maximum number of words to return

    Returns:
        List of word dictionaries with word, grade_level, definition
    """
    # Target words 1-2 grades above student level
    target_grades = [student_grade + 1, student_grade + 2]

    statement = select(GradeWord).where(
        GradeWord.grade_level.in_(target_grades)
    )

    # Filter by subject if provided
    if subject and subject.lower() != "general":
        statement = statement.where(
            (GradeWord.subject == subject) | (GradeWord.subject == None)
        )

    # Limit results
    statement = statement.limit(limit)

    words = session.exec(statement).all()

    return [
        {
            "word": w.word,
            "grade_level": w.grade_level,
            "definition": w.definition,
            "example": w.example,
        }
        for w in words
    ]


async def generate_recommendations(
    student_id: int,
    document_id: Optional[int],
    session: Session,
    count: int = 10,
    subject: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Generate personalized vocabulary recommendations using LLM

    Args:
        student_id: Student ID
        document_id: Optional document ID to base recommendations on
        session: Database session
        count: Number of recommendations to generate (default: 10)
        subject: Optional subject filter

    Returns:
        List of recommendation dictionaries with:
        - current_usage: What student currently uses
        - recommended_word: Recommended vocabulary word
        - recommended_grade: Grade level of recommended word
        - context: Where this would fit
        - example_sentence: Example sentence
        - rationale: Why this word is recommended

    Raises:
        RecommendationGenerationError: If generation fails
    """
    try:
        # Step 1: Get student vocabulary profile
        logger.info(f"Getting vocabulary profile for student {student_id}")
        profile = get_student_vocabulary_profile(student_id, session)
        current_grade = profile["student_grade_level"]
        avg_grade = profile["average_grade_level"]

        # Step 2: Get document text if provided
        text_excerpt = ""
        doc_subject = subject

        if document_id:
            logger.info(f"Extracting text from document {document_id}")
            text_excerpt, doc_subject = get_document_text(document_id, session)
            if not subject:
                subject = doc_subject

        # Step 3: Get available higher-grade words
        logger.info(f"Fetching higher-grade words for grade {current_grade}")
        available_words = get_higher_grade_words(
            current_grade,
            subject,
            session,
            limit=50
        )

        if not available_words:
            logger.warning("No higher-grade words found in database")
            return []

        # Format available words for prompt
        words_list = ", ".join([
            f"{w['word']} (Grade {w['grade_level']})"
            for w in available_words[:30]  # Limit to avoid token overflow
        ])

        # Step 4: Create LangChain prompt
        prompt_template = ChatPromptTemplate.from_template("""
You are a vocabulary education expert for middle school students.

Student's current vocabulary level: Grade {current_grade} (average usage: {avg_grade})
Document subject: {subject}
{text_section}

Available higher-grade words for this subject:
{available_words}

Task: Identify {count} vocabulary improvements where the student could use more sophisticated words from the available list.

For each recommendation, provide:
1. current_usage: A simple phrase or word the student might currently use (infer from context or common usage)
2. recommended_word: A more sophisticated word from the available list
3. recommended_grade: The grade level of the recommended word (must match the word from the list)
4. context: A brief explanation of where/how this would fit (one sentence)
5. example_sentence: An example sentence using the recommended word in an age-appropriate context
6. rationale: Why this word is appropriate for this student (one sentence)

IMPORTANT:
- Only recommend words from the provided available words list
- Ensure recommended_grade matches the grade level shown in the list
- Make recommendations appropriate for a Grade {current_grade} student
- Focus on practical, commonly useful vocabulary
- Each recommendation should be unique (no duplicate words)

Output ONLY a valid JSON array with no additional text or formatting:
[
  {{
    "current_usage": "very good",
    "recommended_word": "excellent",
    "recommended_grade": 7,
    "context": "describing quality of work",
    "example_sentence": "The scientist's research was excellent.",
    "rationale": "Natural step up from 'very good', commonly used in academic writing"
  }}
]
""")

        # Prepare text section
        text_section = ""
        if text_excerpt:
            text_section = f"Student's text excerpt:\n{text_excerpt}\n"

        # Step 5: Invoke LLM
        logger.info("Invoking LLM to generate recommendations")
        llm = get_llm()

        chain = prompt_template | llm

        response = await chain.ainvoke({
            "current_grade": current_grade,
            "avg_grade": avg_grade,
            "subject": subject or "General",
            "text_section": text_section,
            "available_words": words_list,
            "count": count,
        })

        # Track token usage
        if hasattr(response, "response_metadata"):
            usage = response.response_metadata.get("token_usage", {})
            if usage:
                token_tracker.add_usage(
                    usage.get("prompt_tokens", 0),
                    usage.get("completion_tokens", 0)
                )
                logger.info(f"Token usage: {usage}")

        # Step 6: Parse JSON response
        logger.info("Parsing LLM response")
        content = response.content

        # Clean the response - remove markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        try:
            recommendations = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Response content: {content}")
            raise RecommendationGenerationError("LLM returned invalid JSON format")

        if not isinstance(recommendations, list):
            raise RecommendationGenerationError("LLM response is not a JSON array")

        # Step 7: Validate and filter recommendations
        logger.info(f"Validating {len(recommendations)} recommendations")
        valid_recommendations = []
        available_word_set = {w["word"].lower() for w in available_words}

        for rec in recommendations:
            # Validate required fields
            if not all(k in rec for k in ["recommended_word", "recommended_grade"]):
                logger.warning(f"Skipping invalid recommendation: {rec}")
                continue

            # Validate word is in available list
            if rec["recommended_word"].lower() not in available_word_set:
                logger.warning(f"Skipping word not in available list: {rec['recommended_word']}")
                continue

            # Validate grade level is higher than student's
            if rec["recommended_grade"] <= current_grade:
                logger.warning(f"Skipping word not above grade level: {rec['recommended_word']}")
                continue

            valid_recommendations.append(rec)

            # Stop if we have enough
            if len(valid_recommendations) >= count:
                break

        logger.info(f"Generated {len(valid_recommendations)} valid recommendations")
        return valid_recommendations

    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}", exc_info=True)
        raise RecommendationGenerationError(f"Failed to generate recommendations: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error generating recommendations: {e}", exc_info=True)
        raise RecommendationGenerationError(f"Failed to generate recommendations: {str(e)}")
