"""Database base configuration and declarative base."""
from sqlalchemy.orm import declarative_base

# Create declarative base for SQLAlchemy models
Base = declarative_base()

# Import all models here to ensure they are registered with Base.metadata
# This is necessary for migrations and tests
def import_all_models():
    """Import all models to register them with Base.metadata."""
    from app.models import user, book, review  # noqa: F401

# Call this function to ensure models are loaded
import_all_models()
