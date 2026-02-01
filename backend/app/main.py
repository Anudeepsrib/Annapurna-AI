import time
import structlog
import os
import contextlib
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api.routes import router as api_router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter
from app.core.database import create_db_and_tables

# Load environment variables from .env file if present
load_dotenv()

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
    # Startup
    create_db_and_tables()
    yield
    # Shutdown
    
app = FastAPI(title="Annapurna-AI Backend", version="0.1.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Configure CORS
# In production, set FRONTEND_URL to your Vercel domain (e.g., https://annapurna-ai.vercel.app)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    # allow_origins=["*"], # Uncomment if you have issues with specific domains in testing
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

    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    if request.url.path != "/":
        log.info("Request Completed", 
                duration=f"{process_time:.4f}s", 
                status=response.status_code)
    
    return response

# Include Routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def health_check():
    mode = "AI" if os.getenv("OPENAI_API_KEY") else "Mock"
    return {"status": "ok", "system": "Annapurna-AI Evidence Backend", "mode": mode}

if __name__ == "__main__":
    import uvicorn
    is_dev = os.getenv("ENV") != "production"
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=is_dev)
