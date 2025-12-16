"""Book service for CRUD operations on books."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.book import Book
from app.models.review import Review
from app.schemas.book import BookCreate, BookUpdate


class BookService:
    """Service for handling book-related operations."""

    @staticmethod
    async def create_book(
        book_data: BookCreate, db: AsyncSession
    ) -> Book:
        """
        Create a new book.

        Args:
            book_data: Book creation data
            db: Database session

        Returns:
            The created book
        """
        new_book = Book(
            title=book_data.title,
            author=book_data.author,
            genre=book_data.genre,
            year_published=book_data.year_published,
        )

        db.add(new_book)
        await db.commit()
        await db.refresh(new_book)

        return new_book

    @staticmethod
    async def get_all_books(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Book]:
        """
        Get all books with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of books
        """
        result = await db.execute(
            select(Book)
            .offset(skip)
            .limit(limit)
            .order_by(Book.created_at.desc())
        )
        books = result.scalars().all()
        return list(books)

    @staticmethod
    async def get_book_by_id(book_id: int, db: AsyncSession) -> Book:
        """
        Get a book by ID.

        Args:
            book_id: Book ID
            db: Database session

        Returns:
            The book

        Raises:
            HTTPException: If book not found
        """
        result = await db.execute(
            select(Book).where(Book.id == book_id)
        )
        book = result.scalar_one_or_none()

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {book_id} not found",
            )

        return book

    @staticmethod
    async def update_book(
        book_id: int, book_data: BookUpdate, db: AsyncSession
    ) -> Book:
        """
        Update a book.

        Args:
            book_id: Book ID
            book_data: Book update data
            db: Database session

        Returns:
            The updated book

        Raises:
            HTTPException: If book not found
        """
        book = await BookService.get_book_by_id(book_id, db)

        # Update only provided fields
        update_data = book_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(book, field, value)

        await db.commit()
        await db.refresh(book)

        return book

    @staticmethod
    async def delete_book(book_id: int, db: AsyncSession) -> None:
        """
        Delete a book.

        Args:
            book_id: Book ID
            db: Database session

        Raises:
            HTTPException: If book not found
        """
        book = await BookService.get_book_by_id(book_id, db)

        await db.delete(book)
        await db.commit()

    @staticmethod
    async def get_book_summary(book_id: int, db: AsyncSession) -> dict:
        """
        Get book summary with aggregated ratings.

        Args:
            book_id: Book ID
            db: Database session

        Returns:
            Dictionary with book info, summary, and aggregated ratings

        Raises:
            HTTPException: If book not found
        """
        book = await BookService.get_book_by_id(book_id, db)

        # Get aggregated rating and count
        result = await db.execute(
            select(
                func.avg(Review.rating).label("average_rating"),
                func.count(Review.id).label("total_reviews"),
            ).where(Review.book_id == book_id)
        )
        stats = result.one()

        return {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "summary": book.summary,
            "average_rating": (
                float(stats.average_rating)
                if stats.average_rating
                else 0.0
            ),
            "total_reviews": stats.total_reviews,
        }
