"""
Enhanced main.py with all improvements integrated
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
from pathlib import Path
import os

# Import middleware and utilities
from app.middleware.rate_limiter import rate_limit_middleware
from app.utils.logging import setup_logging, get_logger
from app.utils.performance import monitor, track_performance

# Import routers
from app.api.v1 import assessment, admin
from app.api.v1.discovery import router as discovery_router
from app.api.v1.financial import router as financial_router
from app.api.v1.legal import router as legal_router
from app.api.v1.operations import router as operations_router
from app.api.v1.customers import router as customers_router
from app.api.v1.ai_opportunity import router as ai_opportunity_router
from app.api.v1.verdict import router as verdict_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Assessment Tool Backend Starting...")
    logger.info("📁 Loading configuration files...")
    
    # Setup logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_format = os.getenv("LOG_FORMAT", "text")
    setup_logging(log_level=log_level, log_format=log_format)
    
    # Load chapter configuration
    config_path = Path(__file__).parent.parent / "config" / "chapter-flow.json"
    try:
        with open(config_path) as f:
            app.state.chapter_config = json.load(f)
        logger.info(f"✅ Loaded {len(app.state.chapter_config['chapters'])} chapters")
    except FileNotFoundError:
        logger.warning(f"⚠️  Config file not found: {config_path}")
        app.state.chapter_config = {"chapters": []}
    
    # Load UI configuration
    ui_config_path = Path(__file__).parent.parent / "config" / "ui-config.json"
    try:
        with open(ui_config_path) as f:
            app.state.ui_config = json.load(f)
        logger.info(f"✅ Loaded {len(app.state.ui_config['themes'])} UI themes")
    except FileNotFoundError:
        logger.warning(f"⚠️  UI config file not found: {ui_config_path}")
        app.state.ui_config = {"themes": {}, "default_theme": "tech_blue"}
    
    logger.info("🎯 Backend ready for connections")
    
    yield
    
    # Shutdown
    logger.info("👋 Assessment Tool Backend Shutting Down...")


# Create FastAPI app
app = FastAPI(
    title="Assessment Tool API",
    description="AI-powered digital marketing assessment tool",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow all origins for Codespaces
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Codespaces compatibility
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)


# Root endpoint
@app.get("/")
@track_performance("root_endpoint")
async def root():
    """API root endpoint"""
    return {
        "service": "Assessment Tool API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


# Health check
@app.get("/health")
@track_performance("health_check")
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    
    return {
        "status": "healthy",
        "service": "assessment-backend",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }


# Config endpoints
@app.get("/config/chapters")
@track_performance("config_chapters")
async def get_chapters_config():
    """Get chapter flow configuration"""
    return app.state.chapter_config


@app.get("/config/ui")
@track_performance("config_ui")
async def get_ui_config():
    """Get UI theme configuration"""
    return app.state.ui_config


# Debug endpoint (development only)
@app.get("/debug/config")
async def debug_config():
    """Debug endpoint to check configuration"""
    if os.getenv("ENVIRONMENT") == "production":
        raise HTTPException(status_code=404, detail="Not found")
    
    return {
        "chapter_config_loaded": bool(app.state.chapter_config.get("chapters")),
        "ui_config_loaded": bool(app.state.ui_config.get("themes")),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "cors_origins": cors_origins,
        "performance_metrics": monitor.get_stats()
    }


# Include routers  
app.include_router(assessment.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(discovery_router, prefix="/api/v1/discovery", tags=["discovery"])
app.include_router(financial_router, prefix="/api/v1/financial", tags=["financial"])
app.include_router(legal_router, prefix="/api/v1/legal", tags=["legal"])
app.include_router(operations_router, prefix="/api/v1/operations", tags=["operations"])
app.include_router(customers_router, prefix="/api/v1/customers", tags=["customers"])
app.include_router(ai_opportunity_router, prefix="/api/v1/ai-opportunity", tags=["ai-opportunity"])
app.include_router(verdict_router, prefix="/api/v1/verdict", tags=["verdict"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
