"""
Invite API Endpoints
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.utils.db import get_db
from app.utils.security import get_current_user, RoleChecker
from app.models import User, Invite, UserRole, InviteStatus
from app.models.schemas import (
    InviteCreateRequest,
    InviteResponse,
    MessageResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/invites", tags=["Invitations"])


# ============================================================================
# Invite Management (Agency Admin Only)
# ============================================================================

@router.post("", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
async def create_invite(
    request: InviteCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRole.AGENCY_ADMIN])),
):
    """
    Create invitation for new user (agency admin only)
    
    Requires:
        - Role: AGENCY_ADMIN
        - Authorization: Bearer <access_token>
    
    Returns:
        InviteResponse: Created invitation details
    """
    auth_service = AuthService(db)
    invite = auth_service.create_invite(request, current_user)
    
    return InviteResponse(
        id=invite.id,
        email=invite.email,
        role=invite.role,
        status=invite.status,
        created_at=invite.created_at,
        expires_at=invite.expires_at,
        accepted_at=invite.accepted_at,
        agency_id=invite.agency_id,
        team_id=invite.team_id,
        invited_by_id=invite.invited_by_id,
    )


@router.get("", response_model=List[InviteResponse])
async def list_invites(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRole.AGENCY_ADMIN])),
):
    """
    List all invitations for current agency (agency admin only)
    
    Requires:
        - Role: AGENCY_ADMIN
        - Authorization: Bearer <access_token>
    
    Returns:
        List[InviteResponse]: All invitations for the agency
    """
    result = db.execute(
        select(Invite)
        .filter(Invite.agency_id == current_user.agency_id)
        .order_by(Invite.created_at.desc())
    )
    invites = result.scalars().all()
    
    return [
        InviteResponse(
            id=invite.id,
            email=invite.email,
            role=invite.role,
            status=invite.status,
            created_at=invite.created_at,
            expires_at=invite.expires_at,
            accepted_at=invite.accepted_at,
            agency_id=invite.agency_id,
            team_id=invite.team_id,
            invited_by_id=invite.invited_by_id,
        )
        for invite in invites
    ]


@router.get("/{invite_id}", response_model=InviteResponse)
async def get_invite(
    invite_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRole.AGENCY_ADMIN])),
):
    """
    Get invitation details (agency admin only)
    
    Requires:
        - Role: AGENCY_ADMIN
        - Authorization: Bearer <access_token>
    
    Returns:
        InviteResponse: Invitation details
    """
    result = db.execute(
        select(Invite).filter(
            Invite.id == invite_id,
            Invite.agency_id == current_user.agency_id
        )
    )
    invite = result.scalar_one_or_none()
    
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found"
        )
    
    return InviteResponse(
        id=invite.id,
        email=invite.email,
        role=invite.role,
        status=invite.status,
        created_at=invite.created_at,
        expires_at=invite.expires_at,
        accepted_at=invite.accepted_at,
        agency_id=invite.agency_id,
        team_id=invite.team_id,
        invited_by_id=invite.invited_by_id,
    )


@router.delete("/{invite_id}", response_model=MessageResponse)
async def revoke_invite(
    invite_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRole.AGENCY_ADMIN])),
):
    """
    Revoke/cancel invitation (agency admin only)
    
    Requires:
        - Role: AGENCY_ADMIN
        - Authorization: Bearer <access_token>
    
    Returns:
        MessageResponse: Success message
    """
    result = db.execute(
        select(Invite).filter(
            Invite.id == invite_id,
            Invite.agency_id == current_user.agency_id
        )
    )
    invite = result.scalar_one_or_none()
    
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found"
        )
    
    if invite.status != InviteStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot revoke invite with status: {invite.status.value}"
        )
    
    invite.status = InviteStatus.REVOKED
    db.commit()
    
    return MessageResponse(
        message="Invite revoked successfully",
        detail=f"Invitation to {invite.email} has been revoked"
    )


# ============================================================================
# Public Invite Acceptance (No Auth Required)
# ============================================================================

@router.get("/verify/{token}", response_model=InviteResponse)
async def verify_invite_token(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Verify invite token (public endpoint, no auth required)
    
    Used by frontend to check if invite is valid before redirecting to Google SSO
    User should then login via /auth/google/login with their email
    
    Returns:
        InviteResponse: Invitation details if valid
    """
    result = db.execute(
        select(Invite).filter(Invite.token == token)
    )
    invite = result.scalar_one_or_none()
    
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found"
        )
    
    if not invite.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invite is {invite.status.value} or expired"
        )
    
    return InviteResponse(
        id=invite.id,
        email=invite.email,
        role=invite.role,
        status=invite.status,
        created_at=invite.created_at,
        expires_at=invite.expires_at,
        accepted_at=invite.accepted_at,
        agency_id=invite.agency_id,
        team_id=invite.team_id,
        invited_by_id=invite.invited_by_id,
    )
