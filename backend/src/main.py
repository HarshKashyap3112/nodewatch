import asyncio
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.alerts.router import router as alerts_router
from src.auth.router import router as auth_router
from src.checks.router import router as checks_router
from src.config import settings
from src.database import engine
from src.exceptions import register_exception_handlers
from src.metrics.router import router as metrics_router
from src.models import Base
from src.scheduler.jobs import scheduler_loop
from src.servers.router import router as servers_router

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("smp_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Database Tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified successfully.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)

    logger.info("Launching Scheduler Background Task...")
    scheduler_task = asyncio.create_task(scheduler_loop())

    yield

    logger.info("Cancelling Scheduler Background Task...")
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Server Monitoring Platform (SMP) API",
    description="Backend collection, alerting, and dashboard query API for personal server infrastructure.",
    version="1.0.0",
    lifespan=lifespan
)

# Exception Handlers
register_exception_handlers(app)

# CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 Routers
api_v1_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(servers_router, prefix=api_v1_prefix)
app.include_router(metrics_router, prefix=api_v1_prefix)
app.include_router(checks_router, prefix=api_v1_prefix)
app.include_router(alerts_router, prefix=api_v1_prefix)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}
