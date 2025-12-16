"""Review model for storing book reviews and ratings."""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class Review(Base):
    """Review model for storing user reviews and ratings for books."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(
        Integer,
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    review_text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(
        DateTime, default=datetime.now(), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.now(),
        onupdate=datetime.now(),
        nullable=False,
    )

    # Add constraint for rating between 1 and 5
    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5", name="rating_check"
        ),
    )

    # Relationships
    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    def __repr__(self) -> str:
        """String representation of Review."""
        return f"<Review(id={self.id}, book_id={self.book_id}, rating={self.rating})>"
