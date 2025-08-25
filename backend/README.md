# Backend (Django)

This folder contains a Django REST backend that mirrors the original FastAPI `server.py` endpoints.

Quick start (local):

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Create a `.env` in `backend/` with Postgres credentials:

```
POSTGRES_DB=zafir_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DJANGO_SECRET_KEY=change-me
```

3. Run migrations and start the server:

```powershell
cd backend
python manage.py migrate
python manage.py runserver
```

Upload PDFs at `POST /api/upload-pdf/` with form field `file`.
# Zafir Backend

FastAPI backend service for Zafir Medical platform.

## Project Structure

```
backend/
├── main.py           # Main FastAPI application
├── core/            # Core functionality and configurations
├── models/          # Database models
├── services/        # Business logic services
└── gunicorn_config.py  # Gunicorn production server configuration
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn backend.asgi:application --reload --host 0.0.0.0 --port 5177
```

## Production

The application uses Gunicorn with Uvicorn workers in production:

```bash
gunicorn -c gunicorn_config.py
```

## Environment Variables

- `PORT`: Server port (set by Render)
- `ENVIRONMENT`: "development" or "production"
- `DATABASE_URL`: Database connection string
