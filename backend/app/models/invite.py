"""
Invite Model - Email-based team invitations
"""
import uuid
import enum
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.utils.db import Base


class InviteStatus(str, enum.Enum):
    """Status of invitation"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class Invite(Base):
    """
    Email invitation for users to join agency/team
    Supports SSO users - they get auto-assigned on first login
    """
    __tablename__ = "invites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=True)
    
    # Invitee details
    email = Column(String(255), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # Will use UserRole enum values
    
    # Invite metadata
    token = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(Enum(InviteStatus), default=InviteStatus.PENDING, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    
    # Who created the invite
    invited_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    agency = relationship("Agency")
    team = relationship("Team")
    invited_by = relationship("User", foreign_keys=[invited_by_id])

    @staticmethod
    def generate_token() -> str:
        """Generate secure random token"""
        return str(uuid.uuid4())
    
    @staticmethod
    def default_expires_at() -> datetime:
        """Default expiry: 7 days from now"""
        return datetime.utcnow() + timedelta(days=7)
    
    @property
    def is_valid(self) -> bool:
        """Check if invite is still valid"""
        return (
            self.status == InviteStatus.PENDING
            and self.expires_at > datetime.utcnow()
        )

    def __repr__(self):
        return f"<Invite(email={self.email}, status={self.status}, agency_id={self.agency_id})>"
