"""Pydantic schemas for Book model validation and serialization."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.review import ReviewResponse


class BookBase(BaseModel):
    """Base book schema with common attributes."""

    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=255)
    genre: str = Field(..., min_length=1, max_length=100)
    year_published: int = Field(..., ge=1000, le=2100)


class BookCreate(BookBase):
    """Schema for creating a new book."""

    pass


class BookUpdate(BaseModel):
    """Schema for updating book information."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    genre: Optional[str] = Field(None, min_length=1, max_length=100)
    year_published: Optional[int] = Field(None, ge=1000, le=2100)
    summary: Optional[str] = None


class BookInDB(BookBase):
    """Schema for book as stored in database."""

    id: int
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class BookResponse(BookInDB):
    """Schema for book response."""

    pass


class BookWithReviews(BookResponse):
    """Schema for book with its reviews included."""

    reviews: List["ReviewResponse"] = []


class BookSummaryResponse(BaseModel):
    """Schema for book summary with aggregated rating."""

    id: int
    title: str
    author: str
    summary: Optional[str] = None
    average_rating: Optional[float] = None
    total_reviews: int

    class Config:
        """Pydantic configuration."""

        from_attributes = True
