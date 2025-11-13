"""
Models package
Exports database models and API schemas
"""
from .database import (
    # Table models
    Educator,
    Student,
    Document,
    GradeWord,
    # Enums
    DocumentStatus,
    FileType,
    # Public response models
    EducatorPublic,
    StudentPublic,
    DocumentPublic,
    GradeWordPublic,
    # Create models
    EducatorCreate,
    StudentCreate,
    DocumentCreate,
    GradeWordCreate,
    # Update models
    StudentUpdate,
    DocumentUpdate,
)

__all__ = [
    # Table models
    "Educator",
    "Student",
    "Document",
    "GradeWord",
    # Enums
    "DocumentStatus",
    "FileType",
    # Public response models
    "EducatorPublic",
    "StudentPublic",
    "DocumentPublic",
    "GradeWordPublic",
    # Create models
    "EducatorCreate",
    "StudentCreate",
    "DocumentCreate",
    "GradeWordCreate",
    # Update models
    "StudentUpdate",
    "DocumentUpdate",
]
