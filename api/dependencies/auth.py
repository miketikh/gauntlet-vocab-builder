"""
Authentication Dependencies
FastAPI dependencies for protecting endpoints with JWT authentication
"""
from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth import verify_jwt_token, extract_user_id, extract_user_email

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user from JWT token

    Extracts JWT from Authorization: Bearer <token> header,
    verifies it with Supabase JWKS, and returns user claims.

    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user_id": user["user_id"], "email": user["email"]}

    Returns:
        Dict containing user information:
        - user_id: Supabase user ID (UUID)
        - email: User email
        - raw_payload: Full JWT payload for advanced use cases

    Raises:
        HTTPException 401: If token is missing, invalid, or expired
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Verify the JWT token
    payload = await verify_jwt_token(token)

    # Extract user information
    user_id = extract_user_id(payload)
    email = extract_user_email(payload)

    return {
        "user_id": user_id,
        "email": email,
        "raw_payload": payload,
    }


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency for optional authentication

    Same as get_current_user but doesn't raise 401 if no token is provided.
    Useful for endpoints that have both authenticated and public access.

    Returns:
        Dict with user info if authenticated, None if not authenticated
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = await verify_jwt_token(token)

        user_id = extract_user_id(payload)
        email = extract_user_email(payload)

        return {
            "user_id": user_id,
            "email": email,
            "raw_payload": payload,
        }
    except HTTPException:
        # Invalid token - treat as unauthenticated
        return None
