"""
Secrets Management - Azure Key Vault Integration
Supports local development (.env fallback) and production (Key Vault)
"""
import os
from typing import Optional
from functools import lru_cache
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError
import logging

logger = logging.getLogger(__name__)


class SecretManager:
    """
    Centralized secrets management with Azure Key Vault
    
    Environment Variables:
    - USE_AZURE_KEYVAULT: "true" to enable Key Vault, "false" for local .env
    - AZURE_KEYVAULT_URL: Key Vault URL (e.g., https://teamai-kv.vault.azure.net/)
    - AZURE_CLIENT_ID: (Optional) Service principal client ID
    - AZURE_TENANT_ID: (Optional) Azure AD tenant ID
    """
    
    def __init__(self):
        self.use_keyvault = os.getenv("USE_AZURE_KEYVAULT", "false").lower() == "true"
        self.keyvault_url = os.getenv("AZURE_KEYVAULT_URL")
        self.client: Optional[SecretClient] = None
        
        if self.use_keyvault:
            if not self.keyvault_url:
                raise ValueError("AZURE_KEYVAULT_URL must be set when USE_AZURE_KEYVAULT=true")
            
            self._initialize_keyvault_client()
            logger.info(f"✅ Azure Key Vault initialized: {self.keyvault_url}")
        else:
            logger.info("📁 Using local .env file for secrets (development mode)")
    
    def _initialize_keyvault_client(self):
        """Initialize Azure Key Vault client with appropriate credentials"""
        try:
            # Try managed identity first (production in Azure)
            credential = ManagedIdentityCredential()
            self.client = SecretClient(vault_url=self.keyvault_url, credential=credential)
            logger.info("Using Azure Managed Identity")
        except Exception:
            # Fallback to default credential chain (local dev with Azure CLI)
            credential = DefaultAzureCredential()
            self.client = SecretClient(vault_url=self.keyvault_url, credential=credential)
            logger.info("Using Azure DefaultAzureCredential (CLI/Service Principal)")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> str:
        """
        Retrieve secret from Key Vault or .env file
        
        Args:
            key: Secret name (e.g., "DATABASE-PASSWORD", "GROQ-API-KEY")
            default: Default value if secret not found
        
        Returns:
            Secret value
        
        Raises:
            ValueError: If secret not found and no default provided
        """
        if self.use_keyvault:
            return self._get_from_keyvault(key, default)
        else:
            return self._get_from_env(key, default)
    
    def _get_from_keyvault(self, key: str, default: Optional[str] = None) -> str:
        """Get secret from Azure Key Vault"""
        try:
            # Key Vault uses hyphens, not underscores
            kv_key = key.replace("_", "-")
            secret = self.client.get_secret(kv_key)
            logger.debug(f"✅ Retrieved secret: {kv_key}")
            return secret.value
        except ResourceNotFoundError:
            if default is not None:
                logger.warning(f"⚠️  Secret '{key}' not found in Key Vault, using default")
                return default
            raise ValueError(f"Secret '{key}' not found in Azure Key Vault and no default provided")
        except Exception as e:
            logger.error(f"❌ Error retrieving secret '{key}': {str(e)}")
            if default is not None:
                return default
            raise
    
    def _get_from_env(self, key: str, default: Optional[str] = None) -> str:
        """Get secret from environment variable (.env file)"""
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Environment variable '{key}' not set and no default provided")
        return value
    
    def set_secret(self, key: str, value: str) -> None:
        """
        Store secret in Key Vault (production only)
        
        Args:
            key: Secret name
            value: Secret value
        
        Note: This is typically used by admin tools, not application code
        """
        if not self.use_keyvault:
            logger.warning("⚠️  Cannot set secrets in local mode (.env). Use Key Vault in production.")
            return
        
        kv_key = key.replace("_", "-")
        self.client.set_secret(kv_key, value)
        logger.info(f"✅ Secret '{kv_key}' stored in Key Vault")
    
    def list_secrets(self) -> list:
        """List all secret names in Key Vault (admin only)"""
        if not self.use_keyvault:
            logger.warning("⚠️  Cannot list secrets in local mode")
            return []
        
        secrets = []
        for secret in self.client.list_properties_of_secrets():
            secrets.append(secret.name)
        return secrets


@lru_cache()
def get_secret_manager() -> SecretManager:
    """
    Singleton instance of SecretManager
    Use this in application code to avoid multiple clients
    """
    return SecretManager()


# Convenience functions for common use cases
def get_database_url() -> str:
    """Get database connection string"""
    manager = get_secret_manager()
    if manager.use_keyvault:
        # Construct from individual secrets
        host = manager.get_secret("DATABASE-HOST", "postgres")
        port = manager.get_secret("DATABASE-PORT", "5432")
        name = manager.get_secret("DATABASE-NAME", "teamai")
        user = manager.get_secret("DATABASE-USER", "teamai")
        password = manager.get_secret("DATABASE-PASSWORD")
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    else:
        return manager.get_secret("DATABASE_URL")


def get_redis_url() -> str:
    """Get Redis connection string"""
    manager = get_secret_manager()
    return manager.get_secret("REDIS_URL", "redis://redis:6379/0")


def get_jwt_secret() -> str:
    """Get JWT secret key for token signing"""
    manager = get_secret_manager()
    return manager.get_secret("JWT_SECRET_KEY", manager.get_secret("SECRET_KEY"))


def get_groq_api_key() -> str:
    """Get Groq API key for LLM inference"""
    manager = get_secret_manager()
    return manager.get_secret("GROQ_API_KEY")


def get_openai_api_key() -> str:
    """Get OpenAI API key (fallback LLM)"""
    manager = get_secret_manager()
    return manager.get_secret("OPENAI_API_KEY", "")


def get_agency_secret(agency_id: str, key: str) -> str:
    """
    Get agency-specific secret (e.g., Semrush API key)
    
    Args:
        agency_id: Agency UUID
        key: Secret key (e.g., "semrush_api_key")
    
    Returns:
        Secret value
    
    Note: Key Vault secret name format: "agency-{agency_id}-{key}"
    """
    manager = get_secret_manager()
    kv_key = f"agency-{agency_id}-{key}"
    return manager.get_secret(kv_key)
