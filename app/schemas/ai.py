"""Pydantic schemas for AI-related requests and responses."""

from typing import Optional, List
from pydantic import BaseModel, Field


class GenerateSummaryRequest(BaseModel):
    """Schema for generating a summary from book content."""

    book_id: int = Field(..., ge=1)
    content: str = Field(..., min_length=50, max_length=50000)


class GenerateSummaryResponse(BaseModel):
    """Schema for summary generation response."""

    summary: str
    word_count: int


class RecommendationRequest(BaseModel):
    """Schema for book recommendation request."""

    genre: Optional[str] = None
    limit: int = Field(10, ge=1, le=50)


class BookRecommendation(BaseModel):
    """Schema for a single book recommendation."""

    id: int
    title: str
    author: str
    genre: str
    average_rating: Optional[float] = None
    total_reviews: int

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class RecommendationResponse(BaseModel):
    """Schema for book recommendations response."""

    recommendations: List[BookRecommendation]
    total: int
    cached: bool = False
