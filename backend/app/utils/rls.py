"""
Multi-Tenant Middleware - Set PostgreSQL RLS context
Ensures Row-Level Security policies filter data by agency_id
"""
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID


async def set_rls_context(session: AsyncSession, agency_id: Optional[UUID]):
    """
    Set PostgreSQL session variable for Row-Level Security
    
    Args:
        session: Async SQLAlchemy session
        agency_id: Current user's agency ID (from JWT token)
    """
    if agency_id:
        # Set app.current_agency_id session variable
        # RLS policies use this to filter queries
        await session.execute(
            f"SELECT set_config('app.current_agency_id', '{str(agency_id)}', false)"
        )


async def clear_rls_context(session: AsyncSession):
    """
    Clear PostgreSQL RLS context (for superuser operations)
    
    Args:
        session: Async SQLAlchemy session
    """
    await session.execute(
        "SELECT set_config('app.current_agency_id', '', false)"
    )


def get_agency_id_from_user(current_user) -> Optional[UUID]:
    """
    Extract agency_id from authenticated user
    
    Args:
        current_user: UserResponse from JWT token
        
    Returns:
        UUID of user's agency or None
    """
    # Handle dict or object
    if isinstance(current_user, dict):
        return current_user.get('agency_id')
    else:
        return getattr(current_user, 'agency_id', None)
