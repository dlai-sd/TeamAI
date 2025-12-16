"""
Authentication Service - Business logic for user registration, login, and SSO
"""
from typing import Optional, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models import User, Agency, Team, Invite, UserRole, AuthProvider, InviteStatus
from app.models.schemas import (
    TokenResponse,
    InviteCreateRequest,
)
from app.utils.security import create_access_token, create_refresh_token
from app.utils.oauth import google_oauth_client
from app.config import settings


class AuthService:
    """Authentication service with SSO support"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================================================================
    # Google SSO Authentication (Only Method)
    # =========================================================================
    
    def sso_login_or_register(
        self, 
        provider: AuthProvider, 
        external_id: str, 
        email: str, 
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> Tuple[User, TokenResponse, bool]:
        """
        Login or register user via SSO
        
        Args:
            provider: AuthProvider (AZURE_AD or GOOGLE)
            external_id: Provider's user ID
            email: User's email
            full_name: User's full name (optional)
            avatar_url: User's avatar URL (optional)
        
        Returns:
            Tuple of (User, TokenResponse, is_new_user)
        
        Raises:
            HTTPException: 400 if no pending invite for new user
        """
        # Check if user exists (by external_id or email)
        result = self.db.execute(
            select(User).filter(
                (User.external_id == external_id) | (User.email == email)
            )
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Existing user - update last login
            user.last_login_at = datetime.utcnow()
            user.email_verified = True  # SSO users are always verified
            
            # Update profile if missing
            if not user.full_name and full_name:
                user.full_name = full_name
            if not user.avatar_url and avatar_url:
                user.avatar_url = avatar_url
            
            self.db.commit()
            self.db.refresh(user)
            
            tokens = self._generate_tokens(user)
            return user, tokens, False
        
        # New SSO user - check for pending invite
        result = self.db.execute(
            select(Invite).filter(
                Invite.email == email,
                Invite.status == InviteStatus.PENDING,
            )
        )
        invite = result.scalar_one_or_none()
        
        if not invite or not invite.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid invitation found. Please contact your administrator."
            )
        
        # Create user from invite
        # Convert invite role string (e.g., "AGENCY_ADMIN") to UserRole enum (e.g., UserRole.AGENCY_ADMIN)
        try:
            role = UserRole[invite.role]  # Use bracket notation for enum name lookup
        except KeyError:
            # Fallback: convert "AGENCY_ADMIN" string to enum value "agency_admin"
            role = UserRole(invite.role.lower())
        
        user = User(
            agency_id=invite.agency_id,
            team_id=invite.team_id,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
            role=role,
            auth_provider=provider,
            external_id=external_id,
            email_verified=True,  # SSO users are always verified
            is_active=True,
            last_login_at=datetime.utcnow(),
        )
        self.db.add(user)
        
        # Mark invite as accepted
        invite.status = InviteStatus.ACCEPTED
        invite.accepted_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        tokens = self._generate_tokens(user)
        return user, tokens, True
    
    # =========================================================================
    # Invite Management
    # =========================================================================
    
    def create_invite(
        self, 
        request: InviteCreateRequest, 
        invited_by: User
    ) -> Invite:
        """
        Create invitation for new user (agency admin only)
        
        Args:
            request: Invite details
            invited_by: User creating the invite (must be agency_admin)
        
        Returns:
            Created Invite object
        
        Raises:
            HTTPException: 403 if not agency_admin, 409 if email exists
        """
        # Check permissions
        if invited_by.role != UserRole.AGENCY_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only agency admins can invite users"
            )
        
        # Check if email already exists
        result = self.db.execute(
            select(User).filter(User.email == request.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        # Validate team_id for non-admin roles
        if request.role != UserRole.AGENCY_ADMIN and not request.team_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="team_id required for non-admin roles"
            )
        
        # Create invite
        invite = Invite(
            agency_id=invited_by.agency_id,
            team_id=request.team_id,
            email=request.email,
            role=request.role.value,  # Store as string
            token=Invite.generate_token(),
            expires_at=Invite.default_expires_at(),
            invited_by_id=invited_by.id,
        )
        self.db.add(invite)
        self.db.commit()
        self.db.refresh(invite)
        
        # TODO: Send email with invite link
        # invite_link = f"{settings.FRONTEND_URL}/accept-invite?token={invite.token}"
        
        return invite
    
    def get_pending_invite(self, email: str) -> Optional[Invite]:
        """
        Get pending invite for email (used during SSO login)
        
        Args:
            email: User's email from SSO provider
        
        Returns:
            Invite object if found and valid, None otherwise
        """
        result = self.db.execute(
            select(Invite).filter(
                Invite.email == email,
                Invite.status == InviteStatus.PENDING,
            )
        )
        invite = result.scalar_one_or_none()
        
        if invite and invite.is_valid:
            return invite
        return None
    
    def mark_invite_accepted(self, invite_id: UUID) -> None:
        """
        Mark invite as accepted after user logs in via SSO
        
        Args:
            invite_id: ID of the invite to mark as accepted
        """
        result = self.db.execute(
            select(Invite).filter(Invite.id == invite_id)
        )
        invite = result.scalar_one_or_none()
        
        if invite:
            invite.status = InviteStatus.ACCEPTED
            invite.accepted_at = datetime.utcnow()
            self.db.commit()
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def _generate_tokens(self, user: User) -> TokenResponse:
        """Generate JWT access and refresh tokens"""
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
