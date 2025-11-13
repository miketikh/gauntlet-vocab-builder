"""
Students Router
Endpoints for student management
"""
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from dependencies.auth import get_current_user
from services.database import get_session
from services.educator import get_educator_by_email
from models.database import (
    Student,
    StudentCreate,
    StudentPublic,
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
