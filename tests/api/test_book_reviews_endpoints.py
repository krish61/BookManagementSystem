"""Unit tests for book reviews and summary endpoints."""

import pytest
from httpx import AsyncClient


class TestBookReviewsEndpoints:
    """Test cases for book reviews and summary endpoints."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient) -> dict:
        """Get authentication headers for protected endpoints."""
        # Register and login user
        await client.post(
            "/auth/register",
            json={
                "email": "reviewuser@example.com",
                "username": "reviewuser",
                "password": "testpass123",
                "role": "user",
            },
        )

        response = await client.post(
            "/auth/login",
            data={
                "username": "reviewuser",
                "password": "testpass123",
            },
        )

        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    async def sample_book_id(
        self, client: AsyncClient, auth_headers: dict
    ) -> int:
        """Create a sample book and return its ID."""
        response = await client.post(
            "/books",
            json={
                "title": "Sample Book for Reviews",
                "author": "Test Author",
                "year_published": 2023,
                "genre": "Fiction",
                "description": "A sample book for testing reviews",
            },
            headers=auth_headers,
        )
        return response.json()["id"]

    @pytest.mark.asyncio
    async def test_get_book_reviews_empty(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_book_id: int,
    ):
        """Test getting reviews when book has no reviews."""
        response = await client.get(
            f"/books/{sample_book_id}/reviews", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_create_review_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_book_id: int,
    ):
        """Test successful review creation."""
        response = await client.post(
            f"/books/{sample_book_id}/reviews",
            json={
                "rating": 5,
                "review_text": "Excellent book! Highly recommended.",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 5
        assert (
            data["review_text"] == "Excellent book! Highly recommended."
        )
        assert data["book_id"] == sample_book_id
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_review_invalid_rating(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_book_id: int,
    ):
        """Test review creation with invalid rating."""
        # Rating too low
        response = await client.post(
            f"/books/{sample_book_id}/reviews",
            json={
                "rating": 0,
                "review_text": "Bad rating",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

        # Rating too high
        response = await client.post(
            f"/books/{sample_book_id}/reviews",
            json={
                "rating": 6,
                "review_text": "Bad rating",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_review_for_nonexistent_book(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating a review for a non-existent book."""
        response = await client.post(
            "/books/999/reviews",
            json={
                "rating": 5,
                "review_text": "Great book!",
            },
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_duplicate_review(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_book_id: int,
    ):
        """Test that user cannot review the same book twice."""
        # Create first review
        await client.post(
            f"/books/{sample_book_id}/reviews",
            json={
                "rating": 5,
                "review_text": "First review",
            },
            headers=auth_headers,
        )

        # Try to create another review for the same book
        response = await client.post(
            f"/books/{sample_book_id}/reviews",
            json={
                "rating": 4,
                "review_text": "Second review",
            },
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "already reviewed" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_book_reviews_with_data(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_book_id: int,
    ):
        """Test getting reviews when book has reviews."""
        # Create a review
        await client.post(
            f"/books/{sample_book_id}/reviews",
            json={
                "rating": 5,
                "review_text": "Great book!",
            },
            headers=auth_headers,
        )

        # Get reviews
        response = await client.get(
            f"/books/{sample_book_id}/reviews", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["rating"] == 5
        assert data[0]["review_text"] == "Great book!"

    @pytest.mark.asyncio
    async def test_get_book_summary_no_reviews(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_book_id: int,
    ):
        """Test getting book summary when book has no reviews."""
        response = await client.get(
            f"/books/{sample_book_id}/summary", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_book_id
        assert data["title"] == "Sample Book for Reviews"
        assert data["average_rating"] == 0.0
        assert data["total_reviews"] == 0

    @pytest.mark.asyncio
    async def test_get_book_summary_with_reviews(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_book_id: int,
    ):
        """Test getting book summary with reviews and ratings."""
        # Create multiple reviews
        await client.post(
            f"/books/{sample_book_id}/reviews",
            json={
                "rating": 5,
                "review_text": "Excellent!",
            },
            headers=auth_headers,
        )

        # Create another user and review
        await client.post(
            "/auth/register",
            json={
                "email": "user2@example.com",
                "username": "user2",
                "password": "testpass123",
                "role": "user",
            },
        )

        login_response = await client.post(
            "/auth/login",
            data={
                "username": "user2",
                "password": "testpass123",
            },
        )

        user2_token = login_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        await client.post(
            f"/books/{sample_book_id}/reviews",
            json={
                "rating": 3,
                "review_text": "Average book",
            },
            headers=user2_headers,
        )

        # Get summary
        response = await client.get(
            f"/books/{sample_book_id}/summary", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_reviews"] == 2
        assert data["average_rating"] == 4.0  # (5 + 3) / 2

    @pytest.mark.asyncio
    async def test_get_book_summary_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting summary for a non-existent book."""
        response = await client.get(
            "/books/999/summary", headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_reviews_unauthorized_access(
        self, client: AsyncClient, sample_book_id: int
    ):
        """Test that review endpoints require authentication."""
        # GET /books/{id}/reviews
        response = await client.get(f"/books/{sample_book_id}/reviews")
        assert response.status_code == 401

        # POST /books/{id}/reviews
        response = await client.post(
            f"/books/{sample_book_id}/reviews",
            json={
                "rating": 5,
                "review_text": "Test",
            },
        )
        assert response.status_code == 401

        # GET /books/{id}/summary
        response = await client.get(f"/books/{sample_book_id}/summary")
        assert response.status_code == 401
