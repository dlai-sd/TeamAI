"""
Assessment Tool Backend - Pure JSON API
Designed for maximum UI flexibility - backend doesn't know about UI structure
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
from pathlib import Path

# Import routers (will create these next)
# from app.api.v1 import assessment, discovery, analysis, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Assessment Tool Backend Starting...")
    print("📁 Loading configuration files...")
    
    # Load chapter configuration
    config_path = Path(__file__).parent.parent / "config" / "chapter-flow.json"
    with open(config_path) as f:
        app.state.chapter_config = json.load(f)
    
    # Load UI configuration
    ui_config_path = Path(__file__).parent.parent / "config" / "ui-config.json"
    with open(ui_config_path) as f:
        app.state.ui_config = json.load(f)
    
    print(f"✅ Loaded {len(app.state.chapter_config['chapters'])} chapters")
    print("🎯 Backend ready for UI connections")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")

# Initialize FastAPI
app = FastAPI(
    title="Yashus Assessment Tool API",
    description="Pure JSON API for digital assessment - UI agnostic",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Allow any frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint - API information"""
    return {
        "name": "Yashus Assessment Tool API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "config": "/config",
            "assessment": "/api/v1/assessment",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """Health check for monitoring"""
    return {
        "status": "healthy",
        "service": "assessment-backend",
        "timestamp": "2025-12-19T00:00:00Z"
    }

@app.get("/config/chapters")
def get_chapter_config():
    """
    Return chapter configuration - UI reads this to know what to render
    
    This is the key to UI flexibility:
    - UI doesn't hardcode chapter structure
    - UI reads this JSON and renders accordingly
    - Change this JSON = change entire flow without touching UI code
    """
    return app.state.chapter_config

@app.get("/config/ui")
def get_ui_config():
    """
    Return UI configuration (themes, spacing, colors)
    
    UI reads this to style itself - no hardcoded colors in frontend
    """
    ui_config_path = Path(__file__).parent.parent.parent / "config" / "ui-config.json"
    with open(ui_config_path) as f:
        return json.load(f)

# API v1 Routes
from app.api.v1 import assessment
app.include_router(assessment.router, prefix="/api/v1/assessment", tags=["assessment"])
# app.include_router(discovery.router, prefix="/api/v1/discovery", tags=["discovery"])
# app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
# app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
