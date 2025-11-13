"""
Database service for Vocab Builder API.

This module provides helper functions for database operations using the Supabase Python client.
The database schema is managed via Drizzle ORM (TypeScript), but queries are executed in Python.

Note: This file uses raw SQL queries and the Supabase client. For schema changes,
use the Drizzle ORM schema file: /api/drizzle/schema.ts
"""

import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Validate required environment variables
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is not set")
if not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("SUPABASE_SERVICE_ROLE_KEY environment variable is not set")


def get_supabase_client() -> Client:
    """
    Initialize and return a Supabase client with service role access.

    The service role key bypasses RLS policies, allowing the backend to:
    - Perform administrative operations
    - Access data across all educators (when needed for analysis)
    - Write to reference tables (like grade_words)

    Returns:
        Client: Initialized Supabase client
    """
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


# Initialize a singleton client for reuse
supabase: Client = get_supabase_client()


# ============================================================================
# Educator Operations
# ============================================================================

async def get_educator_by_id(educator_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch educator profile by ID.

    Args:
        educator_id: UUID of the educator

    Returns:
        Educator data dict or None if not found
    """
    response = supabase.table("educators").select("*").eq("id", educator_id).execute()
    return response.data[0] if response.data else None


async def get_educator_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Fetch educator profile by email.

    Args:
        email: Email address of the educator

    Returns:
        Educator data dict or None if not found
    """
    response = supabase.table("educators").select("*").eq("email", email).execute()
    return response.data[0] if response.data else None


async def create_educator(
    user_id: str,
    email: str,
    name: str,
    school: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new educator profile (typically called after Supabase Auth signup).

    Args:
        user_id: UUID from Supabase Auth (auth.uid())
        email: Educator's email address
        name: Educator's full name
        school: Optional school name

    Returns:
        Created educator data dict
    """
    data = {
        "id": user_id,
        "email": email,
        "name": name,
        "school": school
    }

    response = supabase.table("educators").insert(data).execute()
    return response.data[0] if response.data else None


# ============================================================================
# Student Operations
# ============================================================================

async def get_students_by_educator(educator_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all students for a given educator.

    Args:
        educator_id: UUID of the educator

    Returns:
        List of student data dicts, ordered by creation date (newest first)
    """
    response = (
        supabase.table("students")
        .select("*")
        .eq("educator_id", educator_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


async def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single student by ID.

    Args:
        student_id: UUID of the student

    Returns:
        Student data dict or None if not found
    """
    response = supabase.table("students").select("*").eq("id", student_id).execute()
    return response.data[0] if response.data else None


async def create_student(
    educator_id: str,
    name: str,
    grade_level: int,
    reading_level: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new student profile.

    Args:
        educator_id: UUID of the educator who owns this student
        name: Student's name
        grade_level: Grade level (6-12)
        reading_level: Optional reading level description
        notes: Optional notes about the student

    Returns:
        Created student data dict

    Raises:
        ValueError: If grade_level is not between 6 and 12
    """
    if not (6 <= grade_level <= 12):
        raise ValueError("grade_level must be between 6 and 12")

    data = {
        "educator_id": educator_id,
        "name": name,
        "grade_level": grade_level,
        "reading_level": reading_level,
        "notes": notes
    }

    response = supabase.table("students").insert(data).execute()
    return response.data[0] if response.data else None


async def update_student(
    student_id: str,
    **updates
) -> Optional[Dict[str, Any]]:
    """
    Update student fields.

    Args:
        student_id: UUID of the student
        **updates: Fields to update (name, grade_level, reading_level, notes)

    Returns:
        Updated student data dict or None if not found
    """
    response = (
        supabase.table("students")
        .update(updates)
        .eq("id", student_id)
        .execute()
    )
    return response.data[0] if response.data else None


# ============================================================================
# Document Operations
# ============================================================================

async def get_documents_by_student(student_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all documents for a given student.

    Args:
        student_id: UUID of the student

    Returns:
        List of document data dicts, ordered by upload date (newest first)
    """
    response = (
        supabase.table("documents")
        .select("*")
        .eq("student_id", student_id)
        .order("upload_date", desc=True)
        .execute()
    )
    return response.data


async def get_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single document by ID.

    Args:
        document_id: UUID of the document

    Returns:
        Document data dict or None if not found
    """
    response = supabase.table("documents").select("*").eq("id", document_id).execute()
    return response.data[0] if response.data else None


async def create_document(
    student_id: str,
    title: str,
    s3_key: str,
    file_type: str,
    status: str = "pending"
) -> Dict[str, Any]:
    """
    Create a new document record.

    Args:
        student_id: UUID of the student who owns this document
        title: Document title
        s3_key: S3 object key for retrieving the file
        file_type: File type (e.g., 'pdf', 'docx', 'txt')
        status: Processing status ('pending', 'processing', 'completed', 'failed')

    Returns:
        Created document data dict

    Raises:
        ValueError: If status is not a valid value
    """
    valid_statuses = ['pending', 'processing', 'completed', 'failed']
    if status not in valid_statuses:
        raise ValueError(f"status must be one of: {', '.join(valid_statuses)}")

    data = {
        "student_id": student_id,
        "title": title,
        "s3_key": s3_key,
        "file_type": file_type,
        "status": status
    }

    response = supabase.table("documents").insert(data).execute()
    return response.data[0] if response.data else None


async def update_document_status(document_id: str, status: str) -> Optional[Dict[str, Any]]:
    """
    Update the processing status of a document.

    Args:
        document_id: UUID of the document
        status: New status ('pending', 'processing', 'completed', 'failed')

    Returns:
        Updated document data dict or None if not found

    Raises:
        ValueError: If status is not a valid value
    """
    valid_statuses = ['pending', 'processing', 'completed', 'failed']
    if status not in valid_statuses:
        raise ValueError(f"status must be one of: {', '.join(valid_statuses)}")

    response = (
        supabase.table("documents")
        .update({"status": status})
        .eq("id", document_id)
        .execute()
    )
    return response.data[0] if response.data else None


# ============================================================================
# Grade Words Operations
# ============================================================================

async def get_grade_words(
    grade_level: int,
    subject: str = "ELA",
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Fetch vocabulary words for a specific grade level.

    Args:
        grade_level: Grade level (6-12)
        subject: Subject area (default: 'ELA')
        limit: Optional limit on number of words to return

    Returns:
        List of word data dicts, ordered by frequency rank (most common first)

    Raises:
        ValueError: If grade_level is not between 6 and 12
    """
    if not (6 <= grade_level <= 12):
        raise ValueError("grade_level must be between 6 and 12")

    query = (
        supabase.table("grade_words")
        .select("*")
        .eq("grade_level", grade_level)
        .eq("subject", subject)
        .order("frequency_rank", desc=False)
    )

    if limit:
        query = query.limit(limit)

    response = query.execute()
    return response.data


async def add_grade_word(
    grade_level: int,
    word: str,
    definition: str,
    example: Optional[str] = None,
    frequency_rank: Optional[int] = None,
    subject: str = "ELA"
) -> Dict[str, Any]:
    """
    Add a new vocabulary word to the grade words reference table.

    Args:
        grade_level: Grade level (6-12)
        word: The vocabulary word
        definition: Definition of the word
        example: Optional example sentence
        frequency_rank: Optional frequency ranking (lower = more common)
        subject: Subject area (default: 'ELA')

    Returns:
        Created word data dict

    Raises:
        ValueError: If grade_level is not between 6 and 12
    """
    if not (6 <= grade_level <= 12):
        raise ValueError("grade_level must be between 6 and 12")

    data = {
        "grade_level": grade_level,
        "word": word,
        "definition": definition,
        "example": example,
        "frequency_rank": frequency_rank,
        "subject": subject
    }

    response = supabase.table("grade_words").insert(data).execute()
    return response.data[0] if response.data else None


# ============================================================================
# Health Check Function
# ============================================================================

def check_connection() -> bool:
    """
    Verify Supabase connection by attempting a simple query.

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        # Try to query the educators table (should work even if empty)
        supabase.table("educators").select("count", count="exact").limit(1).execute()
        return True
    except Exception as e:
        print(f"Supabase connection check failed: {e}")
        return False
