"""
Recommendations Router
Endpoints for generating and managing vocabulary recommendations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from dependencies.auth import get_current_user
from services.database import get_session
from services.educator import get_educator_by_email
from services.recommendation_service import (
    generate_recommendations as generate_recommendations_service,
    RecommendationGenerationError
)
from models.database import (
    Student,
    Recommendation,
    RecommendationPublic,
    RecommendationStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response models
class GenerateRecommendationsRequest(BaseModel):
    """Request body for generating recommendations"""
    document_id: Optional[int] = Field(default=None, description="Document ID to base recommendations on")
    count: int = Field(default=10, ge=1, le=20, description="Number of recommendations to generate")
    subject: Optional[str] = Field(default=None, description="Subject filter (e.g., ELA, Math, Science)")


class GenerateRecommendationsResponse(BaseModel):
    """Response for generating recommendations"""
    recommendations: List[RecommendationPublic]
    count: int
    student_current_grade: int
    student_id: int


# Helper function to verify educator owns student
def verify_educator_owns_student(
    educator_id: int,
    student_id: int,
    session: Session
) -> Student:
    """
    Verify that the educator owns the specified student

    Args:
        educator_id: ID of the educator
        student_id: ID of the student
        session: Database session

    Returns:
        Student: The student record if ownership verified

    Raises:
        HTTPException 404: If student not found
        HTTPException 403: If educator doesn't own the student
    """
    statement = select(Student).where(Student.id == student_id)
    student = session.exec(statement).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )

    if student.educator_id != educator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this student's data"
        )

    return student


def check_for_duplicate_recommendations(
    student_id: int,
    words: List[str],
    session: Session
) -> set:
    """
    Check for existing pending recommendations to avoid duplicates

    Args:
        student_id: Student ID
        words: List of words to check
        session: Database session

    Returns:
        Set of words that already have pending recommendations
    """
    if not words:
        return set()

    statement = select(Recommendation).where(
        Recommendation.student_id == student_id,
        Recommendation.word.in_([w.lower() for w in words]),
        Recommendation.status == RecommendationStatus.PENDING
    )

    existing = session.exec(statement).all()
    return {rec.word.lower() for rec in existing}


@router.post(
    "/{student_id}/recommendations/generate",
    response_model=GenerateRecommendationsResponse,
    status_code=status.HTTP_201_CREATED
)
async def generate_recommendations(
    student_id: int,
    request: GenerateRecommendationsRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Generate personalized vocabulary recommendations for a student

    This endpoint:
    1. Verifies educator owns the student
    2. Calls LLM service to generate recommendations
    3. Stores recommendations in database (deduplicating existing ones)
    4. Returns generated recommendations

    Protected endpoint - requires valid JWT token.

    Args:
        student_id: Student ID to generate recommendations for
        request: Request parameters (document_id, count, subject)
        user: Current authenticated user from JWT
        session: Database session

    Returns:
        GenerateRecommendationsResponse: Generated recommendations

    Raises:
        HTTPException 401: If authentication fails
        HTTPException 403: If educator doesn't own student
        HTTPException 404: If student not found
        HTTPException 500: If recommendation generation fails
    """
    # Get educator from JWT email
    email = user["email"]
    educator = get_educator_by_email(session, email)

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator profile not found",
        )

    # Verify educator owns student
    student = verify_educator_owns_student(educator.id, student_id, session)

    try:
        # Generate recommendations using LLM service
        logger.info(
            f"Generating {request.count} recommendations for student {student_id}, "
            f"document: {request.document_id}, subject: {request.subject}"
        )

        recommendations_data = await generate_recommendations_service(
            student_id=student_id,
            document_id=request.document_id,
            session=session,
            count=request.count,
            subject=request.subject,
        )

        if not recommendations_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No recommendations could be generated. Try analyzing a document first."
            )

        # Check for duplicates
        words_to_recommend = [rec["recommended_word"] for rec in recommendations_data]
        existing_words = check_for_duplicate_recommendations(
            student_id,
            words_to_recommend,
            session
        )

        # Store recommendations in database (skip duplicates)
        saved_recommendations = []
        for rec_data in recommendations_data:
            word = rec_data["recommended_word"]

            # Skip if already exists
            if word.lower() in existing_words:
                logger.info(f"Skipping duplicate recommendation: {word}")
                continue

            # Create recommendation record
            recommendation = Recommendation(
                student_id=student_id,
                document_id=request.document_id,
                word=word,
                recommended_grade_level=rec_data.get("recommended_grade", student.grade_level + 1),
                subject=request.subject,
                current_usage=rec_data.get("current_usage"),
                context=rec_data.get("context"),
                example_sentence=rec_data.get("example_sentence"),
                rationale=rec_data.get("rationale"),
                status=RecommendationStatus.PENDING,
                recommended_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            session.add(recommendation)
            saved_recommendations.append(recommendation)

        # Commit to database
        session.commit()

        # Refresh to get IDs
        for rec in saved_recommendations:
            session.refresh(rec)

        logger.info(f"Saved {len(saved_recommendations)} recommendations for student {student_id}")

        # Convert to public models
        recommendations_public = [
            RecommendationPublic(
                id=rec.id,
                student_id=rec.student_id,
                document_id=rec.document_id,
                word=rec.word,
                recommended_grade_level=rec.recommended_grade_level,
                subject=rec.subject,
                current_usage=rec.current_usage,
                context=rec.context,
                example_sentence=rec.example_sentence,
                rationale=rec.rationale,
                status=rec.status,
                recommended_at=rec.recommended_at,
            )
            for rec in saved_recommendations
        ]

        return GenerateRecommendationsResponse(
            recommendations=recommendations_public,
            count=len(recommendations_public),
            student_current_grade=student.grade_level,
            student_id=student_id,
        )

    except RecommendationGenerationError as e:
        logger.error(f"Recommendation generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get(
    "/{student_id}/recommendations",
    response_model=List[RecommendationPublic]
)
async def get_student_recommendations(
    student_id: int,
    subject: Optional[str] = Query(default=None, description="Filter by subject"),
    status_filter: Optional[RecommendationStatus] = Query(default=None, alias="status", description="Filter by status"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of recommendations to return"),
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get saved recommendations for a student

    This endpoint:
    1. Verifies educator owns the student
    2. Retrieves recommendations from database
    3. Supports filtering by subject and status

    Protected endpoint - requires valid JWT token.

    Args:
        student_id: Student ID
        subject: Optional subject filter
        status_filter: Optional status filter (pending, adopted, not_used)
        limit: Maximum number of recommendations to return
        user: Current authenticated user from JWT
        session: Database session

    Returns:
        List[RecommendationPublic]: Student's recommendations

    Raises:
        HTTPException 401: If authentication fails
        HTTPException 403: If educator doesn't own student
        HTTPException 404: If student not found
    """
    # Get educator from JWT email
    email = user["email"]
    educator = get_educator_by_email(session, email)

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator profile not found",
        )

    # Verify educator owns student
    verify_educator_owns_student(educator.id, student_id, session)

    # Build query
    statement = select(Recommendation).where(
        Recommendation.student_id == student_id
    )

    # Apply filters
    if subject:
        statement = statement.where(Recommendation.subject == subject)

    if status_filter:
        statement = statement.where(Recommendation.status == status_filter)

    # Order by most recent first
    statement = statement.order_by(Recommendation.recommended_at.desc())

    # Apply limit
    statement = statement.limit(limit)

    # Execute query
    recommendations = session.exec(statement).all()

    # Convert to public models
    return [
        RecommendationPublic(
            id=rec.id,
            student_id=rec.student_id,
            document_id=rec.document_id,
            word=rec.word,
            recommended_grade_level=rec.recommended_grade_level,
            subject=rec.subject,
            current_usage=rec.current_usage,
            context=rec.context,
            example_sentence=rec.example_sentence,
            rationale=rec.rationale,
            status=rec.status,
            recommended_at=rec.recommended_at,
        )
        for rec in recommendations
    ]
