"""
Authentication API Endpoints (Google SSO Only)
"""
import secrets
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.utils.db import get_db
from app.utils.security import get_current_user
from app.models import User, AuthProvider
from app.models.schemas import (
    TokenResponse,
    UserResponse,
    OAuth2CallbackResponse,
    MessageResponse,
)
from app.services.auth_service import AuthService
from app.utils.oauth import google_oauth_client
from app.config import settings
import redis.asyncio as redis

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Redis client for OAuth state storage (production-ready)
redis_client = None

async def get_redis():
    """Get Redis client for OAuth state storage with proper Azure configuration"""
    global redis_client
    if redis_client is None:
        # Azure Redis requires SSL and specific configuration
        redis_url = settings.REDIS_URL
        
        # Configure SSL if using rediss://
        if redis_url.startswith('rediss://'):
            import ssl
            redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                ssl_cert_reqs=ssl.CERT_NONE,  # Azure Redis uses self-signed certs
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
        else:
            redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
        
        # Test connection
        try:
            await redis_client.ping()
            print(f"[Redis] Connected successfully to {redis_url[:30]}...")
        except Exception as e:
            print(f"[Redis ERROR] Connection failed: {e}")
            redis_client = None
            raise
    
    return redis_client


# ============================================================================
# Google SSO Authentication (Only Method)
# ============================================================================

@router.get("/google/login")
async def google_login_initiate(
    domain: str = Query(None, description="Optional: Restrict to Google Workspace domain"),
):
    """
    Initiate Google OAuth2 login flow
    
    Redirects user directly to Google login page
    
    Args:
        domain: Optional Google Workspace domain restriction (e.g., 'company.com')
    
    Returns:
        HTTP 302 redirect to Google OAuth authorization page
    """
    # Generate CSRF state token
    state = secrets.token_urlsafe(32)
    
    # Store state in Redis with 10 minute expiry
    try:
        redis_conn = await get_redis()
        result = await redis_conn.setex(
            f"oauth_state:{state}",
            600,  # 10 minutes
            domain or ""
        )
        print(f"[OAuth] State stored in Redis: {state[:10]}... result={result}")
    except Exception as e:
        print(f"[OAuth ERROR] Failed to store state in Redis: {e}")
        # Continue anyway - we'll validate on callback
    
    # Get authorization URL from Google
    auth_url = google_oauth_client.get_authorization_url(state, hd=domain)
    
    # Redirect directly to Google (standard OAuth flow)
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    db: Session = Depends(get_db),
):
    """
    Google OAuth2 callback endpoint (Google redirects here after login)
    
    Args:
        code: Authorization code from Google
        state: State parameter to verify CSRF
    
    Returns:
        OAuth2CallbackResponse: JWT tokens and user profile
    """
    print(f"[OAuth] Callback received - state: {state[:10]}..., code: {code[:20]}...")
    
    # Verify state parameter (CSRF protection) from Redis
    try:
        redis_conn = await get_redis()
        domain = await redis_conn.get(f"oauth_state:{state}")
        print(f"[OAuth] Redis lookup result: {domain}")
        
        if domain is None:
            print(f"[OAuth ERROR] State not found in Redis: oauth_state:{state[:10]}...")
            # Check if Redis is working at all
            test_key = "redis_health_check"
            await redis_conn.setex(test_key, 10, "ok")
            test_value = await redis_conn.get(test_key)
            print(f"[OAuth] Redis health check: {test_value}")
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state parameter - OAuth state not found in Redis"
            )
        
        # Remove used state from Redis
        await redis_conn.delete(f"oauth_state:{state}")
        print(f"[OAuth] State validated and removed from Redis")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[OAuth ERROR] Redis connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Redis connection error: {str(e)}"
        )
    
    try:
        # Exchange authorization code for access token
        token_data = await google_oauth_client.exchange_code_for_token(code)
        user_info = await google_oauth_client.get_user_info(token_data["access_token"])
        
        external_id = user_info["id"]
        email = user_info["email"]
        full_name = user_info.get("name")
        avatar_url = user_info.get("picture")
        
        # Login or register user
        auth_service = AuthService(db)
        user, tokens, is_new_user = auth_service.sso_login_or_register(
            provider=AuthProvider.GOOGLE,
            external_id=external_id,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
        )
        
        # Redirect to frontend with tokens (standard OAuth flow)
        # Frontend will extract tokens from URL and store in localStorage
        redirect_url = (
            f"{settings.FRONTEND_URL}/auth/callback"
            f"?access_token={tokens.access_token}"
            f"&refresh_token={tokens.refresh_token}"
            f"&token_type={tokens.token_type}"
            f"&expires_in={tokens.expires_in}"
            f"&is_new_user={'true' if is_new_user else 'false'}"
        )
        
        return RedirectResponse(url=redirect_url, status_code=302)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user profile
    
    Requires:
        Authorization: Bearer <access_token>
    
    Returns:
        UserResponse: Current user profile
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        auth_provider=current_user.auth_provider,
        email_verified=current_user.email_verified,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at,
        agency_id=current_user.agency_id,
        team_id=current_user.team_id,
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
):
    """
    Logout current user
    
    Note: JWT tokens are stateless, so logout is client-side only
    (client should delete tokens from storage)
    
    Returns:
        MessageResponse: Success message
    """
    # TODO: In production, add token to blacklist in Redis
    # with expiry equal to token's remaining lifetime
    
    return MessageResponse(
        message="Logged out successfully",
        detail="Please delete access and refresh tokens from client storage"
    )
