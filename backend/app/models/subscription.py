"""
Subscription and Billing Models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Integer
from sqlalchemy.orm import relationship
from app.utils.db import Base, UUID


class Subscription(Base):
    """Subscription - Agency's purchased agent licenses"""
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    agent_role_id = Column(UUID(as_uuid=True), ForeignKey("agent_roles.id"), nullable=False)
    
    purchased_count = Column(Integer, default=1)  # How many licenses purchased
    allocated_count = Column(Integer, default=0)  # How many assigned to teams
    active_this_month = Column(Integer, default=0)  # Billable count
    
    monthly_cost = Column(Numeric(10, 2), nullable=False)
    billing_cycle_start = Column(DateTime, nullable=False)
    billing_cycle_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    agency = relationship("Agency", back_populates="subscriptions")
    agent_role = relationship("AgentRole", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(id={self.id}, agency_id={self.agency_id}, count={self.purchased_count})>"


class SecretLocker(Base):
    """Secret Locker - Store encrypted API keys and credentials"""
    __tablename__ = "secret_locker"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=True)
    
    key_name = Column(String(255), nullable=False)  # e.g., "semrush_api_key"
    encrypted_value = Column(String(1024), nullable=False)  # Encrypted secret
    azure_key_vault_id = Column(String(255), nullable=True)  # Reference to Key Vault
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agency = relationship("Agency", back_populates="secret_locker")
    team = relationship("Team", back_populates="secret_locker")

    def __repr__(self):
        return f"<SecretLocker(id={self.id}, key_name={self.key_name})>"
