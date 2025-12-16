"""Authentication service for user registration and login."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, Token
from app.core.security import verify_password, get_password_hash, create_access_token


class AuthService:
    """Service for handling authentication operations."""

    @staticmethod
    async def register_user(user_data: UserCreate, db: AsyncSession) -> User:
        """
        Register a new user.

        Args:
            user_data: User registration data
            db: Database session

        Returns:
            The created user

        Raises:
            HTTPException: If email or username already exists
        """
        # Check if email already exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Check if username already exists
        result = await db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    @staticmethod
    async def authenticate_user(
        username: str, password: str, db: AsyncSession
    ) -> Optional[User]:
        """
        Authenticate a user by username and password.

        Args:
            username: Username or email
            password: Plain text password
            db: Database session

        Returns:
            The authenticated user or None if authentication fails
        """
        # Try to find user by username or email
        result = await db.execute(
            select(User).where(
                (User.username == username) | (User.email == username)
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def login(username: str, password: str, db: AsyncSession) -> Token:
        """
        Login a user and return an access token.

        Args:
            username: Username or email
            password: Plain text password
            db: Database session

        Returns:
            JWT access token

        Raises:
            HTTPException: If authentication fails
        """
        user = await AuthService.authenticate_user(username, password, db)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value}
        )

        return Token(access_token=access_token, token_type="bearer")
