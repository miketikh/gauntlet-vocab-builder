"""
Authentication Service
Handles Supabase JWT verification using JWKS endpoint
"""
import os
from typing import Optional, Dict, Any
from datetime import datetime
from jose import jwt, JWTError, jwk
from jose.backends import RSAKey
import httpx
from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is not set")

# JWKS endpoint for Supabase
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

# Cache for JWKS keys (in production, consider using Redis or similar)
_jwks_cache: Optional[Dict[str, Any]] = None
_jwks_cache_time: Optional[datetime] = None
JWKS_CACHE_DURATION_SECONDS = 3600  # Refresh every hour


async def get_jwks() -> Dict[str, Any]:
    """
    Fetch JWKS (JSON Web Key Set) from Supabase
    Caches the result to avoid excessive requests
    """
    global _jwks_cache, _jwks_cache_time

    # Check if cache is valid
    if _jwks_cache and _jwks_cache_time:
        elapsed = (datetime.utcnow() - _jwks_cache_time).total_seconds()
        if elapsed < JWKS_CACHE_DURATION_SECONDS:
            return _jwks_cache

    # Fetch fresh JWKS
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(JWKS_URL, timeout=10.0)
            response.raise_for_status()
            jwks_data = response.json()

            # Update cache
            _jwks_cache = jwks_data
            _jwks_cache_time = datetime.utcnow()

            return jwks_data
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to fetch JWKS from Supabase: {str(e)}"
            )


async def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify Supabase JWT token using JWKS asymmetric key verification

    Args:
        token: JWT token string from Authorization header

    Returns:
        Dict containing JWT claims (sub, email, etc.)

    Raises:
        HTTPException: If token is invalid, expired, or verification fails
    """
    try:
        # Get JWKS keys
        jwks_data = await get_jwks()

        # Decode the JWT header to get the key ID (kid)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing key ID (kid) in header"
            )

        # Find the matching key in JWKS
        matching_key = None
        for key in jwks_data.get("keys", []):
            if key.get("kid") == kid:
                matching_key = key
                break

        if not matching_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No matching key found in JWKS"
            )

        # Convert JWK to RSA key
        rsa_key = jwk.construct(matching_key)

        # Verify and decode the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
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
