"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    PYTHON_ENV: str = "development"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API - Set via BACKEND_URL env var in production
    API_BASE_URL: str = "http://localhost:8000"
    BACKEND_URL: str = ""  # If set, overrides API_BASE_URL
    
    # Database
    DATABASE_URL: str = "postgresql://teamai:teamai_dev_password@postgres:5432/teamai"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Azure Key Vault (Production Secrets Management)
    USE_AZURE_KEYVAULT: bool = False
    AZURE_KEYVAULT_URL: str = ""
    AZURE_KEY_VAULT_URL: str = ""  # Legacy support
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    
    # LLM Providers
    GROQ_API_KEY: str = ""
    GROQ_MODEL_PRIMARY: str = "llama-3.1-8b-instant"
    GROQ_MODEL_FALLBACK: str = "llama-3.3-70b-versatile"
    OPENAI_API_KEY: str = ""
    
    # Authentication & Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_SECRET_KEY: str = ""  # Will use SECRET_KEY if not set
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google OAuth2 (SSO Only)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""  # Auto-constructed from backend URL if not set
    GOOGLE_WORKSPACE_DOMAIN: str = ""  # Optional: Restrict to specific domain (e.g., 'company.com')
    
    # Frontend URL (for email links)
    FRONTEND_URL: str = "http://localhost:3000"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "https://teamai.com"
    ]
    
    # Feature Flags
    MOCK_MODE: bool = False
    ENABLE_AB_TESTING: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def effective_backend_url(self) -> str:
        """Get the effective backend URL (BACKEND_URL if set, else API_BASE_URL)"""
        return self.BACKEND_URL or self.API_BASE_URL
    
    @property
    def effective_redirect_uri(self) -> str:
        """Get the OAuth redirect URI (auto-construct if not explicitly set)"""
        if self.GOOGLE_REDIRECT_URI:
            return self.GOOGLE_REDIRECT_URI
        return f"{self.effective_backend_url}/api/v1/auth/google/callback"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
