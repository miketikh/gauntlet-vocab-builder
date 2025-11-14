"""
Authentication Service
Handles Supabase JWT verification using HS256 symmetric key
"""
import os
from typing import Dict, Any
from jose import jwt, JWTError
from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is not set")

if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is not set")

# Remove quotes from JWT_SECRET if present (common formatting issue)
JWT_SECRET = JWT_SECRET.strip('"').strip("'")


async def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify Supabase JWT token using HS256 symmetric key verification

    Supabase uses HS256 (symmetric) algorithm for JWT signing by default.
    The JWT secret can be found in your Supabase project settings.

    Note: Supabase's JWKS endpoint currently returns empty keys because
    asymmetric key support (RS256) is not yet fully implemented. Therefore,
    we use the JWT_SECRET for HS256 verification.

    Args:
        token: JWT token string from Authorization header

    Returns:
        Dict containing JWT claims (sub, email, etc.)

    Raises:
        HTTPException: If token is invalid, expired, or verification fails
    """
    try:
        # Verify and decode the token using HS256
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",  # Supabase uses "authenticated" as audience
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_exp": True,
            }
        )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def extract_user_id(token_payload: Dict[str, Any]) -> str:
    """
    Extract user ID from JWT payload

    Args:
        token_payload: Decoded JWT claims

    Returns:
        User ID (UUID string)
    """
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID (sub claim)"
        )
    return user_id


def extract_user_email(token_payload: Dict[str, Any]) -> str:
    """
    Extract user email from JWT payload

    Args:
        token_payload: Decoded JWT claims

    Returns:
        User email
    """
    email = token_payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing email claim"
        )
    return email


def extract_user_metadata(token_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract user metadata from JWT payload

    Args:
        token_payload: Decoded JWT claims

    Returns:
        User metadata dictionary
    """
    return token_payload.get("user_metadata", {})
