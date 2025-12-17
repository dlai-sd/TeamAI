"""
Agency, Team, and User Models
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.utils.db import Base, UUID


class UserRole(str, enum.Enum):
    """Role-based access control for users"""
    AGENCY_ADMIN = "agency_admin"  # Full access: billing, agents, teams, secrets
    TEAM_ADMIN = "team_admin"      # Team management: configure agents, manage members
    TEAM_USER = "team_user"        # Basic access: interact with agents, view outputs


class AuthProvider(str, enum.Enum):
    """Supported authentication providers"""
    GOOGLE = "google"        # Google Workspace (SSO only)


class Agency(Base):
    """Agency (Tenant) - Top level in hierarchy"""
    __tablename__ = "agencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    billing_email = Column(String(255), nullable=False, unique=True)
    subscription_plan = Column(String(50), default="starter")  # starter, professional, enterprise
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teams = relationship("Team", back_populates="agency", cascade="all, delete-orphan")
    users = relationship("User", back_populates="agency", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="agency", cascade="all, delete-orphan")
    secret_locker = relationship("SecretLocker", back_populates="agency", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="agency", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Agency(id={self.id}, name={self.name})>"


class Team(Base):
    """Team - Department/Project within an Agency"""
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agency = relationship("Agency", back_populates="teams")
    users = relationship("User", back_populates="team")
    agent_instances = relationship("AgentInstance", back_populates="team", cascade="all, delete-orphan")
    secret_locker = relationship("SecretLocker", back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name}, agency_id={self.agency_id})>"


class User(Base):
    """User - Can be Agency Admin or Team Member"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    
    # Authentication fields
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)  # Null if SSO user
    email_verified = Column(Boolean, default=False)
    
    # SSO fields
    auth_provider = Column(Enum(AuthProvider), default=AuthProvider.GOOGLE, nullable=False)
    external_id = Column(String(255), nullable=True, index=True)  # SSO provider's user ID
    
    # Profile fields
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Role & status
    role = Column(Enum(UserRole), default=UserRole.TEAM_USER, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    agency = relationship("Agency", back_populates="users")
    team = relationship("Team", back_populates="users")
    
    def has_permission(self, required_role: UserRole) -> bool:
        """Check if user has required role or higher"""
        role_hierarchy = {
            UserRole.TEAM_USER: 1,
            UserRole.TEAM_ADMIN: 2,
            UserRole.AGENCY_ADMIN: 3,
        }
        return role_hierarchy[self.role] >= role_hierarchy[required_role]

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
