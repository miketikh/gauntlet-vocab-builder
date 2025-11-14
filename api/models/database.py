"""
SQLModel Database Models
Defines database schema using SQLModel (SQLAlchemy + Pydantic)
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship, Column, Enum as SQLEnum, JSON


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


class RecommendationStatus(str, Enum):
    """Recommendation status"""
    PENDING = "pending"
    ADOPTED = "adopted"
    NOT_USED = "not_used"


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
    recommendations: List["Recommendation"] = Relationship(back_populates="student")


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
    analysis_results: List["AnalysisResult"] = Relationship(back_populates="document")


class AnalysisResult(SQLModel, table=True):
    """
    AnalysisResult table - stores vocabulary analysis results for documents
    Linked to documents table via document_id
    """
    __tablename__ = "analysis_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id", index=True)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

    # VocabularyProfile data stored as JSON
    student_grade_level: int = Field(ge=6, le=12, description="Student's grade level at time of analysis")

    # Statistics
    total_words: int = Field(ge=0, description="Total word count (including duplicates)")
    unique_words: int = Field(ge=0, description="Count of unique words")
    analyzed_words: int = Field(ge=0, description="Words found in grade_words database")
    unknown_words: int = Field(ge=0, description="Words not found in database")
    unknown_percentage: float = Field(ge=0.0, le=1.0, description="Percentage of words not in database")
    average_grade_level: Optional[float] = Field(default=None, description="Weighted average grade level")
    below_grade_count: int = Field(ge=0, description="Number of words below student's grade")
    at_grade_count: int = Field(ge=0, description="Number of words at student's grade")
    above_grade_count: int = Field(ge=0, description="Number of words above student's grade")

    # Grade distribution (stored as JSON)
    grade_distribution: dict = Field(
        default={},
        sa_column=Column(JSON),
        description="Distribution of words across grade levels"
    )

    # Challenging words and detailed analysis (stored as JSON)
    challenging_words: list = Field(
        default=[],
        sa_column=Column(JSON),
        description="List of challenging words above student's grade level"
    )

    word_details: list = Field(
        default=[],
        sa_column=Column(JSON),
        description="Detailed analysis of all unique words"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    document: Document = Relationship(back_populates="analysis_results")


class Recommendation(SQLModel, table=True):
    """
    Recommendation table - stores personalized vocabulary recommendations for students
    Generated by LLM based on vocabulary analysis
    """
    __tablename__ = "recommendations"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id", index=True)
    document_id: Optional[int] = Field(default=None, foreign_key="documents.id", index=True)

    # Recommendation content
    word: str = Field(max_length=100, description="Recommended vocabulary word")
    recommended_grade_level: int = Field(ge=6, le=12, description="Grade level of recommended word")
    subject: Optional[str] = Field(default=None, max_length=100, description="Subject area")

    # Context from LLM
    current_usage: Optional[str] = Field(default=None, description="Current word/phrase student uses")
    context: Optional[str] = Field(default=None, description="Brief explanation of where this fits")
    example_sentence: Optional[str] = Field(default=None, description="Example sentence using the word")
    rationale: Optional[str] = Field(default=None, description="Why this word is recommended")

    # Status tracking
    status: RecommendationStatus = Field(
        default=RecommendationStatus.PENDING,
        sa_column=Column(SQLEnum(RecommendationStatus))
    )

    # Timestamps
    recommended_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    student: Student = Relationship(back_populates="recommendations")


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
    s3_key: str
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


class AnalysisResultPublic(SQLModel):
    """Public analysis result data for API responses"""
    id: int
    document_id: int
    analyzed_at: datetime
    student_grade_level: int
    total_words: int
    unique_words: int
    analyzed_words: int
    unknown_words: int
    unknown_percentage: float
    average_grade_level: Optional[float]
    below_grade_count: int
    at_grade_count: int
    above_grade_count: int
    grade_distribution: dict
    challenging_words: list
    word_details: list


class RecommendationPublic(SQLModel):
    """Public recommendation data for API responses"""
    id: int
    student_id: int
    document_id: Optional[int]
    word: str
    recommended_grade_level: int
    subject: Optional[str]
    current_usage: Optional[str]
    context: Optional[str]
    example_sentence: Optional[str]
    rationale: Optional[str]
    status: RecommendationStatus
    recommended_at: datetime


class RecommendationCreate(SQLModel):
    """Data required to create a recommendation"""
    student_id: int
    document_id: Optional[int] = None
    word: str
    recommended_grade_level: int
    subject: Optional[str] = None
    current_usage: Optional[str] = None
    context: Optional[str] = None
    example_sentence: Optional[str] = None
    rationale: Optional[str] = None
