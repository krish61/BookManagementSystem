"""Books endpoints for CRUD operations on books."""

from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.book import (
    BookCreate,
    BookUpdate,
    BookResponse,
    BookSummaryResponse,
)
from app.schemas.review import ReviewResponse, ReviewCreate
from app.services.book_service import BookService
from app.services.review_service import ReviewService
from app.services.recommendation_service import RecommendationService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/books", tags=["Books"])


@router.post(
    "", response_model=BookResponse, status_code=status.HTTP_201_CREATED
)
async def create_book(
    book_data: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookResponse:
    """
    Create a new book.

    Args:
        book_data: Book creation data
        db: Database session
        current_user: Authenticated user

    Returns:
        Created book information
    """
    # Create book
    book = await BookService.create_book(book_data, db)

    # Invalidate recommendations cache
    await RecommendationService.invalidate_recommendations_cache()

    return BookResponse.model_validate(book)


@router.get("", response_model=List[BookResponse])
async def get_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[BookResponse]:
    """
    Get all books with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Authenticated user

    Returns:
        List of books
    """
    books = await BookService.get_all_books(db, skip=skip, limit=limit)
    return [BookResponse.model_validate(book) for book in books]


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookResponse:
    """
    Get a specific book by ID.

    Args:
        book_id: Book ID
        db: Database session
        current_user: Authenticated user

    Returns:
        Book information

    Raises:
        HTTPException: If book not found
    """
    book = await BookService.get_book_by_id(book_id, db)
    return BookResponse.model_validate(book)


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookResponse:
    """
    Update a book by ID .

    Args:
        book_id: Book ID
        book_data: Book update data
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated book information

    Raises:
        HTTPException: If book not found
    """
    book = await BookService.update_book(book_id, book_data, db)

    # Invalidate recommendations cache
    await RecommendationService.invalidate_recommendations_cache()

    return BookResponse.model_validate(book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a book by ID .

    Args:
        book_id: Book ID
        db: Database session
        current_user: Authenticated user

    Raises:
        HTTPException: If book not found
    """
    await BookService.delete_book(book_id, db)

    # Invalidate recommendations cache
    await RecommendationService.invalidate_recommendations_cache()


@router.get("/{book_id}/summary", response_model=BookSummaryResponse)
async def get_book_summary(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookSummaryResponse:
    """
    Get book summary with aggregated ratings and review summary.

    Args:
        book_id: Book ID
        db: Database session
        current_user: Authenticated user

    Returns:
        Book summary with ratings and review summary

    Raises:
        HTTPException: If book not found
    """
    # Get book summary with aggregated ratings
    book_data = await BookService.get_book_summary(book_id, db)
    return BookSummaryResponse(**book_data)


@router.get("/{book_id}/reviews", response_model=List[ReviewResponse])
async def get_book_reviews(
    book_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ReviewResponse]:
    """
    Get all reviews for a book.

    Args:
        book_id: Book ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Authenticated user

    Returns:
        List of reviews

    Raises:
        HTTPException: If book not found
    """
    reviews = await ReviewService.get_reviews_for_book(
        book_id, db, skip=skip, limit=limit
    )
    return [ReviewResponse.model_validate(review) for review in reviews]


@router.post(
    "/{book_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_book_review(
    book_id: int,
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReviewResponse:
    """
    Add a review for a book .

    Args:
        book_id: Book ID
        review_data: Review creation data
        db: Database session
        current_user: Authenticated user

    Returns:
        Created review

    Raises:
        HTTPException: If book not found or user already reviewed
    """
    review = await ReviewService.create_review(
        book_id, review_data, current_user.id, db
    )

    # Invalidate recommendations cache since ratings changed
    await RecommendationService.invalidate_recommendations_cache()

    return ReviewResponse.model_validate(review)
