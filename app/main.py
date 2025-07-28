from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.core.error_handlers import http_exception_handler, validation_exception_handler, generic_exception_handler
from app.core.rate_limiter import setup_rate_limiter
from app.routers import roles, tracking_objects, accounts, organizations, tags, alarms, routes
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from app.core.metrics import metrics_router
from app.database.db_init import init_database

settings = get_settings()
logger = get_logger(__name__)

app = FastAPI(title="Trakr Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
setup_rate_limiter(app)

# Exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Routers
app.include_router(roles.router)
app.include_router(tracking_objects.router)
app.include_router(accounts.router)
app.include_router(organizations.router)
app.include_router(tags.router)
app.include_router(alarms.router)
app.include_router(routes.router)
app.include_router(metrics_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Initializing database...")
    try:
        init_database()
        logger.info("Database initialization completed successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't raise the exception - allow the app to start even if database is not available
        # The app will handle database connection errors gracefully in the services

@app.get("/health")
def health_check():
    return {"status": "ok"}
