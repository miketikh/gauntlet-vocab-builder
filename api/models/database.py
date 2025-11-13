"""
SQLModel Database Models
Defines database schema using SQLModel (SQLAlchemy + Pydantic)
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship, Column, Enum as SQLEnum


# Enums
class DocumentStatus(str, Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileType(str, Enum):
    """Supported file types for document upload"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


# Database Models
class Educator(SQLModel, table=True):
    """
    Educator table - stores educator/teacher information
    Linked to Supabase Auth via email
    """
    __tablename__ = "educators"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    school: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    students: List["Student"] = Relationship(back_populates="educator")


class Student(SQLModel, table=True):
    """
    Student table - stores student information managed by educators
    """
    __tablename__ = "students"

    id: Optional[int] = Field(default=None, primary_key=True)
    educator_id: int = Field(foreign_key="educators.id", index=True)
    name: str = Field(max_length=255, description="Student display name")
    grade_level: int = Field(ge=6, le=12, description="Grade level (6-12)")
    reading_level: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    educator: Educator = Relationship(back_populates="students")
    documents: List["Document"] = Relationship(back_populates="student")


class Document(SQLModel, table=True):
    """
    Document table - stores uploaded student documents
    Files are stored in S3, metadata stored in database
    """
    __tablename__ = "documents"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id", index=True)
    title: str = Field(max_length=255)
    s3_key: str = Field(max_length=512, description="S3 object key for file storage")
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    file_type: FileType = Field(sa_column=Column(SQLEnum(FileType)))
    subject: Optional[str] = Field(default=None, max_length=100, description="Subject area (e.g., ELA, Math, Science)")
    status: DocumentStatus = Field(
        default=DocumentStatus.PENDING,
        sa_column=Column(SQLEnum(DocumentStatus))
    )
    error_message: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    student: Student = Relationship(back_populates="documents")


class GradeWord(SQLModel, table=True):
    """
    GradeWord table - stores grade-appropriate vocabulary words
    Pre-populated with curated word lists
    """
    __tablename__ = "grade_words"

    id: Optional[int] = Field(default=None, primary_key=True)
    grade_level: int = Field(ge=6, le=12, index=True, description="Grade level (6-12)")
    word: str = Field(max_length=100, index=True)
    definition: str = Field(description="Student-friendly definition")
    example: Optional[str] = Field(default=None, description="Example sentence")
    frequency_rank: Optional[int] = Field(default=None, description="Word frequency ranking")
    subject: Optional[str] = Field(default=None, max_length=50, description="Subject area (e.g., science, history)")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """SQLModel configuration"""
        # Ensure unique word per grade level
        table_args = (
            {"schema": None},
        )


# API Response Models (Pydantic models for API responses)
class EducatorPublic(SQLModel):
    """Public educator data for API responses"""
    id: int
    email: str
    name: str
    school: Optional[str]
    created_at: datetime


class StudentPublic(SQLModel):
    """Public student data for API responses"""
    id: int
    educator_id: int
    name: str
    grade_level: int
    reading_level: Optional[str]
    notes: Optional[str]
    created_at: datetime


class DocumentPublic(SQLModel):
    """Public document data for API responses"""
    id: int
    student_id: int
    title: str
    upload_date: datetime
    file_type: FileType
    subject: Optional[str]
    status: DocumentStatus
    error_message: Optional[str]


class GradeWordPublic(SQLModel):
    """Public grade word data for API responses"""
    id: int
    grade_level: int
    word: str
    definition: str
    example: Optional[str]
    frequency_rank: Optional[int]
    subject: Optional[str]


# API Create Models (Pydantic models for creating records)
class EducatorCreate(SQLModel):
    """Data required to create an educator"""
    email: str
    name: str
    school: Optional[str] = None


class StudentCreate(SQLModel):
    """Data required to create a student"""
    name: str
    grade_level: int = Field(ge=6, le=12)
    reading_level: Optional[str] = None
    notes: Optional[str] = None


class DocumentCreate(SQLModel):
    """Data required to create a document"""
    student_id: int
    title: str
    s3_key: str
    file_type: FileType
    subject: Optional[str] = None


class GradeWordCreate(SQLModel):
    """Data required to create a grade word"""
    grade_level: int = Field(ge=6, le=12)
    word: str
    definition: str
    example: Optional[str] = None
    frequency_rank: Optional[int] = None
    subject: Optional[str] = None


# API Update Models (Pydantic models for updating records)
class StudentUpdate(SQLModel):
    """Data for updating a student"""
    name: Optional[str] = None
    grade_level: Optional[int] = Field(default=None, ge=6, le=12)
    reading_level: Optional[str] = None
    notes: Optional[str] = None


class DocumentUpdate(SQLModel):
    """Data for updating a document"""
    status: Optional[DocumentStatus] = None
    error_message: Optional[str] = None
