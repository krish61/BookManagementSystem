"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.endpoints import auth, books, ai
from app.services.cache_service import cache_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    await cache_service.connect()
    logger.info("Connected to cache service")

    yield

    # Shutdown
    await cache_service.disconnect()
    logger.info("Disconnected from cache service")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Book Management System with AI-powered summaries and recommendations",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    Root endpoint with API information.

    Returns:
        API information
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
    }


# Include routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(ai.router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.

    Args:
        request: The request that caused the exception
        exc: The exception that was raised

    Returns:
        JSON error response
    """
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method},
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": (
                str(exc)
                if settings.DEBUG
                else "An unexpected error occurred"
            ),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
