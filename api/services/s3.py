"""
AWS S3 Service
Utilities for document storage in S3 using presigned URLs
"""
import os
import uuid
from typing import Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException, status


# Initialize S3 client
def get_s3_client():
    """
    Get configured boto3 S3 client

    Returns:
        boto3.client: Configured S3 client

    Raises:
        HTTPException 500: If AWS credentials are not configured
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        return s3_client
    except NoCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AWS credentials not configured. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
        )


def get_bucket_name() -> str:
    """
    Get S3 bucket name from environment variables

    Returns:
        str: S3 bucket name

    Raises:
        HTTPException 500: If bucket name is not configured
    """
    bucket_name = os.getenv('AWS_S3_BUCKET')
    if not bucket_name:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AWS S3 bucket not configured. Please set AWS_S3_BUCKET environment variable."
        )
    return bucket_name


def generate_document_key(educator_id: int, student_id: int, filename: str) -> str:
    """
    Generate a unique S3 key for document storage

    Uses hierarchical organization:
    educators/{educator_id}/students/{student_id}/documents/{uuid}-{filename}

    This structure:
    - Organizes files by educator and student
    - Prevents name collisions with UUID prefix
    - Makes cleanup easier (delete all files for a student)
    - Supports S3 lifecycle policies per prefix

    Args:
        educator_id: ID of the educator who owns the student
        student_id: ID of the student the document belongs to
        filename: Original filename (will be sanitized)

    Returns:
        str: S3 object key

    Example:
        >>> generate_document_key(1, 5, "essay.pdf")
        "educators/1/students/5/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890-essay.pdf"
    """
    # Generate unique ID to prevent collisions
    unique_id = str(uuid.uuid4())

    # Sanitize filename (remove spaces, special chars)
    safe_filename = filename.replace(" ", "_").replace("/", "_")

    # Build hierarchical key
    key = f"educators/{educator_id}/students/{student_id}/documents/{unique_id}-{safe_filename}"

    return key


def generate_presigned_upload_url(
    key: str,
    content_type: str,
    expires_in: int = 3600
) -> str:
    """
    Generate a presigned URL for uploading a file to S3

    Presigned URLs allow direct browser-to-S3 uploads without routing
    through the API server, which is more efficient and scalable.

    Args:
        key: S3 object key (path) for the file
        content_type: MIME type of the file (e.g., "application/pdf")
        expires_in: URL expiration time in seconds (default 1 hour)

    Returns:
        str: Presigned upload URL

    Raises:
        HTTPException 500: If S3 credentials are invalid or bucket doesn't exist
        HTTPException 503: If network/connection error occurs

    Example:
        >>> url = generate_presigned_upload_url(
        ...     "educators/1/students/5/documents/uuid-essay.pdf",
        ...     "application/pdf"
        ... )
        >>> # Frontend can now PUT directly to this URL
    """
    s3_client = get_s3_client()
    bucket_name = get_bucket_name()

    try:
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': key,
                'ContentType': content_type,
            },
            ExpiresIn=expires_in,
            HttpMethod='PUT'
        )
        return presigned_url

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')

        if error_code == 'NoSuchBucket':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"S3 bucket '{bucket_name}' does not exist. Please create it first."
            )
        elif error_code == 'AccessDenied':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to S3 bucket. Check IAM permissions."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate upload URL: {str(e)}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"S3 service unavailable: {str(e)}"
        )


def generate_presigned_download_url(
    key: str,
    expires_in: int = 3600
) -> str:
    """
    Generate a presigned URL for downloading a file from S3

    Args:
        key: S3 object key (path) for the file
        expires_in: URL expiration time in seconds (default 1 hour)

    Returns:
        str: Presigned download URL

    Raises:
        HTTPException 500: If S3 credentials are invalid or bucket doesn't exist
        HTTPException 404: If object doesn't exist
        HTTPException 503: If network/connection error occurs
    """
    s3_client = get_s3_client()
    bucket_name = get_bucket_name()

    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key,
            },
            ExpiresIn=expires_in,
            HttpMethod='GET'
        )
        return presigned_url

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')

        if error_code == 'NoSuchKey':
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found in S3: {key}"
            )
        elif error_code == 'NoSuchBucket':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"S3 bucket '{bucket_name}' does not exist."
            )
        elif error_code == 'AccessDenied':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to S3 object. Check IAM permissions."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate download URL: {str(e)}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"S3 service unavailable: {str(e)}"
        )


def delete_file(key: str) -> bool:
    """
    Delete a file from S3

    Args:
        key: S3 object key (path) for the file to delete

    Returns:
        bool: True if deletion successful

    Raises:
        HTTPException 500: If S3 credentials are invalid or bucket doesn't exist
        HTTPException 403: If access denied
        HTTPException 503: If network/connection error occurs

    Note:
        S3 delete operations are idempotent - deleting a non-existent
        object returns success.
    """
    s3_client = get_s3_client()
    bucket_name = get_bucket_name()

    try:
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=key
        )
        return True

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')

        if error_code == 'NoSuchBucket':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"S3 bucket '{bucket_name}' does not exist."
            )
        elif error_code == 'AccessDenied':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to delete S3 object. Check IAM permissions."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"S3 service unavailable: {str(e)}"
        )


def list_files(prefix: str, max_keys: int = 1000) -> list:
    """
    List files in S3 by prefix

    Useful for listing all documents for a student or educator.

    Args:
        prefix: S3 key prefix to filter by (e.g., "educators/1/students/5/")
        max_keys: Maximum number of keys to return (default 1000)

    Returns:
        list: List of dictionaries containing file metadata:
            - key: S3 object key
            - size: File size in bytes
            - last_modified: Last modified timestamp

    Raises:
        HTTPException 500: If S3 credentials are invalid or bucket doesn't exist
        HTTPException 503: If network/connection error occurs

    Example:
        >>> files = list_files("educators/1/students/5/documents/")
        >>> for file in files:
        ...     print(f"{file['key']}: {file['size']} bytes")
    """
    s3_client = get_s3_client()
    bucket_name = get_bucket_name()

    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            MaxKeys=max_keys
        )

        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                })

        return files

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')

        if error_code == 'NoSuchBucket':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"S3 bucket '{bucket_name}' does not exist."
            )
        elif error_code == 'AccessDenied':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to list S3 objects. Check IAM permissions."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list files: {str(e)}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"S3 service unavailable: {str(e)}"
        )


def verify_bucket_exists() -> bool:
    """
    Verify that the configured S3 bucket exists and is accessible

    Useful for health checks and startup validation.

    Returns:
        bool: True if bucket exists and is accessible

    Raises:
        HTTPException 500: If bucket doesn't exist or credentials are invalid
        HTTPException 403: If access denied
    """
    s3_client = get_s3_client()
    bucket_name = get_bucket_name()

    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')

        if error_code == '404':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"S3 bucket '{bucket_name}' does not exist. Please create it first."
            )
        elif error_code == '403':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to S3 bucket '{bucket_name}'. Check IAM permissions."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to verify bucket: {str(e)}"
            )
