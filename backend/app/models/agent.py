"""
Agent-related Models (AgentRole, Cookbook, Recipe, AgentInstance)
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.utils.db import Base


class AgentRole(Base):
    """Agent Role - Template/Definition (e.g., SEO Specialist)"""
    __tablename__ = "agent_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="available")  # available, upcoming, deprecated
    version = Column(String(50), nullable=False)
    capabilities = Column(JSONB, nullable=True)  # JSON array of capabilities
    base_price = Column(Numeric(10, 2), default=50.00)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    agent_instances = relationship("AgentInstance", back_populates="agent_role")
    subscriptions = relationship("Subscription", back_populates="agent_role")
    cookbooks = relationship("Cookbook", back_populates="agent_role")

    def __repr__(self):
        return f"<AgentRole(id={self.id}, name={self.name}, version={self.version})>"


class Cookbook(Base):
    """Cookbook - Collection of recipes for an agent role"""
    __tablename__ = "cookbooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_role_id = Column(UUID(as_uuid=True), ForeignKey("agent_roles.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    yaml_definition = Column(JSONB, nullable=False)  # Parsed YAML content
    required_secrets = Column(JSONB, nullable=True)  # List of required secret keys
    allowed_data_sources = Column(JSONB, nullable=True)
    subscription_limits = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    agent_role = relationship("AgentRole", back_populates="cookbooks")
    recipes = relationship("Recipe", back_populates="cookbook", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cookbook(id={self.id}, name={self.name}, version={self.version})>"


class Recipe(Base):
    """Recipe - Executable workflow (e.g., Site Audit)"""
    __tablename__ = "recipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cookbook_id = Column(UUID(as_uuid=True), ForeignKey("cookbooks.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    yaml_definition = Column(JSONB, nullable=False)  # Parsed YAML content
    ab_testing_enabled = Column(Boolean, default=False)
    cost_per_execution = Column(Numeric(10, 4), default=0.50)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    cookbook = relationship("Cookbook", back_populates="recipes")
    ab_test_results = relationship("ABTestResult", back_populates="recipe")
    audit_logs = relationship("AuditLog", back_populates="recipe")

    def __repr__(self):
        return f"<Recipe(id={self.id}, name={self.name}, version={self.version})>"


class AgentInstance(Base):
    """Agent Instance - Deployed agent for a specific team"""
    __tablename__ = "agent_instances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    agent_role_id = Column(UUID(as_uuid=True), ForeignKey("agent_roles.id"), nullable=False)
    
    custom_name = Column(String(255), nullable=False)  # e.g., "Rover"
    avatar_icon = Column(String(100), nullable=True)  # e.g., "dog", "robot"
    configuration = Column(JSONB, nullable=True)  # Custom parameters
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, nullable=True)

    # Relationships
    team = relationship("Team", back_populates="agent_instances")
    agent_role = relationship("AgentRole", back_populates="agent_instances")
    task_queue = relationship("TaskQueue", back_populates="agent_instance", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="agent_instance")
    ab_test_results = relationship("ABTestResult", back_populates="agent_instance")

    def __repr__(self):
        return f"<AgentInstance(id={self.id}, name={self.custom_name}, team_id={self.team_id})>"
