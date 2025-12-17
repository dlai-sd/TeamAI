"""
Pydantic schemas for API request/response validation
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID

from app.models import UserRole, AuthProvider, InviteStatus


# ============================================================================
# Authentication Schemas
# ============================================================================

class UserRegisterRequest(BaseModel):
    """Request to register new user (email/password)"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    full_name: str = Field(..., min_length=2)
    agency_name: str = Field(..., min_length=2, description="Agency name for new agency")
    
    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        """Ensure password has minimum strength"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLoginRequest(BaseModel):
    """Request to login with email/password"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiry in seconds")


class UserResponse(BaseModel):
    """User profile response"""
    id: UUID
    email: str
    full_name: Optional[str]
    role: UserRole
    auth_provider: AuthProvider
    email_verified: bool
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    
    # Related entities
    agency_id: UUID
    team_id: Optional[UUID]
    
    class Config:
        from_attributes = True


# ============================================================================
# OAuth2 Schemas
# ============================================================================

class OAuth2InitiateRequest(BaseModel):
    """Request to start OAuth2 flow"""
    provider: AuthProvider = Field(..., description="azure_ad or google")
    redirect_uri: Optional[str] = Field(None, description="Override default redirect URI")


class OAuth2InitiateResponse(BaseModel):
    """Response with OAuth2 authorization URL"""
    authorization_url: str
    state: str = Field(..., description="State parameter to verify in callback")


class OAuth2CallbackRequest(BaseModel):
    """OAuth2 callback parameters"""
    code: str = Field(..., description="Authorization code from provider")
    state: str = Field(..., description="State parameter from initiate")
    provider: AuthProvider = Field(..., description="azure_ad or google")


class OAuth2CallbackResponse(BaseModel):
    """Response after successful OAuth2 callback"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    is_new_user: bool = Field(..., description="True if user was just created")


# ============================================================================
# Invite Schemas
# ============================================================================

class InviteCreateRequest(BaseModel):
    """Request to create invite (agency admin only)"""
    email: EmailStr
    role: UserRole = Field(..., description="Role to assign: team_user, team_admin, or agency_admin")
    team_id: Optional[UUID] = Field(None, description="Team to assign (required for non-admin roles)")
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        """Ensure role is valid"""
        if v not in [UserRole.TEAM_USER, UserRole.TEAM_ADMIN, UserRole.AGENCY_ADMIN]:
            raise ValueError(f"Invalid role: {v}")
        return v


class InviteResponse(BaseModel):
    """Invite details response"""
    id: UUID
    email: str
    role: str
    status: InviteStatus
    created_at: datetime
    expires_at: datetime
    accepted_at: Optional[datetime]
    
    agency_id: UUID
    team_id: Optional[UUID]
    invited_by_id: Optional[UUID]
    
    class Config:
        from_attributes = True


class InviteAcceptRequest(BaseModel):
    """Request to accept invite"""
    token: str = Field(..., description="Invite token from email link")
    password: Optional[str] = Field(None, min_length=8, description="Password for email/password auth")
    
    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        """Ensure password has minimum strength (if provided)"""
        if v is None:
            return v
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class InviteAcceptResponse(BaseModel):
    """Response after accepting invite"""
    message: str
    user: UserResponse
    access_token: str
    refresh_token: str


# ============================================================================
# Agency & Team Schemas
# ============================================================================

class AgencyCreateRequest(BaseModel):
    """Request to create agency (internal use, during registration)"""
    name: str = Field(..., min_length=2)
    billing_email: EmailStr
    subscription_plan: str = "starter"


class AgencyResponse(BaseModel):
    """Agency details response"""
    id: UUID
    name: str
    billing_email: str
    subscription_plan: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TeamResponse(BaseModel):
    """Team details response"""
    id: UUID
    name: str
    description: Optional[str]
    agency_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Utility Schemas
# ============================================================================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: str
    status_code: int
