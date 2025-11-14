"""
Recommendations Router
Endpoints for generating and managing vocabulary recommendations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
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
    RecommendationStatusUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory job tracking (for simplicity)
# In production, use Redis or database
job_storage: Dict[str, Dict[str, Any]] = {}


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


class BulkGenerateResponse(BaseModel):
    """Response for bulk recommendation generation"""
    job_id: str
    status: str
    message: str
    total_students: int


class JobStatusResponse(BaseModel):
    """Response for job status check"""
    job_id: str
    status: str
    progress: str
    completed: bool
    total_students: int
    processed_students: int
    successful: int
    failed: int
    errors: List[Dict[str, str]] = []
    started_at: datetime
    completed_at: Optional[datetime] = None


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


@router.put("/{recommendation_id}/status", response_model=RecommendationPublic)
async def update_recommendation_status(
    recommendation_id: int,
    status_update: RecommendationStatusUpdate,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Update the status of a recommendation (mark as adopted/not_used)

    This endpoint:
    1. Verifies educator owns the student associated with the recommendation
    2. Updates the recommendation status
    3. Returns updated recommendation

    Protected endpoint - requires valid JWT token.

    Args:
        recommendation_id: Recommendation ID to update
        status_update: New status (pending, adopted, not_used)
        user: Current authenticated user from JWT
        session: Database session

    Returns:
        RecommendationPublic: Updated recommendation

    Raises:
        HTTPException 401: If authentication fails
        HTTPException 403: If educator doesn't own the student
        HTTPException 404: If recommendation not found
    """
    # Get educator from JWT email
    email = user["email"]
    educator = get_educator_by_email(session, email)

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator profile not found",
        )

    # Get recommendation and verify
    recommendation = session.get(Recommendation, recommendation_id)

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation with ID {recommendation_id} not found"
        )

    # Verify educator owns the student
    student = session.get(Student, recommendation.student_id)
    if not student or student.educator_id != educator.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this recommendation"
        )

    # Update status
    recommendation.status = status_update.status
    recommendation.updated_at = datetime.utcnow()

    session.add(recommendation)
    session.commit()
    session.refresh(recommendation)

    logger.info(f"Updated recommendation {recommendation_id} status to {status_update.status}")

    # Return public model
    return RecommendationPublic(
        id=recommendation.id,
        student_id=recommendation.student_id,
        document_id=recommendation.document_id,
        word=recommendation.word,
        recommended_grade_level=recommendation.recommended_grade_level,
        subject=recommendation.subject,
        current_usage=recommendation.current_usage,
        context=recommendation.context,
        example_sentence=recommendation.example_sentence,
        rationale=recommendation.rationale,
        status=recommendation.status,
        recommended_at=recommendation.recommended_at,
    )


# Response model for adoption metrics
class AdoptionMetrics(BaseModel):
    """Metrics about recommendation adoption"""
    student_id: int
    total_recommendations: int
    adopted: int
    pending: int
    not_used: int
    adoption_rate: float


