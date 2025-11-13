"""
Pydantic models for vocabulary recommendations.

This module defines the data models used for generating, storing, and
displaying vocabulary recommendations.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class VocabularyRecommendation(BaseModel):
    """
    A single vocabulary word recommendation for a student.

    This model represents an AI-generated recommendation for a vocabulary word
    that would help the student improve their language skills.
    """

    word: str = Field(..., description="The recommended vocabulary word")
    recommended_grade: int = Field(
        ...,
        ge=1,
        le=12,
        description="Grade level of the recommended word"
    )
    current_usage: str = Field(
        ...,
        description="Simpler word or phrase the student might currently use"
    )
    definition: str = Field(..., description="Clear, student-friendly definition")
    example_sentence: str = Field(
        ...,
        description="Example sentence relevant to the subject and student's level"
    )
    rationale: str = Field(
        ...,
        description="Why this word is appropriate for this student"
    )

    @field_validator("word")
    @classmethod
    def word_must_not_be_empty(cls, v: str) -> str:
        """Validate that word is not empty."""
        if not v or not v.strip():
            raise ValueError("Word cannot be empty")
        return v.strip().lower()

    @field_validator("definition", "rationale")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        """Validate that text fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Text field cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "word": "analyze",
                "recommended_grade": 7,
                "current_usage": "look at",
                "definition": "to examine something carefully and in detail",
                "example_sentence": "Scientists analyze data to find patterns in their experiments.",
                "rationale": "Essential academic vocabulary for scientific inquiry and critical thinking."
            }
        }


class RecommendationRequest(BaseModel):
    """
    Request model for generating vocabulary recommendations.
    """

    student_id: UUID = Field(..., description="ID of the student")
    document_id: Optional[UUID] = Field(
        None,
        description="Optional document ID to base recommendations on"
    )
    count: int = Field(
        10,
        ge=1,
        le=20,
        description="Number of recommendations to generate"
    )
    subject: Optional[str] = Field(
        None,
        description="Optional subject filter (ELA, Math, Science, Social Studies)"
    )
    target_grade_offset: int = Field(
        1,
        ge=1,
        le=3,
        description="How many grade levels above student's current level (1-3)"
    )

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: Optional[str]) -> Optional[str]:
        """Validate subject is one of the allowed values."""
        if v is None:
            return v

        allowed_subjects = ["ELA", "Math", "Science", "Social Studies"]
        if v not in allowed_subjects:
            raise ValueError(f"Subject must be one of: {', '.join(allowed_subjects)}")
        return v


class RecommendationSet(BaseModel):
    """
    A collection of vocabulary recommendations for a student.

    This model represents a complete set of recommendations generated
    at a specific time for a student.
    """

    student_id: UUID = Field(..., description="ID of the student")
    recommendations: List[VocabularyRecommendation] = Field(
        ...,
        description="List of vocabulary recommendations"
    )
    subject: Optional[str] = Field(None, description="Subject area")
    student_grade: int = Field(
        ...,
        ge=6,
        le=8,
        description="Student's grade level (6-8)"
    )
    avg_grade_level: float = Field(
        ...,
        ge=1.0,
        le=12.0,
        description="Student's current average vocabulary grade level"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When recommendations were generated"
    )
    model_used: str = Field(
        default="gpt-4o-mini",
        description="LLM model used for generation"
    )
    tokens_used: Optional[int] = Field(
        None,
        description="Total tokens used in generation"
    )

    @field_validator("recommendations")
    @classmethod
    def must_have_recommendations(cls, v: List[VocabularyRecommendation]) -> List[VocabularyRecommendation]:
        """Validate that there is at least one recommendation."""
        if not v:
            raise ValueError("Must have at least one recommendation")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174000",
                "recommendations": [
                    {
                        "word": "analyze",
                        "recommended_grade": 7,
                        "current_usage": "look at",
                        "definition": "to examine something carefully and in detail",
                        "example_sentence": "Scientists analyze data to find patterns.",
                        "rationale": "Essential for scientific inquiry."
                    }
                ],
                "subject": "Science",
                "student_grade": 7,
                "avg_grade_level": 6.5,
                "created_at": "2024-11-13T12:00:00Z",
                "model_used": "gpt-4o-mini",
                "tokens_used": 250
            }
        }


class RecommendationResponse(BaseModel):
    """
    Response model for recommendation generation API.
    """

    success: bool = Field(..., description="Whether generation was successful")
    recommendations: List[VocabularyRecommendation] = Field(
        default_factory=list,
        description="List of generated recommendations"
    )
    count: int = Field(..., description="Number of recommendations generated")
    student_grade: int = Field(..., description="Student's grade level")
    avg_grade_level: float = Field(
        ...,
        description="Student's current vocabulary grade level"
    )
    subject: Optional[str] = Field(None, description="Subject filter applied")
    tokens_used: Optional[int] = Field(None, description="Tokens used in generation")
    estimated_cost: Optional[float] = Field(
        None,
        description="Estimated cost in USD"
    )
    error: Optional[str] = Field(None, description="Error message if failed")


class VocabularyGapAnalysis(BaseModel):
    """
    Analysis of vocabulary gaps in student writing.

    Identifies specific places in student text where vocabulary
    could be improved.
    """

    original_phrase: str = Field(..., description="Original phrase from student text")
    suggested_replacement: str = Field(
        ...,
        description="Suggested more sophisticated alternative"
    )
    grade_level: int = Field(
        ...,
        ge=1,
        le=12,
        description="Grade level of suggested replacement"
    )
    context: str = Field(..., description="Context where this appears in the text")
    improvement_note: str = Field(
        ...,
        description="Why this replacement would improve the writing"
    )


class GapAnalysisResponse(BaseModel):
    """
    Response model for vocabulary gap analysis.
    """

    success: bool = Field(..., description="Whether analysis was successful")
    gaps: List[VocabularyGapAnalysis] = Field(
        default_factory=list,
        description="List of identified vocabulary gaps"
    )
    student_id: UUID = Field(..., description="ID of the student")
    document_id: Optional[UUID] = Field(None, description="ID of analyzed document")
    analyzed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When analysis was performed"
    )
    error: Optional[str] = Field(None, description="Error message if failed")


class RecommendationSettings(BaseModel):
    """
    Customizable settings for recommendation generation.

    These settings allow educators to fine-tune how recommendations
    are generated for individual students.
    """

    student_id: UUID = Field(..., description="ID of the student")
    count: int = Field(
        10,
        ge=5,
        le=20,
        description="Default number of recommendations"
    )
    target_grade_offset: int = Field(
        1,
        ge=1,
        le=3,
        description="Grade levels above current (1=conservative, 2=moderate, 3=challenging)"
    )
    subjects: Optional[List[str]] = Field(
        None,
        description="Subject filters (None = all subjects)"
    )
    auto_generate: bool = Field(
        False,
        description="Whether to auto-generate after document analysis"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When settings were last updated"
    )

    @field_validator("subjects")
    @classmethod
    def validate_subjects(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate all subjects are allowed values."""
        if v is None:
            return v

        allowed_subjects = {"ELA", "Math", "Science", "Social Studies"}
        for subject in v:
            if subject not in allowed_subjects:
                raise ValueError(
                    f"Invalid subject: {subject}. Must be one of: {', '.join(allowed_subjects)}"
                )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174000",
                "count": 10,
                "target_grade_offset": 1,
                "subjects": ["Science", "ELA"],
                "auto_generate": False,
                "updated_at": "2024-11-13T12:00:00Z"
            }
        }
