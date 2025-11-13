"""
Documents Router
Endpoints for managing document metadata after S3 upload
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from dependencies.auth import get_current_user
from services.database import get_session
from services import s3
from models.database import (
    Document,
    DocumentCreate,
    DocumentPublic,
    DocumentUpdate,
    DocumentStatus,
    FileType,
    Student,
    Educator
)

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
