"""
Alembic migration script template
Generates database migrations for schema changes
"""

# Run this to create a new migration:
# alembic revision --autogenerate -m "description"

# Apply migrations:
# alembic upgrade head

# Rollback:
# alembic downgrade -1

"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-12-19

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create initial tables"""
    
    # Assessments table
    op.create_table(
        'assessments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow),
        
        # Company info
        sa.Column('company_name', sa.String(200)),
        sa.Column('cin', sa.String(50)),
        sa.Column('industry', sa.String(100)),
        sa.Column('location', sa.String(200)),
        sa.Column('website', sa.String(500)),
        
        # Assessment state
        sa.Column('status', sa.String(50), nullable=False, default='initiated'),
        sa.Column('current_chapter', sa.Integer(), nullable=False, default=1),
        
        # Scores
        sa.Column('digital_health_score', sa.Integer()),
        sa.Column('financial_health_score', sa.Integer()),
        sa.Column('overall_score', sa.Integer()),
        
        # Contact
        sa.Column('contact_email', sa.String(200)),
        sa.Column('contact_phone', sa.String(50)),
        
        # Indexes
        sa.Index('idx_status', 'status'),
        sa.Index('idx_created_at', 'created_at'),
        sa.Index('idx_company_name', 'company_name')
    )


def downgrade():
    """Drop tables"""
    op.drop_table('assessments')
