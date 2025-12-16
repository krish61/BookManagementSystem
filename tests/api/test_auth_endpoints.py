"""Unit tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    """Test cases for authentication endpoints."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpass123",
                "full_name": "Test User",
                "role": "user",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "password" not in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test registration with duplicate email."""
        # Register first user
        await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser1",
                "password": "testpass123",
                "role": "user",
            },
        )

        # Try to register with same email
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser2",
                "password": "testpass123",
                "role": "user",
            },
        )

        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "invalid-email",
                "username": "testuser",
                "password": "testpass123",
                "role": "user",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """Test registration with short password."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "short",
                "role": "user",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """Test successful login."""
        # Register user first
        await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpass123",
                "role": "user",
            },
        )

        # Login
        response = await client.post(
            "/auth/login",
            data={
                "username": "testuser",
                "password": "testpass123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_with_email(self, client: AsyncClient):
        """Test login with email instead of username."""
        # Register user first
        await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpass123",
                "role": "user",
            },
        )

        # Login with email
        response = await client.post(
            "/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpass123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """Test login with wrong password."""
        # Register user first
        await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpass123",
                "role": "user",
            },
        )

        # Try to login with wrong password
        response = await client.post(
            "/auth/login",
            data={
                "username": "testuser",
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        assert (
            "Incorrect username or password"
            in response.json()["detail"]
        )

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        response = await client.post(
            "/auth/login",
            data={
                "username": "nonexistent",
                "password": "testpass123",
            },
        )

        assert response.status_code == 401
        assert (
            "Incorrect username or password"
            in response.json()["detail"]
        )
