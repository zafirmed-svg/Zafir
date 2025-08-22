from fastapi import FastAPI, Depends, HTTPException
import signal
import sys
import os
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from core.database import get_session
from models.sql_models import Quote, SurgicalPackage, Procedure, Surgeon
from services.sql_database_service import SQLDatabaseService
from services.logging_service import log_error
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Set up logging
import logging
import os

# Configure logging based on environment
log_level = logging.DEBUG if os.getenv("ENVIRONMENT") != "production" else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Signal handlers
should_exit = False

def handle_exit(signo, frame):
    global should_exit
    logger.info(f"Received signal {signo}. Performing graceful shutdown...")
    should_exit = True

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.debug("Starting up FastAPI application")
    try:
        # Verify database connection
        from core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
            logger.debug("Database connection verified")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.debug("Shutting down FastAPI application")

# Keep-alive event to prevent server shutdown
@app.middleware("http")
async def add_process_time_header(request, call_next):
    global should_exit
    try:
        if should_exit:
            return JSONResponse(
                status_code=503,
                content={"detail": "Server is shutting down"}
            )
        logger.debug(f"Processing request to {request.url.path}")
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise

# Root endpoint for health check
@app.get("/")
async def root():
    logger.debug("Root endpoint called")
    return {"status": "ok", "message": "Zafir Medical API is running"}

# Configurar CORS
origins = []
if os.getenv("ENVIRONMENT") == "production":
    origins = [
        os.getenv("FRONTEND_URL", ""),  # URL del frontend en producción
    ]
else:
    origins = ["*"]  # En desarrollo, permite todos los orígenes

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Quotes endpoints
@app.post("/api/quotes/")
def create_quote(quote_data: dict, session: Session = Depends(get_session)):
    db = SQLDatabaseService(session)
    try:
        quote = db.create_quote(quote_data)
        return quote
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/quotes/{quote_id}")
def get_quote(quote_id: int, session: Session = Depends(get_session)):
    db = SQLDatabaseService(session)
    quote = db.get_quote(quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote

@app.get("/api/quotes/")
async def get_quotes(skip: int = 0, limit: int = 10, session: Session = Depends(get_session)) -> List[Dict[str, Any]]:
    try:
        db = SQLDatabaseService(session)
        quotes = db.get_quotes(skip, limit)
        if quotes is None:
            quotes = []
        return quotes
    except Exception as e:
        log_error("get_quotes", e)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(e)}
        )

# Packages endpoints
@app.post("/api/packages/")
def create_package(package_data: dict, session: Session = Depends(get_session)):
    db = SQLDatabaseService(session)
    try:
        package = db.create_surgical_package(package_data)
        return package
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/packages/{package_id}")
def get_package(package_id: int, session: Session = Depends(get_session)):
    db = SQLDatabaseService(session)
    package = db.get_surgical_package(package_id)
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

@app.get("/api/packages/")
def get_packages(skip: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    db = SQLDatabaseService(session)
    packages = db.get_surgical_packages(skip, limit)
    return packages

# Pricing suggestions endpoint
@app.get("/api/pricing-suggestions/{procedure_name}")
async def get_pricing_suggestions(procedure_name: str, session: Session = Depends(get_session)) -> Dict[str, Any]:
    try:
        db = SQLDatabaseService(session)
        suggestions = db.get_pricing_suggestions(procedure_name)
        return {
            "quote_count": int(suggestions.get("quote_count", 0)),
            "avg_facility_fee": float(suggestions.get("avg_facility_fee", 0)),
            "avg_equipment_costs": float(suggestions.get("avg_equipment_costs", 0)),
            "avg_total_cost": float(suggestions.get("avg_total_cost", 0))
        }
    except Exception as e:
        log_error("get_pricing_suggestions", e)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(e)}
        )

# Procedures endpoints
@app.post("/api/procedures/")
def create_procedure(procedure_data: dict, session: Session = Depends(get_session)):
    db = SQLDatabaseService(session)
    try:
        procedure = db.create_procedure(procedure_data)
        return procedure
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/procedures/{procedure_id}")
def get_procedure(procedure_id: int, session: Session = Depends(get_session)):
    db = SQLDatabaseService(session)
    procedure = db.get_procedure(procedure_id)
    if procedure is None:
        raise HTTPException(status_code=404, detail="Procedure not found")
    return procedure

@app.get("/api/procedures")
async def get_procedures(skip: int = 0, limit: int = 10, session: Session = Depends(get_session)) -> List[Dict[str, Any]]:
    try:
        db = SQLDatabaseService(session)
        procedures = db.get_procedures(skip, limit)
        return [
            {
                "id": procedure.id,
                "name": procedure.name,
                "description": procedure.description,
                "estimated_time": procedure.estimated_time,
                "price": float(procedure.price) if procedure.price else None,
                "created_at": procedure.created_at.isoformat() if procedure.created_at else None
            }
            for procedure in (procedures or [])
        ]
    except Exception as e:
        log_error("get_procedures", e)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(e)}
        )

# Surgeons endpoints
@app.post("/api/surgeons/")
def create_surgeon(surgeon_data: dict, session: Session = Depends(get_session)):
    db = SQLDatabaseService(session)
    try:
        surgeon = db.create_surgeon(surgeon_data)
        return surgeon
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/surgeons/{surgeon_id}")
def get_surgeon(surgeon_id: int, session: Session = Depends(get_session)):
    db = SQLDatabaseService(session)
    surgeon = db.get_surgeon(surgeon_id)
    if surgeon is None:
        raise HTTPException(status_code=404, detail="Surgeon not found")
    return surgeon

@app.get("/api/surgeons")
async def get_surgeons(skip: int = 0, limit: int = 10, session: Session = Depends(get_session)) -> List[Dict[str, Any]]:
    try:
        db = SQLDatabaseService(session)
        surgeons = db.get_surgeons(skip, limit)
        return [
            {
                "id": surgeon.id,
                "name": surgeon.name,
                "specialty": surgeon.specialty,
                "license_number": surgeon.license_number,
                "contact_info": surgeon.contact_info,
                "created_at": surgeon.created_at.isoformat() if surgeon.created_at else None
            }
            for surgeon in (surgeons or [])
        ]
    except Exception as e:
        log_error("get_surgeons", e)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(e)}
        )

# Dashboard endpoint
@app.get("/api/dashboard")
async def get_dashboard(session: Session = Depends(get_session)) -> Dict[str, Any]:
    try:
        db = SQLDatabaseService(session)
        stats = db.get_dashboard_stats()
        if stats is None:
            stats = {
                "total_quotes": 0,
                "recent_quotes": [],
                "top_procedures": [],
                "total_procedures": 0,
                "total_surgeons": 0,
                "total_packages": 0
            }
        return stats
    except Exception as e:
        log_error("get_dashboard", e)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(e)}
        )
