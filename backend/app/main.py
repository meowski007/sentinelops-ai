"""
SentinelOps AI - Main FastAPI Application
AI-Powered Enterprise IT Operations & Incident Response Platform
"""
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.db.session import SessionLocal, get_db, init_db
from app.models.incident import Incident
from app.scripts.seed_data import seed_database

START_TIME = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup structured logging
    setup_logging()
    logger.info("Initializing SentinelOps AI database and services...")
    init_db()

    # Automatically seed synthetic dataset if database has no incidents
    with SessionLocal() as db:
        try:
            count = db.query(Incident).count()
            if count == 0:
                logger.info("Seeding synthetic IT incident dataset...")
                res = seed_database(db, seed=settings.DATA_SEED)
                logger.info(f"Synthetic dataset seeded: {res}")
        except Exception as e:
            logger.warning(f"Could not auto-seed database: {e}")

    logger.info("SentinelOps AI backend is ready and listening.")
    yield
    logger.info("SentinelOps AI backend shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise IT Operations & Incident Response Platform powered by Hybrid RAG and deterministic investigation agents.",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health", tags=["Health"], summary="System health check and uptime probe")
def health_check(db: Session = Depends(get_db)):
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    uptime_sec = round(time.time() - START_TIME, 1)

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "ai_engine_mode": settings.AI_INVESTIGATION_MODE,
        "uptime_seconds": uptime_sec,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

# Register API Router
app.include_router(api_router)
