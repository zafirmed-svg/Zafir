from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import logging

from .core.config import settings, Database
from .api.endpoints import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the main app
app = FastAPI(
    title="Sistema de Gestión de Cotizaciones Quirúrgicas",
    description="API para la gestión de cotizaciones quirúrgicas",
    version="1.0.0"
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Bienvenido al Sistema de Gestión de Cotizaciones Quirúrgicas",
        "docs_url": "/docs",
        "api_prefix": "/api"
    }

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # Permitir todos los orígenes temporalmente
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include the router
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    Database.close_client()
