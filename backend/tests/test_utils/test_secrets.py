"""
Test Azure Key Vault Integration
"""
import pytest
import os
from unittest.mock import Mock, patch
from app.utils.secrets import SecretManager, get_secret_manager


class TestSecretManagerLocal:
    """Test SecretManager in local mode (.env fallback)"""
    
    def test_local_mode_enabled_by_default(self):
        """Should use local .env by default"""
        with patch.dict(os.environ, {"USE_AZURE_KEYVAULT": "false"}):
            manager = SecretManager()
            assert not manager.use_keyvault
            assert manager.client is None
    
    def test_get_secret_from_env(self):
        """Should retrieve secret from environment variable"""
        with patch.dict(os.environ, {
            "USE_AZURE_KEYVAULT": "false",
            "TEST_SECRET": "test_value"
        }):
            manager = SecretManager()
            value = manager.get_secret("TEST_SECRET")
            assert value == "test_value"
    
    def test_get_secret_with_default(self):
        """Should return default if secret not found"""
        with patch.dict(os.environ, {"USE_AZURE_KEYVAULT": "false"}, clear=True):
            manager = SecretManager()
            value = manager.get_secret("NONEXISTENT", default="default_value")
            assert value == "default_value"
    
    def test_get_secret_raises_without_default(self):
        """Should raise ValueError if secret not found and no default"""
        with patch.dict(os.environ, {"USE_AZURE_KEYVAULT": "false"}, clear=True):
            manager = SecretManager()
            with pytest.raises(ValueError, match="not set and no default"):
                manager.get_secret("NONEXISTENT")


class TestSecretManagerKeyVault:
    """Test SecretManager with Azure Key Vault"""
    
    @patch('app.utils.secrets.SecretClient')
    @patch('app.utils.secrets.ManagedIdentityCredential')
    def test_keyvault_mode_initializes_client(self, mock_credential, mock_client):
        """Should initialize Key Vault client when enabled"""
        with patch.dict(os.environ, {
            "USE_AZURE_KEYVAULT": "true",
            "AZURE_KEYVAULT_URL": "https://test-kv.vault.azure.net/"
        }):
            manager = SecretManager()
            assert manager.use_keyvault
            assert manager.client is not None
    
    @patch('app.utils.secrets.SecretClient')
    @patch('app.utils.secrets.ManagedIdentityCredential')
    def test_get_secret_from_keyvault(self, mock_credential, mock_client_class):
        """Should retrieve secret from Key Vault"""
        # Mock Key Vault response
        mock_secret = Mock()
        mock_secret.value = "keyvault_value"
        mock_client = Mock()
        mock_client.get_secret.return_value = mock_secret
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {
            "USE_AZURE_KEYVAULT": "true",
            "AZURE_KEYVAULT_URL": "https://test-kv.vault.azure.net/"
        }):
            manager = SecretManager()
            manager.client = mock_client
            
            value = manager.get_secret("TEST_SECRET")
            
            assert value == "keyvault_value"
            mock_client.get_secret.assert_called_once_with("TEST-SECRET")
    
    def test_keyvault_requires_url(self):
        """Should raise error if Key Vault URL not set"""
        with patch.dict(os.environ, {"USE_AZURE_KEYVAULT": "true"}, clear=True):
            with pytest.raises(ValueError, match="AZURE_KEYVAULT_URL must be set"):
                SecretManager()


class TestConvenienceFunctions:
    """Test convenience functions for common secrets"""
    
    def test_get_database_url_from_env(self):
        """Should get database URL from environment"""
        from app.utils.secrets import get_database_url
        
        with patch.dict(os.environ, {
            "USE_AZURE_KEYVAULT": "false",
            "DATABASE_URL": "postgresql://user:pass@host:5432/db"
        }):
            url = get_database_url()
            assert url == "postgresql://user:pass@host:5432/db"
    
    @patch('app.utils.secrets.SecretManager')
    def test_get_groq_api_key(self, mock_manager_class):
        """Should get Groq API key"""
        from app.utils.secrets import get_groq_api_key
        
        mock_manager = Mock()
        mock_manager.get_secret.return_value = "gsk_test_key"
        mock_manager_class.return_value = mock_manager
        
        with patch('app.utils.secrets.get_secret_manager', return_value=mock_manager):
            key = get_groq_api_key()
            assert key == "gsk_test_key"
            mock_manager.get_secret.assert_called_once_with("GROQ_API_KEY")
    
    @patch('app.utils.secrets.SecretManager')
    def test_get_agency_secret(self, mock_manager_class):
        """Should get agency-specific secret"""
        from app.utils.secrets import get_agency_secret
        
        mock_manager = Mock()
        mock_manager.get_secret.return_value = "agency_secret_value"
        mock_manager_class.return_value = mock_manager
        
        with patch('app.utils.secrets.get_secret_manager', return_value=mock_manager):
            value = get_agency_secret("uuid-123", "semrush_api_key")
            assert value == "agency_secret_value"
            mock_manager.get_secret.assert_called_once_with("agency-uuid-123-semrush_api_key")
