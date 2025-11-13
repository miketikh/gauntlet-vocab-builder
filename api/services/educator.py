"""
Educator Service
Handles educator-related business logic including get-or-create on first login
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Session, select

from models.database import Educator, EducatorCreate


def get_or_create_educator(
    session: Session,
    user_id: str,
    email: str,
    name: Optional[str] = None,
    school: Optional[str] = None,
) -> Educator:
    """
    Get existing educator by email or create new one on first login

    This function handles the first-time login flow:
    1. Check if educator exists in database (by email)
    2. If exists, return the educator
    3. If not exists, create new educator record

    Args:
        session: SQLModel database session
        user_id: Supabase auth user ID (UUID) - stored for reference
        email: Educator email from JWT claims
        name: Educator name from user metadata (optional)
        school: School name from user metadata (optional)

    Returns:
        Educator: Existing or newly created educator record
    """
    # Try to find existing educator by email
    statement = select(Educator).where(Educator.email == email)
    existing_educator = session.exec(statement).first()

    if existing_educator:
        # Update updated_at timestamp on login
        existing_educator.updated_at = datetime.utcnow()
        session.add(existing_educator)
        session.commit()
        session.refresh(existing_educator)
        return existing_educator

    # Create new educator on first login
    new_educator = Educator(
        email=email,
        name=name or email.split("@")[0],  # Default name from email if not provided
        school=school,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    session.add(new_educator)
    session.commit()
    session.refresh(new_educator)

    return new_educator


def get_educator_by_email(session: Session, email: str) -> Optional[Educator]:
    """
    Get educator by email address

    Args:
        session: SQLModel database session
        email: Educator email

    Returns:
        Educator if found, None otherwise
    """
    statement = select(Educator).where(Educator.email == email)
    return session.exec(statement).first()


def get_educator_by_id(session: Session, educator_id: int) -> Optional[Educator]:
    """
    Get educator by database ID

    Args:
        session: SQLModel database session
        educator_id: Educator database ID

    Returns:
        Educator if found, None otherwise
    """
    return session.get(Educator, educator_id)


def update_educator(
    session: Session,
    educator_id: int,
    name: Optional[str] = None,
    school: Optional[str] = None,
) -> Optional[Educator]:
    """
    Update educator information

    Args:
        session: SQLModel database session
        educator_id: Educator database ID
        name: Updated name (optional)
        school: Updated school (optional)

    Returns:
        Updated Educator if found, None otherwise
    """
    educator = get_educator_by_id(session, educator_id)

    if not educator:
        return None

    # Update fields if provided
    if name is not None:
        educator.name = name
    if school is not None:
        educator.school = school

    educator.updated_at = datetime.utcnow()

    session.add(educator)
    session.commit()
    session.refresh(educator)

    return educator
