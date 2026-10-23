from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.supabase import is_supabase_configured
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Emergency Blood Donation Coordination Platform for Pakistan",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for Frontend Vite app
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 endpoints
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs": "/docs",
        "supabase_connected": is_supabase_configured(),
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "supabase": "connected" if is_supabase_configured() else "using_local_fallback",
    }
