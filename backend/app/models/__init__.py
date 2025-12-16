"""
Models package - Import all models here for Alembic
"""
from app.utils.db import Base

# Import all models so Alembic can detect them
from app.models.agency import Agency, Team, User, UserRole, AuthProvider
from app.models.agent import AgentRole, Cookbook, Recipe, AgentInstance
from app.models.subscription import Subscription, SecretLocker
from app.models.audit import AuditLog, TaskQueue, ABTestResult
from app.models.invite import Invite, InviteStatus

__all__ = [
    "Base",
    "Agency",
    "Team",
    "User",
    "UserRole",
    "AuthProvider",
    "AgentRole",
    "Cookbook",
    "Recipe",
    "AgentInstance",
    "Subscription",
    "SecretLocker",
    "AuditLog",
    "TaskQueue",
    "ABTestResult",
    "Invite",
    "InviteStatus",
]
