"""Recommendation service for generating book recommendations with caching."""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.book import Book
from app.models.review import Review
from app.services.cache_service import cache_service


class RecommendationService:
    """Service for generating book recommendations."""

    @staticmethod
    async def get_recommendations(
        db: AsyncSession,
        genre: Optional[str] = None,
        limit: int = 10,
    ) -> tuple[List[Dict[str, Any]], bool]:
        """
        Get book recommendations based on filters with Redis caching.

        Args:
            db: Database session
            genre: Optional genre filter
            limit: Maximum number of recommendations

        Returns:
            Tuple of (list of book recommendations, is_cached flag)
        """
        # Generate cache key
        cache_key = f"recommendations:genre={genre}:limit={limit}"

        # Try to get from cache
        cached_data = await cache_service.get(cache_key)
        if cached_data is not None:
            return cached_data, True

        # Build query with aggregated ratings
        query = (
            select(
                Book.id,
                Book.title,
                Book.author,
                Book.genre,
                func.avg(Review.rating).label("average_rating"),
                func.count(Review.id).label("total_reviews"),
            )
            .outerjoin(Review, Book.id == Review.book_id)
            .group_by(Book.id, Book.title, Book.author, Book.genre)
        )

        # Apply filters
        filters = []
        if genre:
            filters.append(Book.genre.ilike(f"%{genre}%"))

        if filters:
            query = query.where(and_(*filters))

        # Order by rating (books with reviews first, then by rating)
        query = query.order_by(
            func.count(Review.id).desc(), func.avg(Review.rating).desc()
        ).limit(limit)

        # Execute query
        result = await db.execute(query)
        rows = result.all()

        # Format results
        recommendations = [
            {
                "id": row.id,
                "title": row.title,
                "author": row.author,
                "genre": row.genre,
                "average_rating": (
                    float(row.average_rating)
                    if row.average_rating
                    else None
                ),
                "total_reviews": row.total_reviews,
            }
            for row in rows
        ]

        # Cache the results
        await cache_service.set(cache_key, recommendations)

        return recommendations, False

    @staticmethod
    async def invalidate_recommendations_cache() -> None:
        """
        Invalidate all recommendation caches.
        Should be called when books or reviews are created/updated/deleted.
        """
        await cache_service.clear_pattern("recommendations:*")
