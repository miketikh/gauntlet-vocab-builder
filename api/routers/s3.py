"""
S3 Router
Endpoints for document upload/download via presigned URLs
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from dependencies.auth import get_current_user
from services.database import get_session
from services.s3 import (
    generate_document_key,
    generate_presigned_upload_url,
    generate_presigned_download_url,
    verify_bucket_exists
)
from models.database import Student, Educator

router = APIRouter()


# Request/Response Models
class UploadUrlRequest(BaseModel):
    """Request to generate a presigned upload URL"""
    student_id: int = Field(..., description="ID of the student the document belongs to")
    filename: str = Field(..., description="Original filename", min_length=1, max_length=255)
    content_type: str = Field(..., description="MIME type (e.g., application/pdf, text/plain)")

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": 5,
                "filename": "essay.pdf",
                "content_type": "application/pdf"
            }
        }


class UploadUrlResponse(BaseModel):
    """Response containing presigned upload URL"""
    presigned_url: str = Field(..., description="Presigned URL for uploading the file via PUT request")
    s3_key: str = Field(..., description="S3 object key - save this to document metadata")
    expires_in: int = Field(..., description="URL expiration time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "presigned_url": "https://bucket.s3.amazonaws.com/path?signature=...",
                "s3_key": "educators/1/students/5/documents/uuid-essay.pdf",
                "expires_in": 3600
            }
        }


class DownloadUrlRequest(BaseModel):
    """Request to generate a presigned download URL"""
    s3_key: str = Field(..., description="S3 object key from document metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "s3_key": "educators/1/students/5/documents/uuid-essay.pdf"
            }
        }


class DownloadUrlResponse(BaseModel):
    """Response containing presigned download URL"""
    presigned_url: str = Field(..., description="Presigned URL for downloading the file via GET request")
    expires_in: int = Field(..., description="URL expiration time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "presigned_url": "https://bucket.s3.amazonaws.com/path?signature=...",
                "expires_in": 3600
            }
        }


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
    # Get student
    statement = select(Student).where(Student.id == student_id)
    student = session.exec(statement).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )

    # Check ownership
    if student.educator_id != educator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this student's documents"
        )

    return student


@router.post("/upload-url", response_model=UploadUrlResponse)
async def get_upload_url(
    request: UploadUrlRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Generate a presigned URL for uploading a document to S3

    This endpoint:
    1. Verifies the educator owns the student
    2. Generates a unique S3 key for the document
    3. Creates a presigned URL for direct browser upload
    4. Returns the URL and S3 key (save the key in document metadata)

    The frontend should:
    1. Call this endpoint to get presigned URL and S3 key
    2. Upload file directly to S3 using PUT request with presigned URL
    3. Create document record in database with the returned S3 key

    Protected endpoint - requires valid JWT token.

    Args:
        request: Upload URL request with student_id, filename, content_type
        user: Current authenticated user (injected by dependency)
        session: Database session (injected by dependency)

    Returns:
        UploadUrlResponse: Presigned URL and S3 key

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If educator doesn't own the student
        HTTPException 404: If student not found
        HTTPException 500: If S3 configuration error
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
    student = verify_educator_owns_student(
        educator_id=educator.id,
        student_id=request.student_id,
        session=session
    )

    # Generate S3 key
    s3_key = generate_document_key(
        educator_id=educator.id,
        student_id=student.id,
        filename=request.filename
    )

    # Generate presigned upload URL (1 hour expiration)
    expires_in = 3600
    presigned_url = generate_presigned_upload_url(
        key=s3_key,
        content_type=request.content_type,
        expires_in=expires_in
    )

    return UploadUrlResponse(
        presigned_url=presigned_url,
        s3_key=s3_key,
        expires_in=expires_in
    )


@router.post("/download-url", response_model=DownloadUrlResponse)
async def get_download_url(
    request: DownloadUrlRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Generate a presigned URL for downloading a document from S3

    This endpoint:
    1. Extracts educator and student IDs from the S3 key
    2. Verifies the educator owns the student
    3. Generates a presigned URL for downloading the file

    Protected endpoint - requires valid JWT token.

    Args:
        request: Download URL request with S3 key
        user: Current authenticated user (injected by dependency)
        session: Database session (injected by dependency)

    Returns:
        DownloadUrlResponse: Presigned URL for download

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If educator doesn't own the document
        HTTPException 404: If educator or student not found
        HTTPException 400: If S3 key format is invalid
        HTTPException 500: If S3 configuration error
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

    # Parse S3 key to extract educator_id and student_id
    # Expected format: educators/{educator_id}/students/{student_id}/documents/{uuid}-{filename}
    try:
        key_parts = request.s3_key.split('/')
        if len(key_parts) < 6 or key_parts[0] != 'educators' or key_parts[2] != 'students':
            raise ValueError("Invalid S3 key format")

        key_educator_id = int(key_parts[1])
        key_student_id = int(key_parts[3])

    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid S3 key format. Expected: educators/{id}/students/{id}/documents/{file}"
        )

    # Verify the S3 key belongs to the current educator
    if key_educator_id != educator.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this document"
        )

    # Verify educator owns the student
    verify_educator_owns_student(
        educator_id=educator.id,
        student_id=key_student_id,
        session=session
    )

    # Generate presigned download URL (1 hour expiration)
    expires_in = 3600
    presigned_url = generate_presigned_download_url(
        key=request.s3_key,
        expires_in=expires_in
    )

    return DownloadUrlResponse(
        presigned_url=presigned_url,
        expires_in=expires_in
    )


@router.get("/health")
async def s3_health_check():
    """
    S3 health check endpoint

    Verifies that:
    - S3 credentials are configured
    - S3 bucket exists and is accessible

    Returns:
        dict: Health status

    Raises:
        HTTPException 500: If S3 is not properly configured
    """
    try:
        bucket_exists = verify_bucket_exists()
        return {
            "status": "healthy",
            "service": "s3",
            "bucket_accessible": bucket_exists
        }
    except HTTPException as e:
        return {
            "status": "unhealthy",
            "service": "s3",
            "error": e.detail
        }
