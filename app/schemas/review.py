"""Pydantic schemas for Review model validation and serialization."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class ReviewBase(BaseModel):
    """Base review schema with common attributes."""

    review_text: str = Field(..., min_length=10, max_length=5000)
    rating: int = Field(..., ge=1, le=5)


class ReviewCreate(ReviewBase):
    """Schema for creating a new review."""

    pass


class ReviewUpdate(BaseModel):
    """Schema for updating review information."""

    review_text: Optional[str] = Field(
        None, min_length=10, max_length=5000
    )
    rating: Optional[int] = Field(None, ge=1, le=5)


class ReviewInDB(ReviewBase):
    """Schema for review as stored in database."""

    id: int
    book_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ReviewResponse(ReviewInDB):
    """Schema for review response."""

    pass


class ReviewWithUser(ReviewResponse):
    """Schema for review with user information."""

    user: "UserResponse"
