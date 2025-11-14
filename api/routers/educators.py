"""
Educators Router
Endpoints for educator-level analytics and class management
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from pydantic import BaseModel, Field

from dependencies.auth import get_current_user
from services.database import get_session
from services.educator import get_educator_by_email
from models.database import (
    Student,
    VocabularyHistory,
    Recommendation,
    RecommendationStatus,
)

router = APIRouter()


# Response models for analytics
class GradeDistribution(BaseModel):
    """Distribution of students by grade level performance"""
    below_grade: int = Field(description="Students below their actual grade level")
    at_grade: int = Field(description="Students at or near their grade level (within 0.5)")
    above_grade: int = Field(description="Students above their grade level")


class StudentSummary(BaseModel):
    """Summary information for a student"""
    student_id: int
    name: str
    current_grade_level: Optional[float] = Field(description="Latest vocabulary grade level")
    actual_grade: int = Field(description="Student's actual school grade")
    progress_trend: str = Field(description="improving, stable, or declining")
    grade_level_change: float = Field(description="Change in grade level from first to last analysis")
    adoption_rate: float = Field(description="Percentage of recommendations adopted (0-1)")
    total_recommendations: int
    adopted_recommendations: int
    last_activity: Optional[datetime] = Field(description="Last document analysis date")
    needs_support: bool = Field(description="True if declining or stagnant")
    is_top_performer: bool = Field(description="True if highest growth")


class EducatorAnalytics(BaseModel):
    """Aggregate analytics for educator's entire class"""
    total_students: int
    average_grade_level: Optional[float] = Field(description="Average vocabulary grade across all students")
    grade_distribution: GradeDistribution
    average_adoption_rate: float = Field(description="Class average adoption rate (0-1)")
    total_documents_analyzed: int
    students: List[StudentSummary] = Field(description="All students with their metrics")
    top_performers: List[StudentSummary] = Field(description="Students with highest growth (top 3)")
    needs_support: List[StudentSummary] = Field(description="Students declining or stagnant")


@router.get("/analytics", response_model=EducatorAnalytics)
async def get_educator_analytics(
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get aggregate analytics across all educator's students

    This endpoint:
    1. Verifies JWT token and gets educator from email
    2. Retrieves all students for educator
    3. Calculates aggregate metrics:
       - Total students, average grade level
       - Grade distribution (below/at/above grade)
       - Average adoption rate
       - Total documents analyzed
       - Top performers (highest growth)
       - Students needing support (declining/stagnant)

    Protected endpoint - requires valid JWT token in Authorization header.

    Args:
        user: Current authenticated user from JWT
        session: Database session

    Returns:
        EducatorAnalytics: Aggregate class-level analytics

    Raises:
        HTTPException 401: If authentication fails
        HTTPException 404: If educator not found
    """
    # Get educator from JWT email
    email = user["email"]
    educator = get_educator_by_email(session, email)

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator profile not found. Please complete registration.",
        )

    # Get all students for this educator
    statement = select(Student).where(Student.educator_id == educator.id)
    students = session.exec(statement).all()

    total_students = len(students)

    if total_students == 0:
        # Return empty analytics if no students
        return EducatorAnalytics(
            total_students=0,
            average_grade_level=None,
            grade_distribution=GradeDistribution(
                below_grade=0,
                at_grade=0,
                above_grade=0,
            ),
            average_adoption_rate=0.0,
            total_documents_analyzed=0,
            students=[],
            top_performers=[],
            needs_support=[],
        )

    # Collect student summaries and metrics
    student_summaries: List[StudentSummary] = []
    total_grade_levels = 0.0
    grade_level_count = 0
    total_adoption_rate = 0.0
    adoption_rate_count = 0
    total_documents = 0
    below_grade_count = 0
    at_grade_count = 0
    above_grade_count = 0

    for student in students:
        # Get vocabulary history for this student
        history_statement = (
            select(VocabularyHistory)
            .where(VocabularyHistory.student_id == student.id)
            .order_by(VocabularyHistory.analyzed_at)
        )
        history_records = session.exec(history_statement).all()

        # Calculate progress metrics
        current_grade_level = None
        progress_trend = "stable"
        grade_level_change = 0.0
        last_activity = None

        if history_records:
            total_documents += len(history_records)
            last_activity = history_records[-1].analyzed_at

            if len(history_records) >= 2:
                # Calculate trend
                first_grade = history_records[0].average_grade_level or 0.0
                last_grade = history_records[-1].average_grade_level or 0.0
                current_grade_level = last_grade
                grade_level_change = last_grade - first_grade

                # Determine trend
                if grade_level_change > 0.2:
                    progress_trend = "improving"
                elif grade_level_change < -0.2:
                    progress_trend = "declining"
                else:
                    progress_trend = "stable"
            elif len(history_records) == 1:
                current_grade_level = history_records[0].average_grade_level

        # Calculate adoption rate
        recommendations_statement = select(Recommendation).where(
            Recommendation.student_id == student.id
        )
        recommendations = session.exec(recommendations_statement).all()

        total_recommendations = len(recommendations)
        adopted_recommendations = len([r for r in recommendations if r.status == RecommendationStatus.ADOPTED])
        adoption_rate = adopted_recommendations / total_recommendations if total_recommendations > 0 else 0.0

        # Update aggregates
        if current_grade_level is not None:
            total_grade_levels += current_grade_level
            grade_level_count += 1

            # Grade distribution
            grade_diff = current_grade_level - student.grade_level
            if grade_diff < -0.5:
                below_grade_count += 1
            elif grade_diff > 0.5:
                above_grade_count += 1
            else:
                at_grade_count += 1

        if total_recommendations > 0:
            total_adoption_rate += adoption_rate
            adoption_rate_count += 1

        # Determine if needs support or is top performer (will sort later)
        needs_support = progress_trend == "declining" or (progress_trend == "stable" and len(history_records) >= 3)

        student_summaries.append(StudentSummary(
            student_id=student.id,
            name=student.name,
            current_grade_level=current_grade_level,
            actual_grade=student.grade_level,
            progress_trend=progress_trend,
            grade_level_change=round(grade_level_change, 2),
            adoption_rate=round(adoption_rate, 2),
            total_recommendations=total_recommendations,
            adopted_recommendations=adopted_recommendations,
            last_activity=last_activity,
            needs_support=needs_support,
            is_top_performer=False,  # Will set after sorting
        ))

    # Calculate averages
    average_grade_level = round(total_grade_levels / grade_level_count, 2) if grade_level_count > 0 else None
    average_adoption_rate = round(total_adoption_rate / adoption_rate_count, 2) if adoption_rate_count > 0 else 0.0

    # Identify top performers (top 3 by grade_level_change, must be improving)
    improving_students = [s for s in student_summaries if s.progress_trend == "improving"]
    improving_students.sort(key=lambda s: s.grade_level_change, reverse=True)
    top_performers = improving_students[:3]
    for performer in top_performers:
        performer.is_top_performer = True

    # Identify students needing support
    needs_support_students = [s for s in student_summaries if s.needs_support]
    needs_support_students.sort(key=lambda s: s.grade_level_change)  # Lowest change first

    return EducatorAnalytics(
        total_students=total_students,
        average_grade_level=average_grade_level,
        grade_distribution=GradeDistribution(
            below_grade=below_grade_count,
            at_grade=at_grade_count,
            above_grade=above_grade_count,
        ),
        average_adoption_rate=average_adoption_rate,
        total_documents_analyzed=total_documents,
        students=student_summaries,
        top_performers=top_performers,
        needs_support=needs_support_students,
    )
