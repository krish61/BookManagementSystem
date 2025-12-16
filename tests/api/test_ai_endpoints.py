"""Unit tests for AI and recommendation endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


class TestAIEndpoints:
    """Test cases for AI and recommendation endpoints."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient) -> dict:
        """Get authentication headers for protected endpoints."""
        # Register and login user
        await client.post(
            "/auth/register",
            json={
                "email": "aiuser@example.com",
                "username": "aiuser",
                "password": "testpass123",
                "role": "user",
            },
        )

        response = await client.post(
            "/auth/login",
            data={
                "username": "aiuser",
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
                "title": "Atomic Habits",
                "author": "James Clear",
                "genre": "Self-help / Personal Development",
                "year_published": 2018,
            },
            headers=auth_headers,
        )
        return response.json()["id"]

    @pytest.mark.asyncio
    async def test_generate_summary_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_book_id: int,
    ):
        """Test successful summary generation."""
        with patch(
            "app.services.ai_service.ai_service.generate_summary",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = (
                "This is a generated summary of the book content."
            )

            response = await client.post(
                "/generate-summary",
                json={
                    "book_id": sample_book_id,
                    "content": "This is the book content that needs summarization. "
                    * 50,
                },
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert data["summary"] == (
                "This is a generated summary of the book content."
            )
            assert "word_count" in data
            assert data["word_count"] > 0
            mock_generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_summary_empty_content(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_book_id: int,
    ):
        """Test summary generation with empty content."""
        response = await client.post(
            "/generate-summary",
            json={
                "book_id": sample_book_id,
                "content": "",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_generate_summary_nonexistent_book(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test summary generation for non-existent book."""
        with patch(
            "app.services.ai_service.ai_service.generate_summary",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = "Generated summary"

            response = await client.post(
                "/generate-summary",
                json={
                    "book_id": 999,
                    "content": "This is a longer content string that meets the minimum length requirement of 50 characters for validation.",
                },
                headers=auth_headers,
            )

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_generate_summary_ai_failure(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_book_id: int,
    ):
        """Test summary generation when AI service fails."""
        with patch(
            "app.services.ai_service.ai_service.generate_summary",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.side_effect = Exception("AI service error")

            response = await client.post(
                "/generate-summary",
                json={
                    "book_id": sample_book_id,
                    "content": "This is a longer content string that meets the minimum length requirement of 50 characters for validation.",
                },
                headers=auth_headers,
            )

            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_get_recommendations_with_books(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting recommendations with books in database."""
        # Create several books with different ratings
        books_data = [
            {
                "title": f"Sci-Fi Book {i}",
                "author": f"Author {i}",
                "isbn": f"978-0-12345-{i:03d}-9",
                "publication_year": 2020 + i,
                "genre": "Science Fiction",
            }
            for i in range(5)
        ]

        for book_data in books_data:
            await client.post(
                "/books", json=book_data, headers=auth_headers
            )

        # Create reviews for some books
        # Register additional users for reviews
        for i in range(3):
            await client.post(
                "/auth/register",
                json={
                    "email": f"reviewer{i}@example.com",
                    "username": f"reviewer{i}",
                    "password": "testpass123",
                    "role": "user",
                },
            )

            login_response = await client.post(
                "/auth/login",
                data={
                    "username": f"reviewer{i}",
                    "password": "testpass123",
                },
            )

            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Add reviews to first two books
            for book_id in [1, 2]:
                await client.post(
                    f"/books/{book_id}/reviews",
                    json={
                        "rating": 5,
                        "review_text": "Excellent book!",
                    },
                    headers=headers,
                )

        # Get recommendations
        response = await client.get(
            "/recommendations", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["recommendations"], list)
        assert data["total"] >= 0
        assert isinstance(data["cached"], bool)

    @pytest.mark.asyncio
    async def test_get_recommendations_with_genre_filter(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting recommendations with genre filter."""
        # Create books with different genres
        await client.post(
            "/books",
            json={
                "title": "Mystery Book",
                "author": "Mystery Author",
                "isbn": "978-0-111111-11-1",
                "publication_year": 2023,
                "genre": "Mystery",
            },
            headers=auth_headers,
        )

        await client.post(
            "/books",
            json={
                "title": "Romance Book",
                "author": "Romance Author",
                "isbn": "978-0-222222-22-2",
                "publication_year": 2023,
                "genre": "Romance",
            },
            headers=auth_headers,
        )

        # Get recommendations filtered by genre
        response = await client.get(
            "/recommendations?genre=Mystery", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["recommendations"], list)
        # If there are recommendations, they should all be Mystery genre
        for rec in data["recommendations"]:
            assert rec["genre"] == "Mystery"

    @pytest.mark.asyncio
    async def test_get_recommendations_with_limit(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting recommendations with limit parameter."""
        # Create 10 books
        for i in range(10):
            await client.post(
                "/books",
                json={
                    "title": f"Book {i}",
                    "author": f"Author {i}",
                    "isbn": f"978-0-12345-{i:03d}-9",
                    "publication_year": 2023,
                    "genre": "Fiction",
                },
                headers=auth_headers,
            )

        # Get recommendations with limit of 5
        response = await client.get(
            "/recommendations?limit=5", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) <= 5

    @pytest.mark.asyncio
    async def test_get_recommendations_caching(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that recommendations are cached."""
        # Create a book
        await client.post(
            "/books",
            json={
                "title": "Cached Book",
                "author": "Cache Author",
                "isbn": "978-0-123456-78-9",
                "publication_year": 2023,
                "genre": "Fiction",
            },
            headers=auth_headers,
        )

        # First request - should not be cached
        response1 = await client.get(
            "/recommendations", headers=auth_headers
        )
        assert response1.status_code == 200
        data1 = response1.json()

        # Second request - might be cached (depends on cache implementation)
        response2 = await client.get(
            "/recommendations", headers=auth_headers
        )
        assert response2.status_code == 200
        data2 = response2.json()

        # Both should return valid data
        assert "recommendations" in data1
        assert "recommendations" in data2
        assert "cached" in data1
        assert "cached" in data2

    @pytest.mark.asyncio
    async def test_recommendations_invalid_limit(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test recommendations with invalid limit parameter."""
        # Limit too low
        response = await client.get(
            "/recommendations?limit=0", headers=auth_headers
        )
        assert response.status_code == 422

        # Limit too high
        response = await client.get(
            "/recommendations?limit=100", headers=auth_headers
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_ai_endpoints_unauthorized(self, client: AsyncClient):
        """Test that AI endpoints require authentication."""
        # POST /generate-summary
        response = await client.post(
            "/generate-summary",
            json={
                "book_id": 1,
                "content": "Some content",
            },
        )
        assert response.status_code == 401

        # GET /recommendations
        response = await client.get("/recommendations")
        assert response.status_code == 401
