# User Service

This service handles user authentication, profile management, and social features for the bar application.

## Features

- User registration with age verification
- JWT-based authentication
- Profile management
- Social features (follow/friend)

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Set up environment variables:
```bash
export SECRET_KEY="your-secret-key"
export DATABASE_URL="postgresql://user:password@localhost:5432/db"
```

3. Run migrations:
```bash
alembic upgrade head
```

4. Start the service:
```bash
poetry run uvicorn src.main:app --reload
```

## API Documentation

Once running, visit `/docs` for the OpenAPI documentation.

## Testing

Run tests with:
```bash
poetry run pytest
```
