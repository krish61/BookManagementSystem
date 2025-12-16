"""Unit tests for book CRUD endpoints."""

import pytest
from httpx import AsyncClient


class TestBookEndpoints:
    """Test cases for book CRUD endpoints."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient) -> dict:
        """Get authentication headers for protected endpoints."""
        # Register and login user
        await client.post(
            "/auth/register",
            json={
                "email": "bookuser@example.com",
                "username": "bookuser",
                "password": "testpass123",
                "role": "user",
            },
        )

        response = await client.post(
            "/auth/login",
            data={
                "username": "bookuser",
                "password": "testpass123",
            },
        )

        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_create_book_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test successful book creation."""
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

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Atomic Habits"
        assert data["author"] == "James Clear"
        assert data["genre"] == "Self-help / Personal Development"
        assert data["year_published"] == 2018
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_book_unauthorized(self, client: AsyncClient):
        """Test book creation without authentication."""
        response = await client.post(
            "/books",
            json={
                "title": "Atomic Habits",
                "author": "James Clear",
                "genre": "Self-help / Personal Development",
                "year_published": 2018,
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_book_invalid_data(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test book creation with invalid data."""
        response = await client.post(
            "/books",
            json={
                "title": "",  # Empty title
                "author": "Test Author",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_all_books_with_data(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting all books with data."""
        # Create multiple books
        books = [
            {
                "title": f"Book {i}",
                "author": f"Author {i}",
                "year_published": 2020 + i,
                "genre": "Fiction",
            }
            for i in range(5)
        ]

        for book_data in books:
            await client.post(
                "/books", json=book_data, headers=auth_headers
            )

        # Get all books
        response = await client.get("/books", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 6
        assert all("id" in book for book in data)

    @pytest.mark.asyncio
    async def test_get_all_books_pagination(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting books with pagination."""
        # Create 15 books
        for i in range(15):
            await client.post(
                "/books",
                json={
                    "title": f"Book {i}",
                    "author": f"Author {i}",
                    "year_published": 2020,
                    "genre": "Fiction",
                },
                headers=auth_headers,
            )

        # Get first page (default limit is 10)
        response = await client.get(
            "/books?skip=0&limit=10", headers=auth_headers
        )
        assert response.status_code == 200
        assert len(response.json()) == 10

        # Get second page
        response = await client.get(
            "/books?skip=10&limit=10", headers=auth_headers
        )
        assert response.status_code == 200
        assert len(response.json()) == 6

    @pytest.mark.asyncio
    async def test_get_book_by_id_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting a specific book by ID."""
        # Create a book
        create_response = await client.post(
            "/books",
            json={
                "title": "Test Book",
                "author": "Test Author",
                "year_published": 2023,
                "genre": "Fiction",
            },
            headers=auth_headers,
        )

        book_id = create_response.json()["id"]

        # Get the book
        response = await client.get(
            f"/books/{book_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == book_id
        assert data["title"] == "Test Book"
        assert data["author"] == "Test Author"

    @pytest.mark.asyncio
    async def test_get_book_by_id_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting a non-existent book."""
        response = await client.get("/books/999", headers=auth_headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_book_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test successful book update."""
        # Create a book
        create_response = await client.post(
            "/books",
            json={
                "title": "Original Title",
                "author": "Original Author",
                "year_published": 2023,
                "genre": "Fiction",
            },
            headers=auth_headers,
        )

        book_id = create_response.json()["id"]

        # Update the book
        response = await client.put(
            f"/books/{book_id}",
            json={
                "title": "Updated Title",
                "author": "Updated Author",
                "genre": "Non-Fiction",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["author"] == "Updated Author"
        assert data["genre"] == "Non-Fiction"

    @pytest.mark.asyncio
    async def test_update_book_partial(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test partial book update."""
        # Create a book
        create_response = await client.post(
            "/books",
            json={
                "title": "Original Title",
                "author": "Original Author",
                "year_published": 2023,
                "genre": "Fiction",
            },
            headers=auth_headers,
        )

        book_id = create_response.json()["id"]

        # Update only the title
        response = await client.put(
            f"/books/{book_id}",
            json={"title": "Updated Title Only"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title Only"
        assert data["author"] == "Original Author"  # Unchanged

    @pytest.mark.asyncio
    async def test_update_book_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating a non-existent book."""
        response = await client.put(
            "/books/999",
            json={"title": "Updated Title"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_book_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test successful book deletion."""
        # Create a book
        create_response = await client.post(
            "/books",
            json={
                "title": "Book to Delete",
                "author": "Test Author",
                "year_published": 2023,
                "genre": "Fiction",
            },
            headers=auth_headers,
        )

        book_id = create_response.json()["id"]

        # Delete the book
        response = await client.delete(
            f"/books/{book_id}", headers=auth_headers
        )

        assert response.status_code == 204

        # Verify book is deleted
        get_response = await client.get(
            f"/books/{book_id}", headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_book_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test deleting a non-existent book."""
        response = await client.delete(
            "/books/999", headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_books_unauthorized_access(self, client: AsyncClient):
        """Test that all book endpoints require authentication."""
        # GET /books
        response = await client.get("/books")
        assert response.status_code == 401

        # GET /books/{id}
        response = await client.get("/books/1")
        assert response.status_code == 401

        # PUT /books/{id}
        response = await client.put("/books/1", json={"title": "Test"})
        assert response.status_code == 401

        # DELETE /books/{id}
        response = await client.delete("/books/1")
        assert response.status_code == 401
