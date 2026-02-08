import time
import structlog
import os
import contextlib
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter
from app.core.database import create_db_and_tables
from app.core.config import settings
from app.core.exceptions import AppError, app_exception_handler, general_exception_handler

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
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
    lifespan=lifespan
)

# Connect Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register Global Exception Handlers
app.add_exception_handler(AppError, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Configure CORS
origins = settings.BACKEND_CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Safety & Audit Middleware
@app.middleware("http")
async def safety_audit_logger(request: Request, call_next):
    start_time = time.time()
    
    # Log Request
    log = logger.bind(
        method=request.method,
        path=request.url.path,
        query=str(request.query_params)
    )
    # Don't create excessive noise on health checks
    if request.url.path != "/":
        log.info("Request Started")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        if request.url.path != "/":
            log.info("Request Completed", 
                    duration=f"{process_time:.4f}s", 
                    status=response.status_code)
        return response
    except Exception as e:
        # Ensure middleware doesn't swallow errors before they reach exception handler
        # But log the failure time
        process_time = time.time() - start_time
        log.error("Request Failed", duration=f"{process_time:.4f}s", error=str(e))
        raise e

# Include Routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def health_check():
    mode = "AI" if settings.OPENAI_API_KEY else "Mock"
    return {"status": "ok", "system": "Annapurna-AI Evidence Backend", "mode": mode}

if __name__ == "__main__":
    import uvicorn
    # Use config settings for reload behavior
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
