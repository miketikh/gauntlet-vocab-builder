"""
Authentication Router
Endpoints for authentication and user management
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from dependencies.auth import get_current_user
from services.database import get_session
from services.educator import get_or_create_educator
from models.database import EducatorPublic

router = APIRouter()


@router.get("/me", response_model=EducatorPublic)
async def get_current_educator(
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get current authenticated educator information

    This endpoint:
    1. Verifies JWT token (via get_current_user dependency)
    2. Gets or creates educator record in database
    3. Returns educator information

    Protected endpoint - requires valid JWT token in Authorization header.

    Returns:
        EducatorPublic: Current educator's information
    """
    # Extract user info from JWT
    user_id = user["user_id"]
    email = user["email"]

    # Get user metadata if available
    user_metadata = user.get("raw_payload", {}).get("user_metadata", {})
    name = user_metadata.get("name") or user_metadata.get("full_name")
    school = user_metadata.get("school")

    # Get or create educator record
    educator = get_or_create_educator(
        session=session,
        user_id=user_id,
        email=email,
        name=name,
        school=school,
    )

    return educator


@router.post("/logout")
async def logout(
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Logout endpoint (placeholder)

    In Supabase, logout is handled client-side by clearing the session.
    This endpoint exists for consistency and can be used for:
    - Logging logout events
    - Invalidating refresh tokens (if needed)
    - Analytics

    Returns:
        Success message
    """
    return {
        "message": "Logged out successfully",
        "user_id": user["user_id"],
    }


@router.get("/verify")
async def verify_token(
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Verify JWT token validity

    Simple endpoint to check if a token is valid.
    Useful for frontend to verify authentication status.

    Returns:
        User information if token is valid
    """
    return {
        "valid": True,
        "user_id": user["user_id"],
        "email": user["email"],
    }