@router.get(
    "/{student_id}/recommendations/metrics",
    response_model=AdoptionMetrics
)
async def get_adoption_metrics(
    student_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get adoption metrics for a student's recommendations

    This endpoint:
    1. Verifies educator owns the student
    2. Calculates adoption statistics
    3. Returns metrics (total, adopted, pending, not_used, adoption_rate)

    Protected endpoint - requires valid JWT token.

    Args:
        student_id: Student ID
        user: Current authenticated user from JWT
        session: Database session

    Returns:
        AdoptionMetrics: Recommendation adoption statistics

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
    student = verify_educator_owns_student(educator.id, student_id, session)

    # Get all recommendations for this student
    statement = select(Recommendation).where(
        Recommendation.student_id == student_id
    )
    recommendations = session.exec(statement).all()

    # Calculate metrics
    total = len(recommendations)
    adopted = sum(1 for r in recommendations if r.status == RecommendationStatus.ADOPTED)
    pending = sum(1 for r in recommendations if r.status == RecommendationStatus.PENDING)
    not_used = sum(1 for r in recommendations if r.status == RecommendationStatus.NOT_USED)

    # Calculate adoption rate (adopted / total, excluding pending if desired)
    # For now, we'll calculate as adopted / (adopted + not_used), ignoring pending
    # If there are no completed recommendations, rate is 0
    completed_recommendations = adopted + not_used
    adoption_rate = (adopted / completed_recommendations) if completed_recommendations > 0 else 0.0

    logger.info(
        f"Adoption metrics for student {student_id}: "
        f"total={total}, adopted={adopted}, pending={pending}, "
        f"not_used={not_used}, rate={adoption_rate:.2f}"
    )

    return AdoptionMetrics(
        student_id=student_id,
        total_recommendations=total,
        adopted=adopted,
        pending=pending,
        not_used=not_used,
        adoption_rate=round(adoption_rate, 2),
    )


# Background task function for bulk generation
async def generate_recommendations_for_all_students(
    job_id: str,
    educator_id: int,
    count: int,
    subject: Optional[str]
):
    """
    Background task to generate recommendations for all students

    Args:
        job_id: Unique job identifier
        educator_id: Educator ID
        count: Number of recommendations per student
        subject: Optional subject filter
    """
    from services.database import SessionLocal

    session = SessionLocal()

    try:
        # Update job status
        job_storage[job_id]["status"] = "running"

        # Get all students for this educator
        statement = select(Student).where(Student.educator_id == educator_id)
        students = session.exec(statement).all()

        total_students = len(students)
        job_storage[job_id]["total_students"] = total_students

        logger.info(f"Starting bulk generation for {total_students} students (job {job_id})")

        successful = 0
        failed = 0
        errors = []

        for idx, student in enumerate(students, 1):
            try:
                logger.info(f"Generating recommendations for student {student.id} ({idx}/{total_students})")

                # Generate recommendations for this student
                # Use the most recent document if available
                doc_statement = select(Student).where(Student.id == student.id)
                student_obj = session.exec(doc_statement).first()

                document_id = None
                if student_obj and student_obj.documents:
                    # Get most recent document
                    sorted_docs = sorted(student_obj.documents, key=lambda d: d.upload_date, reverse=True)
                    if sorted_docs:
                        document_id = sorted_docs[0].id

                # Generate recommendations
                recommendations_data = await generate_recommendations_service(
                    student_id=student.id,
                    document_id=document_id,
                    session=session,
                    count=count,
                    subject=subject,
                )

                if recommendations_data:
                    # Check for duplicates
                    words_to_recommend = [rec["recommended_word"] for rec in recommendations_data]
                    existing_words = check_for_duplicate_recommendations(
                        student.id,
                        words_to_recommend,
                        session
                    )

                    # Store recommendations (skip duplicates)
                    saved_count = 0
                    for rec_data in recommendations_data:
                        word = rec_data["recommended_word"]

                        if word.lower() in existing_words:
                            continue

                        recommendation = Recommendation(
                            student_id=student.id,
                            document_id=document_id,
                            word=word,
                            recommended_grade_level=rec_data.get("recommended_grade", student.grade_level + 1),
                            subject=subject,
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
                        saved_count += 1

                    session.commit()
                    logger.info(f"Saved {saved_count} recommendations for student {student.id}")
                    successful += 1
                else:
                    logger.warning(f"No recommendations generated for student {student.id}")
                    failed += 1
                    errors.append({
                        "student_id": str(student.id),
                        "student_name": student.name,
                        "error": "No recommendations could be generated"
                    })

            except Exception as e:
                logger.error(f"Failed to generate recommendations for student {student.id}: {e}", exc_info=True)
                failed += 1
                errors.append({
                    "student_id": str(student.id),
                    "student_name": student.name,
                    "error": str(e)
                })

            # Update progress
            job_storage[job_id]["processed_students"] = idx
            job_storage[job_id]["successful"] = successful
            job_storage[job_id]["failed"] = failed
            job_storage[job_id]["progress"] = f"{idx}/{total_students} students"

        # Mark job as completed
        job_storage[job_id]["status"] = "completed"
        job_storage[job_id]["completed"] = True
        job_storage[job_id]["completed_at"] = datetime.utcnow()
        job_storage[job_id]["errors"] = errors

        logger.info(
            f"Bulk generation completed (job {job_id}): "
            f"{successful} successful, {failed} failed"
        )

    except Exception as e:
        logger.error(f"Bulk generation job {job_id} failed: {e}", exc_info=True)
        job_storage[job_id]["status"] = "failed"
        job_storage[job_id]["completed"] = True
        job_storage[job_id]["completed_at"] = datetime.utcnow()
        job_storage[job_id]["errors"].append({
            "error": f"Job failed: {str(e)}"
        })

    finally:
        session.close()


@router.post(
    "/educators/recommendations/generate-all",
    response_model=BulkGenerateResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def generate_all_recommendations(
    background_tasks: BackgroundTasks,
    count: int = Query(default=10, ge=1, le=20, description="Number of recommendations per student"),
    subject: Optional[str] = Query(default=None, description="Subject filter"),
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Generate recommendations for all students of the current educator

    This endpoint:
    1. Verifies educator authentication
    2. Starts background job to generate recommendations for all students
    3. Returns job ID for progress tracking

    The generation runs asynchronously - use GET /api/jobs/{job_id} to check progress.

    Protected endpoint - requires valid JWT token.

    Args:
        background_tasks: FastAPI background tasks handler
        count: Number of recommendations to generate per student (default: 10)
        subject: Optional subject filter
        user: Current authenticated user from JWT
        session: Database session

    Returns:
        BulkGenerateResponse: Job information with job_id for tracking

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
            detail="Educator profile not found",
        )

    # Get student count for initial response
    statement = select(Student).where(Student.educator_id == educator.id)
    students = session.exec(statement).all()
    total_students = len(students)

    if total_students == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No students found. Add students before generating recommendations.",
        )

    # Create job ID
    job_id = str(uuid.uuid4())

    # Initialize job tracking
    job_storage[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": "0/0 students",
        "completed": False,
        "total_students": total_students,
        "processed_students": 0,
        "successful": 0,
        "failed": 0,
        "errors": [],
        "started_at": datetime.utcnow(),
        "completed_at": None,
        "educator_id": educator.id,
    }

    # Start background task
    background_tasks.add_task(
        generate_recommendations_for_all_students,
        job_id=job_id,
        educator_id=educator.id,
        count=count,
        subject=subject
    )

    logger.info(
        f"Started bulk recommendation generation for educator {educator.id} "
        f"({total_students} students, job {job_id})"
    )

    return BulkGenerateResponse(
        job_id=job_id,
        status="pending",
        message=f"Bulk recommendation generation started for {total_students} students",
        total_students=total_students,
    )


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse
)
async def get_job_status(
    job_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get status of a bulk recommendation generation job

    This endpoint returns the current progress of a background job.

    Protected endpoint - requires valid JWT token.

    Args:
        job_id: Job identifier returned from generate-all endpoint
        user: Current authenticated user from JWT
        session: Database session

    Returns:
        JobStatusResponse: Current job status and progress

    Raises:
        HTTPException 401: If authentication fails
        HTTPException 404: If job not found
    """
    # Verify user is authenticated
    email = user["email"]
    educator = get_educator_by_email(session, email)

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator profile not found",
        )

    # Check if job exists
    if job_id not in job_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    job = job_storage[job_id]

    # Verify educator owns this job
    if job.get("educator_id") != educator.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this job",
        )

    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        progress=job["progress"],
        completed=job["completed"],
        total_students=job["total_students"],
        processed_students=job["processed_students"],
        successful=job["successful"],
        failed=job["failed"],
        errors=job["errors"],
        started_at=job["started_at"],
        completed_at=job["completed_at"],
    )
