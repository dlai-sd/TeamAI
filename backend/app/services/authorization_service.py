"""
Authorization Service - Role-based access control
Validates user permissions for agency operations
"""
from typing import Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.schemas import UserResponse
from app.models.agency import Agency, Team
from app.models.subscription import Subscription


class AuthorizationService:
    """
    Service for validating user permissions
    
    Handles:
    - Agency admin checks
    - Team ownership validation
    - Subscription limit enforcement
    """
    
    def __init__(self, db_session: AsyncSession):
        self.session = db_session
    
    async def validate_agency_admin(
        self, 
        current_user: UserResponse, 
        agency_id: Optional[UUID] = None
    ) -> bool:
        """
        Validate user is admin of agency
        
        Args:
            current_user: Authenticated user
            agency_id: Agency to check (defaults to user's agency)
            
        Returns:
            True if user is admin
            
        Raises:
            HTTPException: If user is not admin
        """
        # Extract user info
        user_agency_id = self._get_user_agency_id(current_user)
        user_role = self._get_user_role(current_user)
        
        # Check agency match
        target_agency = agency_id or user_agency_id
        if user_agency_id != target_agency:
            raise HTTPException(
                status_code=403, 
                detail="Access denied: Not a member of this agency"
            )
        
        # Check admin role
        if user_role not in ['admin', 'owner']:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Admin role required"
            )
        
        return True
    
    async def validate_team_ownership(
        self,
        current_user: UserResponse,
        team_id: UUID
    ) -> Team:
        """
        Validate team belongs to user's agency
        
        Args:
            current_user: Authenticated user
            team_id: Team to validate
            
        Returns:
            Team record if valid
            
        Raises:
            HTTPException: If team not found or not owned by user's agency
        """
        user_agency_id = self._get_user_agency_id(current_user)
        
        # Query team
        stmt = select(Team).where(Team.id == team_id)
        result = await self.session.execute(stmt)
        team = result.scalar_one_or_none()
        
        if not team:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        
        if team.agency_id != user_agency_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Team belongs to different agency"
            )
        
        return team
    
    async def check_subscription_limits(
        self,
        agency_id: UUID,
        agent_role_id: UUID
    ) -> bool:
        """
        Check if agency can allocate another agent
        
        Args:
            agency_id: Agency ID
            agent_role_id: AgentRole being allocated
            
        Returns:
            True if within limits
            
        Raises:
            HTTPException: If limit exceeded
        """
        # Query subscription
        stmt = select(Subscription).where(
            Subscription.agency_id == agency_id,
            Subscription.agent_role_id == agent_role_id
        )
        result = await self.session.execute(stmt)
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(
                status_code=400,
                detail=f"No subscription found for agent role. Purchase required."
            )
        
        # Check limits
        if subscription.allocated_count >= subscription.purchased_count:
            raise HTTPException(
                status_code=400,
                detail=f"Subscription limit reached: {subscription.allocated_count}/{subscription.purchased_count} agents allocated"
            )
        
        return True
    
    async def increment_allocation(
        self,
        agency_id: UUID,
        agent_role_id: UUID
    ):
        """
        Increment allocated_count after successful allocation
        
        Args:
            agency_id: Agency ID
            agent_role_id: AgentRole allocated
        """
        stmt = select(Subscription).where(
            Subscription.agency_id == agency_id,
            Subscription.agent_role_id == agent_role_id
        )
        result = await self.session.execute(stmt)
        subscription = result.scalar_one_or_none()
        
        if subscription:
            subscription.allocated_count += 1
            await self.session.flush()
    
    async def decrement_allocation(
        self,
        agency_id: UUID,
        agent_role_id: UUID
    ):
        """
        Decrement allocated_count after deactivation
        
        Args:
            agency_id: Agency ID
            agent_role_id: AgentRole deallocated
        """
        stmt = select(Subscription).where(
            Subscription.agency_id == agency_id,
            Subscription.agent_role_id == agent_role_id
        )
        result = await self.session.execute(stmt)
        subscription = result.scalar_one_or_none()
        
        if subscription and subscription.allocated_count > 0:
            subscription.allocated_count -= 1
            await self.session.flush()
    
    def _get_user_agency_id(self, user: UserResponse) -> UUID:
        """Extract agency_id from user"""
        if isinstance(user, dict):
            agency_id = user.get('agency_id')
        else:
            agency_id = getattr(user, 'agency_id', None)
        
        if not agency_id:
            raise HTTPException(status_code=400, detail="User has no agency assigned")
        
        return agency_id
    
    def _get_user_role(self, user: UserResponse) -> str:
        """Extract role from user"""
        if isinstance(user, dict):
            return user.get('role', 'member')
        else:
            return getattr(user, 'role', 'member')
