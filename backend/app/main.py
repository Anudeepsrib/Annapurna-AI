import contextlib
import time

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.exceptions import AppError, app_exception_handler, general_exception_handler

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables (Async)
    await create_db_and_tables()
    yield
    # Shutdown


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Register Global Exception Handlers
app.add_exception_handler(AppError, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Configure CORS - restricted for local desktop safety
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Safety & Audit Middleware
@app.middleware("http")
async def safety_audit_logger(request: Request, call_next):
    start_time = time.time()

    # Log only route metadata by default. Dietary text and query strings can be sensitive.
    log = logger.bind(method=request.method, path=request.url.path)
    # Don't create excessive noise on health checks
    if request.url.path not in {"/", "/health", f"{settings.API_V1_STR}/health"}:
        log.info("Request started")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        if request.url.path not in {"/", "/health", f"{settings.API_V1_STR}/health"}:
            log.info(
                "Request completed",
                duration=f"{process_time:.4f}s",
                status=response.status_code,
            )
        return response
    except Exception as e:
        # Ensure middleware doesn't swallow errors before they reach exception handler
        # But log the failure time
        process_time = time.time() - start_time
        log.error("Request failed", duration=f"{process_time:.4f}s", error=e.__class__.__name__)
        raise e


# Include Routes
app.include_router(api_router, prefix=settings.API_V1_STR)


def health_payload():
    return {
        "status": "ok",
        "system": "Annapurna-AI Local Backend",
        "mode": settings.APP_ENV,
        "external_network_enabled": settings.ENABLE_EXTERNAL_NETWORK,
        "optional_fetchers": {
            "usda": settings.ENABLE_USDA,
            "pubmed": settings.ENABLE_PUBMED,
        },
    }


@app.get("/")
def root_health_check():
    return health_payload()


@app.get("/health")
def health_check():
    return health_payload()


if __name__ == "__main__":
    import uvicorn

    # Use config settings for reload behavior
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
