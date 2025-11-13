"""
Analysis Models
Pydantic models for vocabulary analysis results
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class WordCategory(str, Enum):
    """Category of word relative to student's grade level"""
    BELOW = "below"  # 2+ grades below student (easier vocabulary)
    AT = "at"        # Within 1 grade of student level (appropriate difficulty)
    ABOVE = "above"  # 2+ grades above student (challenging vocabulary)
    UNKNOWN = "unknown"  # Not in our database


class WordAnalysisResult(BaseModel):
    """Analysis result for a single word"""
    word: str = Field(description="The analyzed word (lemmatized)")
    frequency: int = Field(ge=1, description="Number of times word appears in text")
    grade_level: Optional[int] = Field(
        default=None,
        ge=6,
        le=12,
        description="Grade level of word (6-12) if found in database"
    )
    definition: Optional[str] = Field(
        default=None,
        description="Definition of the word if available"
    )
    example: Optional[str] = Field(
        default=None,
        description="Example usage of the word if available"
    )
    subject: Optional[str] = Field(
        default=None,
        description="Subject area (e.g., ELA, Science, Math)"
    )
    category: WordCategory = Field(
        description="Category relative to student's grade level"
    )

    class Config:
        use_enum_values = True


class GradeDistribution(BaseModel):
    """Distribution of words across grade levels"""
    grade_6: float = Field(ge=0.0, le=1.0, description="Percentage of grade 6 words")
    grade_7: float = Field(ge=0.0, le=1.0, description="Percentage of grade 7 words")
    grade_8: float = Field(ge=0.0, le=1.0, description="Percentage of grade 8 words")
    grade_9: float = Field(ge=0.0, le=1.0, description="Percentage of grade 9 words")
    grade_10: float = Field(ge=0.0, le=1.0, description="Percentage of grade 10 words")
    grade_11: float = Field(ge=0.0, le=1.0, description="Percentage of grade 11 words")
    grade_12: float = Field(ge=0.0, le=1.0, description="Percentage of grade 12 words")

    def to_dict(self) -> Dict[int, float]:
        """Convert to dictionary mapping grade to percentage"""
        return {
            6: self.grade_6,
            7: self.grade_7,
            8: self.grade_8,
            9: self.grade_9,
            10: self.grade_10,
            11: self.grade_11,
            12: self.grade_12
        }

    @classmethod
    def from_dict(cls, data: Dict[int, float]) -> "GradeDistribution":
        """Create from dictionary mapping grade to percentage"""
        return cls(
            grade_6=data.get(6, 0.0),
            grade_7=data.get(7, 0.0),
            grade_8=data.get(8, 0.0),
            grade_9=data.get(9, 0.0),
            grade_10=data.get(10, 0.0),
            grade_11=data.get(11, 0.0),
            grade_12=data.get(12, 0.0)
        )


class VocabularyStatistics(BaseModel):
    """Statistical summary of vocabulary analysis"""
    total_words: int = Field(ge=0, description="Total word count (including duplicates)")
    unique_words: int = Field(ge=0, description="Count of unique words")
    analyzed_words: int = Field(ge=0, description="Words found in grade_words database")
    unknown_words: int = Field(ge=0, description="Words not found in database")
    unknown_percentage: float = Field(
        ge=0.0,
        le=1.0,
        description="Percentage of words not in database"
    )
    average_grade_level: Optional[float] = Field(
        default=None,
        ge=6.0,
        le=12.0,
        description="Weighted average grade level of analyzed words"
    )
    below_grade_count: int = Field(ge=0, description="Number of words below student's grade")
    at_grade_count: int = Field(ge=0, description="Number of words at student's grade")
    above_grade_count: int = Field(ge=0, description="Number of words above student's grade")


class VocabularyProfile(BaseModel):
    """Complete vocabulary analysis profile for a document"""
    student_grade_level: int = Field(
        ge=6,
        le=12,
        description="Student's current grade level"
    )
    statistics: VocabularyStatistics = Field(
        description="Statistical summary of vocabulary"
    )
    grade_distribution: GradeDistribution = Field(
        description="Distribution of words across grade levels"
    )
    challenging_words: List[WordAnalysisResult] = Field(
        default_factory=list,
        description="Words above student's grade level (most challenging)"
    )
    word_details: List[WordAnalysisResult] = Field(
        default_factory=list,
        description="Detailed analysis of all unique words"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "student_grade_level": 8,
                "statistics": {
                    "total_words": 523,
                    "unique_words": 245,
                    "analyzed_words": 220,
                    "unknown_words": 25,
                    "unknown_percentage": 0.102,
                    "average_grade_level": 8.2,
                    "below_grade_count": 140,
                    "at_grade_count": 50,
                    "above_grade_count": 30
                },
                "grade_distribution": {
                    "grade_6": 0.30,
                    "grade_7": 0.25,
                    "grade_8": 0.20,
                    "grade_9": 0.15,
                    "grade_10": 0.07,
                    "grade_11": 0.02,
                    "grade_12": 0.01
                },
                "challenging_words": [],
                "word_details": []
            }
        }


class DocumentAnalysisRequest(BaseModel):
    """Request model for document analysis"""
    document_id: int = Field(description="Database ID of document to analyze")
    student_grade_level: Optional[int] = Field(
        default=None,
        ge=6,
        le=12,
        description="Override student's grade level (uses document's student if not provided)"
    )


class DocumentAnalysisResponse(BaseModel):
    """Response model for document analysis"""
    document_id: int
    analysis: VocabularyProfile
    analyzed_at: str = Field(description="ISO timestamp of analysis")
