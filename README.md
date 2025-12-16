# Book Management System

An intelligent Book Management System built with Python, FastAPI, PostgreSQL, and AI-powered features using Groq's LLaMA 3 model. The system provides RESTful APIs for managing books, reviews, and AI-generated summaries with Redis caching for improved performance.

## Features

- **Book Management**: Full CRUD operations for books
- **Review System**: Users can add, update, and delete reviews with ratings (1-5 stars)
- **AI-Powered Summaries**: Automatic book and review summaries using Groq's LLaMA 3 model
- **Smart Recommendations**: Book recommendations based on genre and ratings with Redis caching
- **JWT Authentication**: Secure authentication with role-based access control (Admin/User)
- **Asynchronous Operations**: Fast, non-blocking database and AI operations
- **Docker Support**: Containerized deployment with Docker Compose
- **Comprehensive Testing**: Unit tests with >80% code coverage
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## Tech Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Caching**: Redis
- **AI Model**: Groq API 
- **Authentication**: JWT with bcrypt password hashing
- **Testing**: Pytest with async support
- **Containerization**: Docker & Docker Compose

## Project Structure

```
BookManagementSystemClaude/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── books.py         # Book CRUD endpoints
│   │       └── ai.py            # AI and recommendations
│   ├── core/
│   │   ├── config.py            # Application configuration
│   │   ├── security.py          # JWT and password utilities
│   │   └── dependencies.py      # FastAPI dependencies
│   ├── db/
│   │   ├── base.py              # SQLAlchemy base
│   │   └── session.py           # Database session management
│   ├── models/
│   │   ├── user.py              # User model
│   │   ├── book.py              # Book model
│   │   └── review.py            # Review model
│   ├── schemas/
│   │   ├── user.py              # User Pydantic schemas
│   │   ├── book.py              # Book Pydantic schemas
│   │   ├── review.py            # Review Pydantic schemas
│   │   └── ai.py                # AI-related schemas
│   ├── services/
│   │   ├── auth_service.py      # Authentication logic
│   │   ├── book_service.py      # Book business logic
│   │   ├── review_service.py    # Review business logic
│   │   ├── ai_service.py        # AI integration (Groq)
│   │   ├── cache_service.py     # Redis caching
│   │   └── recommendation_service.py  # Recommendations
│   └── main.py                  # FastAPI application
├── alembic/
│   ├── versions/                # Database migrations
│   └── env.py                   # Alembic configuration
├── tests/
│   ├── api/                 # API endpoint tests
│   └── conftest.py              # Pytest configuration
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
├── .env.example
└── README.md
```

## Prerequisites

- Python 3.11+
- Docker & Docker Compose 
- Groq API Key 

## Installation & Setup

### Option 1: Docker Compose

1. **Clone the repository**
   ```bash
   cd /BookManagementSystem
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file and add values**

4. **Start all services**
   ```bash
   docker-compose up --build
   ```

5. **Access the application**
   - Swagger Docs: http://localhost:8000/docs

### Option 2: Local Development

1. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup PostgreSQL and Redis**
   - Install PostgreSQL 15+
   - Install Redis 7+
   - Create database

4. **Create `.env` file**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and Groq API key
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## Running Tests

### Run all tests with coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term
```
