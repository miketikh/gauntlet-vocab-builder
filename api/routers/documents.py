"""
Documents Router
Endpoints for managing document metadata after S3 upload
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from dependencies.auth import get_current_user
from services.database import get_session
from services import s3
from services.text_extraction import extract_text_from_file, TextExtractionError, UnsupportedFileTypeError
from services.word_processing import extract_words_from_text, WordProcessingError
from services.vocabulary_analysis import analyze_vocabulary, VocabularyAnalysisError
from models.database import (
    Document,
    DocumentCreate,
    DocumentPublic,
    DocumentUpdate,
    DocumentStatus,
    FileType,
    Student,
    Educator,
    AnalysisResult,
    AnalysisResultPublic,
    VocabularyHistory,
)
from models.analysis import VocabularyProfile

logger = logging.getLogger(__name__)

router = APIRouter()


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
            detail="You do not have permission to access this student's documents"
        )

    return student


def verify_educator_owns_document(
    educator_id: int,
    document_id: int,
    session: Session
) -> Document:
    """
    Verify that the educator owns the specified document

    Args:
        educator_id: ID of the educator
        document_id: ID of the document
        session: Database session

    Returns:
        Document: The document record if ownership verified

    Raises:
        HTTPException 404: If document not found
        HTTPException 403: If educator doesn't own the document
    """
    statement = select(Document).where(Document.id == document_id)
    document = session.exec(statement).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )

    # Check if educator owns the student that owns this document
    student_statement = select(Student).where(Student.id == document.student_id)
    student = session.exec(student_statement).first()

    if not student or student.educator_id != educator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this document"
        )

    return document


@router.post("", response_model=DocumentPublic, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create document metadata after S3 upload

    This endpoint should be called AFTER successfully uploading a file to S3.
    It creates a database record linking the document to a student.

    Workflow:
    1. Frontend gets presigned URL from /api/s3/upload-url
    2. Frontend uploads file directly to S3 using presigned URL
    3. Frontend calls this endpoint to save document metadata
    4. Document status starts as 'pending' (analysis happens later)

    Protected endpoint - requires valid JWT token.

    Args:
        document: Document metadata (student_id, title, s3_key, file_type, subject)
        user: Current authenticated user (injected by dependency)
        session: Database session (injected by dependency)

    Returns:
        DocumentPublic: Created document with metadata

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If educator doesn't own the student
        HTTPException 404: If student not found
    """
    # Get educator from session
    educator_email = user["email"]
    educator_statement = select(Educator).where(Educator.email == educator_email)
    educator = session.exec(educator_statement).first()

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator not found. Please complete authentication setup."
        )

    # Verify educator owns the student
    verify_educator_owns_student(
        educator_id=educator.id,
        student_id=document.student_id,
        session=session
    )

    # Create document record
    db_document = Document(
        student_id=document.student_id,
        title=document.title,
        s3_key=document.s3_key,
        file_type=document.file_type,
        subject=document.subject,
        status=DocumentStatus.PENDING,
        upload_date=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(db_document)
    session.commit()
    session.refresh(db_document)

    return db_document


@router.get("/students/{student_id}/documents", response_model=List[DocumentPublic])
async def list_student_documents(
    student_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all documents for a specific student

    Returns documents sorted by upload date (newest first).

    Protected endpoint - requires valid JWT token.

    Args:
        student_id: ID of the student
        user: Current authenticated user (injected by dependency)
        session: Database session (injected by dependency)

    Returns:
        List[DocumentPublic]: List of documents for the student

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If educator doesn't own the student
        HTTPException 404: If student not found
    """
    # Get educator from session
    educator_email = user["email"]
    educator_statement = select(Educator).where(Educator.email == educator_email)
    educator = session.exec(educator_statement).first()

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator not found. Please complete authentication setup."
        )

    # Verify educator owns the student
    verify_educator_owns_student(
        educator_id=educator.id,
        student_id=student_id,
        session=session
    )

    # Get all documents for the student, sorted by upload date (newest first)
    statement = (
        select(Document)
        .where(Document.student_id == student_id)
        .order_by(Document.upload_date.desc())
    )
    documents = session.exec(statement).all()

    return documents


@router.get("/{document_id}", response_model=DocumentPublic)
async def get_document(
    document_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a single document by ID

    Protected endpoint - requires valid JWT token.

    Args:
        document_id: ID of the document
        user: Current authenticated user (injected by dependency)
        session: Database session (injected by dependency)

    Returns:
        DocumentPublic: Document metadata

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If educator doesn't own the document
        HTTPException 404: If document not found
    """
    # Get educator from session
    educator_email = user["email"]
    educator_statement = select(Educator).where(Educator.email == educator_email)
    educator = session.exec(educator_statement).first()

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator not found. Please complete authentication setup."
        )

    # Verify educator owns the document
    document = verify_educator_owns_document(
        educator_id=educator.id,
        document_id=document_id,
        session=session
    )

    return document


class DocumentStatusUpdate(BaseModel):
    """Request to update document status"""
    status: DocumentStatus = Field(..., description="New document status")
    error_message: Optional[str] = Field(default=None, description="Error message if status is FAILED")


@router.patch("/{document_id}/status", response_model=DocumentPublic)
async def update_document_status(
    document_id: int,
    status_update: DocumentStatusUpdate,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update document processing status

    Used by background processing workers to update document status
    as it moves through the analysis pipeline:
    - PENDING -> PROCESSING (when analysis starts)
    - PROCESSING -> COMPLETED (when analysis finishes)
    - PROCESSING -> FAILED (if analysis fails)

    Protected endpoint - requires valid JWT token.

    Args:
        document_id: ID of the document
        status_update: New status and optional error message
        user: Current authenticated user (injected by dependency)
        session: Database session (injected by dependency)

    Returns:
        DocumentPublic: Updated document metadata

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If educator doesn't own the document
        HTTPException 404: If document not found
    """
    # Get educator from session
    educator_email = user["email"]
    educator_statement = select(Educator).where(Educator.email == educator_email)
    educator = session.exec(educator_statement).first()

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator not found. Please complete authentication setup."
        )

    # Verify educator owns the document
    document = verify_educator_owns_document(
        educator_id=educator.id,
        document_id=document_id,
        session=session
    )

    # Update status
    document.status = status_update.status
    if status_update.error_message:
        document.error_message = status_update.error_message
    document.updated_at = datetime.utcnow()

    session.add(document)
    session.commit()
    session.refresh(document)

    return document


class DeleteResponse(BaseModel):
    """Response for document deletion"""
    message: str = Field(..., description="Success message")
    document_id: int = Field(..., description="ID of deleted document")


@router.delete("/{document_id}", response_model=DeleteResponse)
async def delete_document(
    document_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a document and its associated S3 file

    This endpoint:
    1. Verifies the educator owns the document (via student)
    2. Deletes the file from S3
    3. Deletes the database record
    4. Returns a success message

    Protected endpoint - requires valid JWT token.

    Args:
        document_id: ID of the document to delete
        user: Current authenticated user (injected by dependency)
        session: Database session (injected by dependency)

    Returns:
        DeleteResponse: Success message with document ID

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If educator doesn't own the document
        HTTPException 404: If document not found
        HTTPException 500: If S3 deletion fails
    """
    # Get educator from session
    educator_email = user["email"]
    educator_statement = select(Educator).where(Educator.email == educator_email)
    educator = session.exec(educator_statement).first()

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator not found. Please complete authentication setup."
        )

    # Verify educator owns the document
    document = verify_educator_owns_document(
        educator_id=educator.id,
        document_id=document_id,
        session=session
    )

    # Delete file from S3
    # Note: S3 delete is idempotent - if file doesn't exist, it still returns success
    try:
        s3.delete_file(document.s3_key)
    except HTTPException as e:
        # If S3 deletion fails, we still want to delete the database record
        # to avoid orphaned records, but we'll log the error
        # In production, you might want to queue this for retry
        print(f"Warning: Failed to delete S3 file {document.s3_key}: {e.detail}")

    # Delete database record
    session.delete(document)
    session.commit()

    return DeleteResponse(
        message=f"Document '{document.title}' deleted successfully",
        document_id=document_id
    )


@router.post("/{document_id}/analyze", response_model=VocabularyProfile)
async def analyze_document(
    document_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Analyze document vocabulary and generate vocabulary profile

    This endpoint performs the full analysis pipeline:
    1. Verifies educator owns the document
    2. Downloads file from S3
    3. Extracts text from the file
    4. Processes and lemmatizes words
    5. Maps words to grade levels
    6. Calculates vocabulary profile
    7. Saves analysis results to database
    8. Updates document status to 'completed'

    The analysis runs synchronously (for MVP). For production, consider
    using a background task queue (Celery, RQ, etc.).

    Protected endpoint - requires valid JWT token.

    Args:
        document_id: ID of the document to analyze
        user: Current authenticated user (injected by dependency)
        session: Database session (injected by dependency)

    Returns:
        VocabularyProfile: Complete vocabulary analysis results

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If educator doesn't own the document
        HTTPException 404: If document not found or student not found
        HTTPException 500: If analysis fails (file download, text extraction, etc.)
    """
    # Get educator from session
    educator_email = user["email"]
    educator_statement = select(Educator).where(Educator.email == educator_email)
    educator = session.exec(educator_statement).first()

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator not found. Please complete authentication setup."
        )

    # Verify educator owns the document
    document = verify_educator_owns_document(
        educator_id=educator.id,
        document_id=document_id,
        session=session
    )

    # Get student information for grade level
    student_statement = select(Student).where(Student.id == document.student_id)
    student = session.exec(student_statement).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found for this document"
        )

    try:
        # Step 1: Update document status to 'processing'
        logger.info(f"Starting analysis for document {document_id}")
        document.status = DocumentStatus.PROCESSING
        document.error_message = None
        document.updated_at = datetime.utcnow()
        session.add(document)
        session.commit()

        # Step 2: Download file from S3
        logger.info(f"Downloading file from S3: {document.s3_key}")
        try:
            download_url = s3.generate_presigned_download_url(document.s3_key)
            response = requests.get(download_url, timeout=60)
            response.raise_for_status()
            file_content = response.content
            logger.info(f"Downloaded {len(file_content)} bytes from S3")
        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to download file from S3: {str(e)}"
            )

        # Step 3: Extract text from file
        logger.info(f"Extracting text from {document.file_type} file")
        try:
            text = extract_text_from_file(
                file_content=file_content,
                file_type=document.file_type.value,
                filename=document.title
            )
            logger.info(f"Extracted {len(text)} characters of text")
        except UnsupportedFileTypeError as e:
            document.status = DocumentStatus.FAILED
            document.error_message = f"Unsupported file type: {str(e)}"
            document.updated_at = datetime.utcnow()
            session.add(document)
            session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except TextExtractionError as e:
            document.status = DocumentStatus.FAILED
            document.error_message = f"Text extraction failed: {str(e)}"
            document.updated_at = datetime.utcnow()
            session.add(document)
            session.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to extract text: {str(e)}"
            )

        # Step 4: Analyze vocabulary
        logger.info(f"Analyzing vocabulary for student grade {student.grade_level}")
        try:
            profile = analyze_vocabulary(
                text=text,
                student_grade_level=student.grade_level,
                session=session
            )
            logger.info(
                f"Analysis complete: {profile.statistics.unique_words} unique words, "
                f"avg grade level: {profile.statistics.average_grade_level}"
            )
        except (WordProcessingError, VocabularyAnalysisError) as e:
            document.status = DocumentStatus.FAILED
            document.error_message = f"Vocabulary analysis failed: {str(e)}"
            document.updated_at = datetime.utcnow()
            session.add(document)
            session.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to analyze vocabulary: {str(e)}"
            )

        # Step 5: Save analysis results to database
        logger.info("Saving analysis results to database")
        analysis_result = AnalysisResult(
            document_id=document.id,
            analyzed_at=datetime.utcnow(),
            student_grade_level=profile.student_grade_level,
            total_words=profile.statistics.total_words,
            unique_words=profile.statistics.unique_words,
            analyzed_words=profile.statistics.analyzed_words,
            unknown_words=profile.statistics.unknown_words,
            unknown_percentage=profile.statistics.unknown_percentage,
            average_grade_level=profile.statistics.average_grade_level,
            below_grade_count=profile.statistics.below_grade_count,
            at_grade_count=profile.statistics.at_grade_count,
            above_grade_count=profile.statistics.above_grade_count,
            grade_distribution=profile.grade_distribution.to_dict(),
            challenging_words=[word.dict() for word in profile.challenging_words],
            word_details=[word.dict() for word in profile.word_details],
            created_at=datetime.utcnow()
        )

        session.add(analysis_result)
        session.flush()  # Flush to get analysis_result.id before commit

        # Step 5.5: Create vocabulary history snapshot
        logger.info("Creating vocabulary history snapshot")
        history_entry = VocabularyHistory(
            student_id=document.student_id,
            document_id=document.id,
            analysis_result_id=analysis_result.id,
            analyzed_at=datetime.utcnow(),
            average_grade_level=profile.statistics.average_grade_level,
            total_words=profile.statistics.total_words,
            unique_words=profile.statistics.unique_words,
            grade_distribution=profile.grade_distribution.to_dict(),
            created_at=datetime.utcnow()
        )
        session.add(history_entry)

        # Step 6: Update document status to 'completed'
        document.status = DocumentStatus.COMPLETED
        document.updated_at = datetime.utcnow()
        session.add(document)

        session.commit()
        session.refresh(analysis_result)

        logger.info(f"Analysis saved with ID {analysis_result.id}, history entry created")

        return profile

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error during analysis: {str(e)}", exc_info=True)
        document.status = DocumentStatus.FAILED
        document.error_message = f"Unexpected error: {str(e)}"
        document.updated_at = datetime.utcnow()
        session.add(document)
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/{document_id}/analysis", response_model=VocabularyProfile)
async def get_document_analysis(
    document_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get saved analysis results for a document

    Returns the most recent vocabulary analysis for the specified document.
    If the document has not been analyzed yet, returns 404.

    Protected endpoint - requires valid JWT token.

    Args:
        document_id: ID of the document
        user: Current authenticated user (injected by dependency)
        session: Database session (injected by dependency)

    Returns:
        VocabularyProfile: Saved vocabulary analysis results

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If educator doesn't own the document
        HTTPException 404: If document not found or not analyzed yet
    """
    # Get educator from session
    educator_email = user["email"]
    educator_statement = select(Educator).where(Educator.email == educator_email)
    educator = session.exec(educator_statement).first()

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educator not found. Please complete authentication setup."
        )

    # Verify educator owns the document
    document = verify_educator_owns_document(
        educator_id=educator.id,
        document_id=document_id,
        session=session
    )

    # Get most recent analysis result for this document
    statement = (
        select(AnalysisResult)
        .where(AnalysisResult.document_id == document_id)
        .order_by(AnalysisResult.analyzed_at.desc())
    )
    analysis = session.exec(statement).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis results found for this document. Run POST /api/documents/{id}/analyze first."
        )

    # Reconstruct VocabularyProfile from database record
    from models.analysis import (
        VocabularyStatistics,
        GradeDistribution,
        WordAnalysisResult
    )

    statistics = VocabularyStatistics(
        total_words=analysis.total_words,
        unique_words=analysis.unique_words,
        analyzed_words=analysis.analyzed_words,
        unknown_words=analysis.unknown_words,
        unknown_percentage=analysis.unknown_percentage,
        average_grade_level=analysis.average_grade_level,
        below_grade_count=analysis.below_grade_count,
        at_grade_count=analysis.at_grade_count,
        above_grade_count=analysis.above_grade_count
    )

    grade_distribution = GradeDistribution.from_dict(analysis.grade_distribution)

    challenging_words = [
        WordAnalysisResult(**word) for word in analysis.challenging_words
    ]

    word_details = [
        WordAnalysisResult(**word) for word in analysis.word_details
    ]

    profile = VocabularyProfile(
        student_grade_level=analysis.student_grade_level,
        statistics=statistics,
        grade_distribution=grade_distribution,
        challenging_words=challenging_words,
        word_details=word_details
    )

    return profile
