"""Book model for storing book information."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship

from app.db.base import Base


class Book(Base):
    """Book model for storing book information and AI-generated summaries."""

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    genre = Column(String(100), nullable=False, index=True)
    year_published = Column(Integer, nullable=False)
    # AI-generated summary
    summary = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=datetime.now(), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.now(),
        onupdate=datetime.now(),
        nullable=False,
    )

    # Relationships
    reviews = relationship(
        "Review", back_populates="book", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Book."""
        return f"<Book(id={self.id}, title={self.title}, author={self.author})>"
