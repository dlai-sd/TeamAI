""" Audit Logging, Task Queue, and A/B Testing Models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Integer, Boolean
from sqlalchemy.orm import relationship
from app.utils.db import Base, UUID, JSONB


class AuditLog(Base):
    """Audit Log - Track all agent executions for billing and monitoring"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    agent_instance_id = Column(UUID(as_uuid=True), ForeignKey("agent_instances.id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id"), nullable=True)
    
    execution_time_ms = Column(Integer, nullable=False)
    tokens_used = Column(Integer, default=0)
    cost_incurred = Column(Numeric(10, 4), default=0.0)
    status = Column(String(50), nullable=False)  # success, failed, timeout
    
    execution_metadata = Column(JSONB, nullable=True)  # Additional execution details (renamed from 'metadata')
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    agency = relationship("Agency", back_populates="audit_logs")
    agent_instance = relationship("AgentInstance", back_populates="audit_logs")
    recipe = relationship("Recipe", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, status={self.status}, timestamp={self.timestamp})>"


class TaskQueue(Base):
    """Task Queue - Pending and completed agent tasks"""
    __tablename__ = "task_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_instance_id = Column(UUID(as_uuid=True), ForeignKey("agent_instances.id", ondelete="CASCADE"), nullable=False)
    
    task_type = Column(String(100), nullable=False)  # e.g., "site_audit"
    input_params = Column(JSONB, nullable=False)  # Task inputs
    output_data = Column(JSONB, nullable=True)  # Task results
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    agent_instance = relationship("AgentInstance", back_populates="task_queue")

    def __repr__(self):
        return f"<TaskQueue(id={self.id}, type={self.task_type}, status={self.status})>"


class ABTestResult(Base):
    """A/B Test Results - Track recipe performance for ML optimization"""
    __tablename__ = "ab_test_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id"), nullable=False)
    agent_instance_id = Column(UUID(as_uuid=True), ForeignKey("agent_instances.id"), nullable=False)
    
    variant_version = Column(String(50), nullable=False)  # e.g., "1.0.0" vs "1.1.0-beta"
    quality_score = Column(Numeric(5, 2), nullable=True)  # 0-100 score
    execution_time_ms = Column(Integer, nullable=False)
    token_cost = Column(Numeric(10, 4), nullable=False)
    
    tested_at = Column(DateTime, default=datetime.utcnow)
    is_winner = Column(Boolean, default=False)

    # Relationships
    recipe = relationship("Recipe", back_populates="ab_test_results")
    agent_instance = relationship("AgentInstance", back_populates="ab_test_results")

    def __repr__(self):
        return f"<ABTestResult(id={self.id}, variant={self.variant_version}, score={self.quality_score})>"
