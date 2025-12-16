"""AI and recommendations endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.ai import (
    GenerateSummaryRequest,
    GenerateSummaryResponse,
    RecommendationResponse,
    BookRecommendation,
)
from app.services.ai_service import ai_service
from app.services.book_service import BookService
from app.services.recommendation_service import RecommendationService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(tags=["AI & Recommendations"])


@router.post(
    "/generate-summary", response_model=GenerateSummaryResponse
)
async def generate_summary(
    request: GenerateSummaryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GenerateSummaryResponse:
    """
    Generate a summary for given book content using AI.

    Args:
        request: Summary generation request with content
        current_user: Authenticated user

    Returns:
        Generated summary and word count

    Raises:
        HTTPException: If AI service fails
    """

    book = await BookService.get_book_by_id(request.book_id, db)

    try:
        summary = await ai_service.generate_summary(request.content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(e)}",
        )

    book.summary = summary
    await db.commit()
    await db.refresh(book)

    word_count = len(summary.split())

    return GenerateSummaryResponse(
        summary=summary, word_count=word_count
    )


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    genre: str = Query(None, description="Filter by genre"),
    limit: int = Query(
        10, ge=1, le=50, description="Number of recommendations"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecommendationResponse:
    """
    Get book recommendations based on preferences with Redis caching.

    Args:
        genre: Optional genre filter
        min_rating: Optional minimum rating filter
        limit: Number of recommendations to return
        db: Database session
        current_user: Authenticated user

    Returns:
        List of book recommendations with cache status
    """
    recommendations, is_cached = (
        await RecommendationService.get_recommendations(
            db=db,
            genre=genre,
            limit=limit,
        )
    )

    return RecommendationResponse(
        recommendations=[
            BookRecommendation(**rec) for rec in recommendations
        ],
        total=len(recommendations),
        cached=is_cached,
    )
