"""
Database Service
Handles SQLModel engine initialization and session management
"""
import os
from typing import Generator, Optional
from sqlmodel import SQLModel, create_engine, Session, select
from dotenv import load_dotenv

from models.database import Educator, Student, Document

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine
# Note: For Supabase pooler connection string, we use the session mode URL
# Format: postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-us-east-2.pooler.supabase.com:6543/postgres
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10,
)


def create_db_and_tables():
    """
    Create all database tables
    Note: In production, use Alembic migrations instead
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI endpoints to get database session

    Usage:
        @app.get("/students")
        def get_students(session: Session = Depends(get_session)):
            students = session.exec(select(Student)).all()
            return students
    """
    with Session(engine) as session:
        yield session


# Helper functions for common queries
def get_educator_by_email(session: Session, email: str) -> Optional[Educator]:
    """Get educator by email address"""
    statement = select(Educator).where(Educator.email == email)
    return session.exec(statement).first()


def get_educator_by_id(session: Session, educator_id: int) -> Optional[Educator]:
    """Get educator by ID"""
    return session.get(Educator, educator_id)


def get_educator_students(session: Session, educator_id: int) -> list[Student]:
    """Get all students for a specific educator"""
    statement = select(Student).where(Student.educator_id == educator_id)
    return list(session.exec(statement).all())


def get_student_by_id(session: Session, student_id: int) -> Optional[Student]:
    """Get student by ID"""
    return session.get(Student, student_id)


def get_student_documents(session: Session, student_id: int) -> list[Document]:
    """Get all documents for a specific student"""
    statement = select(Document).where(Document.student_id == student_id)
    return list(session.exec(statement).all())


def verify_educator_owns_student(
    session: Session, educator_id: int, student_id: int
) -> bool:
    """
    Verify that an educator owns a specific student
    Used for authorization checks
    """
    student = get_student_by_id(session, student_id)
    return student is not None and student.educator_id == educator_id


def verify_educator_owns_document(
    session: Session, educator_id: int, document_id: int
) -> bool:
    """
    Verify that an educator owns a specific document (via student)
    Used for authorization checks
    """
    document = session.get(Document, document_id)
    if not document:
        return False
    return verify_educator_owns_student(session, educator_id, document.student_id)


# Database initialization
def init_db():
    """
    Initialize database
    Creates tables if they don't exist
    Note: In production, use Alembic migrations
    """
    create_db_and_tables()
    print("Database initialized successfully")
