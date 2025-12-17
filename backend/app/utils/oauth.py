"""
OAuth2 client for Google SSO (single provider)
"""
import httpx
from typing import Dict, Any
from fastapi import HTTPException, status

from app.config import settings


class GoogleOAuthClient:
    """Google OAuth2 client (SSO only)"""
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.effective_redirect_uri  # Use property for dynamic URL
        
        # Google OAuth endpoints
        self.authorize_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_authorization_url(self, state: str, hd: str = None) -> str:
        """
        Generate OAuth2 authorization URL for user redirect
        
        Args:
            state: Random state parameter to prevent CSRF
            hd: Hosted domain (e.g., 'company.com' to restrict to specific domain)
        
        Returns:
            URL string to redirect user to Google login
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        
        # Optional: Restrict to specific Google Workspace domain
        if hd:
            params["hd"] = hd
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.authorize_url}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from redirect callback
        
        Returns:
            Dict with access_token, id_token, expires_in
        
        Raises:
            HTTPException: If token exchange fails
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.token_url, data=data)
                response.raise_for_status()
                token_data = response.json()
                return token_data
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Google token exchange failed: {e.response.text}"
                )
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Fetch user profile from Google API
        
        Args:
            access_token: Access token from token exchange
        
        Returns:
            Dict with user profile: id, email, name, picture, hd (domain)
        
        Raises:
            HTTPException: If API call fails
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.userinfo_url, headers=headers)
                response.raise_for_status()
                user_info = response.json()
                return user_info
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to fetch Google user info: {e.response.text}"
                )


# Singleton instance
google_oauth_client = GoogleOAuthClient()
