"""
TeamAI Backend - FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Import routers
from app.api import auth, invites, agents, tasks

app = FastAPI(
    title="TeamAI API",
    description="Virtual AI Workforce Platform for Digital Marketing Agencies",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - Allow all origins in development (Codespaces compatibility)
# In production, this should be restricted to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=False,  # Can't use credentials with wildcard
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Register API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(invites.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "name": "TeamAI API",
        "version": "0.1.0",
        "status": "operational",
        "message": "🚀 Google SSO Authentication Active!",
        "docs": "/docs",
        "authentication": {
            "method": "Google OAuth2 SSO Only",
            "login_url": "/api/v1/auth/google/login",
            "features": [
                "Google Workspace Integration",
                "Role-Based Access Control (RBAC)",
                "Invite-Based Team Assignment",
                "Admin-Controlled User Management"
            ]
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}

# Import routers (will be created later)
# from app.api import admin, teams, agents, marketplace, tasks
# app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
# app.include_router(teams.router, prefix="/api/teams", tags=["Teams"])
# app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
# app.include_router(marketplace.router, prefix="/api/marketplace", tags=["Marketplace"])
# app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
