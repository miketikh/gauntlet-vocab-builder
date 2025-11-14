"""
Students Router
Endpoints for student management
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel, Field

from dependencies.auth import get_current_user
from services.database import get_session
from services.educator import get_educator_by_email
from models.database import (
    Student,
    StudentCreate,
    StudentPublic,
    VocabularyHistory,
    VocabularyHistoryPublic,
    Document,
)

router = APIRouter()


@router.post("", response_model=StudentPublic, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Create a new student profile

    This endpoint:
    1. Verifies JWT token and gets educator from email
    2. Validates student data (name, grade_level 6-12)
    3. Creates student record linked to educator
    4. Returns created student

    Protected endpoint - requires valid JWT token in Authorization header.

    Args:
        student_data: Student information (name, grade_level, reading_level, notes)
        user: Current authenticated user from JWT
        session: Database session

    Returns:
        StudentPublic: Created student information

    Raises:
        HTTPException 401: If authentication fails
        HTTPException 404: If educator not found
        HTTPException 422: If validation fails (e.g., invalid grade level)
    """
    # Get educator from JWT email
    email = user["email"]
    educator = get_educator_by_email(session, email)

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator profile not found. Please complete registration.",
        )

    # Create student record
    new_student = Student(
        educator_id=educator.id,
        name=student_data.name,
        grade_level=student_data.grade_level,
        reading_level=student_data.reading_level,
        notes=student_data.notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    session.add(new_student)
    session.commit()
    session.refresh(new_student)

    return new_student


@router.get("", response_model=list[StudentPublic])
async def get_students(
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get all students for the current educator

    Protected endpoint - requires valid JWT token.
    Returns only students belonging to the authenticated educator.

    Args:
        user: Current authenticated user from JWT
        session: Database session

    Returns:
        list[StudentPublic]: List of students for this educator
    """
    # Get educator from JWT email
    email = user["email"]
    educator = get_educator_by_email(session, email)

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator profile not found",
        )

    # Get all students for this educator
    statement = select(Student).where(Student.educator_id == educator.id)
    students = session.exec(statement).all()

    return students


@router.get("/{student_id}", response_model=StudentPublic)
async def get_student(
    student_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get a specific student by ID

    Protected endpoint - verifies the student belongs to the authenticated educator.

    Args:
        student_id: Student database ID
        user: Current authenticated user from JWT
        session: Database session

    Returns:
        StudentPublic: Student information

    Raises:
        HTTPException 404: If student not found or doesn't belong to educator
    """
    # Get educator
    email = user["email"]
    educator = get_educator_by_email(session, email)

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator profile not found",
        )

    # Get student and verify ownership
    student = session.get(Student, student_id)

    if not student or student.educator_id != educator.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return student


# Response models for vocabulary history
class VocabularyHistoryDataPoint(BaseModel):
    """Single data point in vocabulary progress"""
    date: str
    average_grade_level: Optional[float]
    document_id: int
    document_title: str
    unique_words: int
    total_words: int


class VocabularyHistoryResponse(BaseModel):
    """Response for vocabulary history endpoint"""
    student_id: int
    data_points: List[VocabularyHistoryDataPoint]
    overall_trend: str
    grade_level_change: float


@router.get("/{student_id}/vocabulary/history", response_model=VocabularyHistoryResponse)
async def get_vocabulary_history(
    student_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get historical vocabulary tracking data for a student

    This endpoint:
    1. Verifies educator owns the student
    2. Retrieves all vocabulary history snapshots
    3. Calculates overall trend (improving, stable, declining)
    4. Returns time-series data for visualization

    Protected endpoint - requires valid JWT token.

    Args:
        student_id: Student ID
        user: Current authenticated user from JWT
        session: Database session

    Returns:
        VocabularyHistoryResponse: Historical vocabulary data with trend analysis

    Raises:
        HTTPException 401: If authentication fails
        HTTPException 403: If educator doesn't own student
        HTTPException 404: If student not found or insufficient data
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
    student = session.get(Student, student_id)
    if not student or student.educator_id != educator.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    # Get all vocabulary history for this student, ordered by date
    statement = (
        select(VocabularyHistory, Document)
        .join(Document, VocabularyHistory.document_id == Document.id)
        .where(VocabularyHistory.student_id == student_id)
        .order_by(VocabularyHistory.analyzed_at)
    )

    results = session.exec(statement).all()

    # Check if we have enough data
    if len(results) < 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enough data. At least 2 analyzed documents are required to show progress.",
        )

    # Build data points
    data_points = []
    for history, document in results:
        data_points.append(VocabularyHistoryDataPoint(
            date=history.analyzed_at.strftime("%Y-%m-%d"),
            average_grade_level=history.average_grade_level,
            document_id=history.document_id,
            document_title=document.title,
            unique_words=history.unique_words,
            total_words=history.total_words,
        ))

    # Calculate trend
    first_grade = data_points[0].average_grade_level or 0.0
    last_grade = data_points[-1].average_grade_level or 0.0
    grade_level_change = last_grade - first_grade

    # Determine trend: improving (>0.2), stable (-0.2 to +0.2), declining (<-0.2)
    if grade_level_change > 0.2:
        overall_trend = "improving"
    elif grade_level_change < -0.2:
        overall_trend = "declining"
    else:
        overall_trend = "stable"

    return VocabularyHistoryResponse(
        student_id=student_id,
        data_points=data_points,
        overall_trend=overall_trend,
        grade_level_change=round(grade_level_change, 2),
    )
