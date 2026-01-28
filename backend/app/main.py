import time
from fastapi import FastAPI, Request
from app.api.routes import router as api_router

app = FastAPI(title="Annapurna-AI Backend", version="0.1.0")

# Safety & Audit Middleware
@app.middleware("http")
async def safety_audit_logger(request: Request, call_next):
    start_time = time.time()
    
    # Log Request
    # In production, use structured logging (e.g., structlog)
    print(f"[AUDIT] {request.method} {request.url.path} | Query: {request.query_params}")

    response = await call_next(request)
    
    process_time = time.time() - start_time
    print(f"[AUDIT] Completed in {process_time:.4f}s | Status: {response.status_code}")
    
    return response

# Include Routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "ok", "system": "Annapurna-AI Evidence Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
