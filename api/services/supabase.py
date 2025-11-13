"""
Supabase client initialization and utility functions.

This module provides:
- Supabase client setup using environment variables
- Helper functions for common database operations
- Service role access for backend operations
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
# Helper Functions for Common Operations
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


async def get_students_by_educator(educator_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all students for a given educator.

    Args:
        educator_id: UUID of the educator

    Returns:
        List of student data dicts
    """
    response = (
        supabase.table("students")
        .select("*")
        .eq("educator_id", educator_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


async def get_documents_by_student(student_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all documents for a given student.

    Args:
        student_id: UUID of the student

    Returns:
        List of document data dicts
    """
    response = (
        supabase.table("documents")
        .select("*")
        .eq("student_id", student_id)
        .order("upload_date", desc=True)
        .execute()
    )
    return response.data


async def get_grade_words(grade_level: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Fetch vocabulary words for a specific grade level.

    Args:
        grade_level: Grade level (6-12)
        limit: Optional limit on number of words to return

    Returns:
        List of word data dicts, ordered by frequency rank
    """
    query = (
        supabase.table("grade_words")
        .select("*")
        .eq("grade_level", grade_level)
        .order("frequency_rank", desc=False)
    )

    if limit:
        query = query.limit(limit)

    response = query.execute()
    return response.data


async def update_document_status(document_id: str, status: str) -> Dict[str, Any]:
    """
    Update the processing status of a document.

    Args:
        document_id: UUID of the document
        status: New status ('pending', 'processing', 'completed', 'failed')

    Returns:
        Updated document data dict
    """
    response = (
        supabase.table("documents")
        .update({"status": status})
        .eq("id", document_id)
        .execute()
    )
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
