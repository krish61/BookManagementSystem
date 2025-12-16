"""Review service for CRUD operations on reviews."""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.review import Review
from app.models.book import Book
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewService:
    """Service for handling review-related operations."""

    @staticmethod
    async def create_review(
        book_id: int, review_data: ReviewCreate, user_id: int, db: AsyncSession
    ) -> Review:
        """
        Create a new review for a book.

        Args:
            book_id: Book ID
            review_data: Review creation data
            user_id: User ID creating the review
            db: Database session

        Returns:
            The created review

        Raises:
            HTTPException: If book not found
        """
        # Verify book exists
        result = await db.execute(select(Book).where(Book.id == book_id))
        book = result.scalar_one_or_none()

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {book_id} not found",
            )

        # Check if user already reviewed this book
        result = await db.execute(
            select(Review).where(
                (Review.book_id == book_id) & (Review.user_id == user_id)
            )
        )
        existing_review = result.scalar_one_or_none()

        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this book",
            )

        # Create new review
        new_review = Review(
            book_id=book_id,
            user_id=user_id,
            review_text=review_data.review_text,
            rating=review_data.rating,
        )

        db.add(new_review)
        await db.commit()
        await db.refresh(new_review)

        return new_review

    @staticmethod
    async def get_reviews_for_book(
        book_id: int, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Review]:
        """
        Get all reviews for a book.

        Args:
            book_id: Book ID
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of reviews

        Raises:
            HTTPException: If book not found
        """
        # Verify book exists
        result = await db.execute(select(Book).where(Book.id == book_id))
        book = result.scalar_one_or_none()

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {book_id} not found",
            )

        # Get reviews
        result = await db.execute(
            select(Review)
            .where(Review.book_id == book_id)
            .offset(skip)
            .limit(limit)
            .order_by(Review.created_at.desc())
        )
        reviews = result.scalars().all()

        return list(reviews)

    @staticmethod
    async def get_review_by_id(review_id: int, db: AsyncSession) -> Review:
        """
        Get a review by ID.

        Args:
            review_id: Review ID
            db: Database session

        Returns:
            The review

        Raises:
            HTTPException: If review not found
        """
        result = await db.execute(select(Review).where(Review.id == review_id))
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review with id {review_id} not found",
            )

        return review

    @staticmethod
    async def update_review(
        review_id: int, review_data: ReviewUpdate, user_id: int, db: AsyncSession
    ) -> Review:
        """
        Update a review (only by the review author).

        Args:
            review_id: Review ID
            review_data: Review update data
            user_id: User ID requesting the update
            db: Database session

        Returns:
            The updated review

        Raises:
            HTTPException: If review not found or user not authorized
        """
        review = await ReviewService.get_review_by_id(review_id, db)

        # Check if user is the author
        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own reviews",
            )

        # Update only provided fields
        update_data = review_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(review, field, value)

        await db.commit()
        await db.refresh(review)

        return review

    @staticmethod
    async def delete_review(review_id: int, user_id: int, db: AsyncSession) -> None:
        """
        Delete a review (only by the review author).

        Args:
            review_id: Review ID
            user_id: User ID requesting the deletion
            db: Database session

        Raises:
            HTTPException: If review not found or user not authorized
        """
        review = await ReviewService.get_review_by_id(review_id, db)

        # Check if user is the author
        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews",
            )

        await db.delete(review)
        await db.commit()
