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
uvicorn main:app --reload --host 0.0.0.0 --port 5177
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
