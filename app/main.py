from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import log
from app.api.v1.media import router as media_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    version="1.0.0"
)

# Include routers
app.include_router(media_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    log.info("🚀 Media Service started successfully")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME
    }