"""Mako template for migration files"""
"""seed_test_data

Revision ID: 064f82babb8e
Revises: 3cb00c0eea3c
Create Date: 2025-12-16 12:22:27.546197

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from datetime import datetime, timedelta
import uuid


# revision identifiers, used by Alembic.
revision = '064f82babb8e'
down_revision = '3cb00c0eea3c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Seed test data for authentication testing"""
    
    # Define tables
    agencies = table('agencies',
        column('id', sa.UUID),
        column('name', sa.String),
        column('billing_email', sa.String),
        column('subscription_plan', sa.String),
        column('is_active', sa.Boolean),
        column('created_at', sa.DateTime)
    )
    
    teams = table('teams',
        column('id', sa.UUID),
        column('name', sa.String),
        column('description', sa.String),
        column('agency_id', sa.UUID),
        column('created_at', sa.DateTime)
    )
    
    users = table('users',
        column('id', sa.UUID),
        column('email', sa.String),
        column('full_name', sa.String),
        column('auth_provider', sa.Enum('GOOGLE', name='authprovider')),
        column('external_id', sa.String),
        column('email_verified', sa.Boolean),
        column('is_active', sa.Boolean),
        column('role', sa.Enum('AGENCY_ADMIN', 'TEAM_ADMIN', 'TEAM_USER', name='userrole')),
        column('agency_id', sa.UUID),
        column('team_id', sa.UUID),
        column('created_at', sa.DateTime)
    )
    
    invites = table('invites',
        column('id', sa.UUID),
        column('email', sa.String),
        column('role', sa.String),
        column('agency_id', sa.UUID),
        column('team_id', sa.UUID),
        column('invited_by_id', sa.UUID),
        column('token', sa.UUID),
        column('status', sa.Enum('PENDING', 'ACCEPTED', 'EXPIRED', 'REVOKED', name='invitestatus')),
        column('created_at', sa.DateTime),
        column('expires_at', sa.DateTime)
    )
    
    # Generate UUIDs
    agency_id = uuid.uuid4()
    seo_team_id = uuid.uuid4()
    social_team_id = uuid.uuid4()
    admin_user_id = uuid.uuid4()
    team_admin_id = uuid.uuid4()
    team_user_id = uuid.uuid4()
    
    now = datetime.utcnow()
    
    # Insert agency
    op.bulk_insert(agencies, [{
        'id': agency_id,
        'name': 'Acme Marketing',
        'billing_email': 'admin@acmemarketing.com',
        'subscription_plan': 'professional',
        'is_active': True,
        'created_at': now
    }])
    
    # Insert teams
    op.bulk_insert(teams, [
        {
            'id': seo_team_id,
            'name': 'SEO Department',
            'description': 'Technical SEO and content optimization',
            'agency_id': agency_id,
            'created_at': now
        },
        {
            'id': social_team_id,
            'name': 'Social Media Team',
            'description': 'Social media management and content creation',
            'agency_id': agency_id,
            'created_at': now
        }
    ])
    
    # Insert users
    op.bulk_insert(users, [
        {
            'id': admin_user_id,
            'email': 'admin@acmemarketing.com',
            'full_name': 'Alex Admin',
            'auth_provider': 'GOOGLE',
            'external_id': 'google-admin-123',
            'email_verified': True,
            'is_active': True,
            'role': 'AGENCY_ADMIN',
            'agency_id': agency_id,
            'team_id': None,
            'created_at': now
        },
        {
            'id': team_admin_id,
            'email': 'seo-lead@acmemarketing.com',
            'full_name': 'Sarah SEO Lead',
            'auth_provider': 'GOOGLE',
            'external_id': 'google-seo-lead-456',
            'email_verified': True,
            'is_active': True,
            'role': 'TEAM_ADMIN',
            'agency_id': agency_id,
            'team_id': seo_team_id,
            'created_at': now
        },
        {
            'id': team_user_id,
            'email': 'john@acmemarketing.com',
            'full_name': 'John Doe',
            'auth_provider': 'GOOGLE',
            'external_id': 'google-john-789',
            'email_verified': True,
            'is_active': True,
            'role': 'TEAM_USER',
            'agency_id': agency_id,
            'team_id': seo_team_id,
            'created_at': now
        }
    ])
    
    # Insert invites
    invite1_token = uuid.uuid4()
    invite2_token = uuid.uuid4()
    
    op.bulk_insert(invites, [
        {
            'id': uuid.uuid4(),
            'email': 'newuser@acmemarketing.com',
            'role': 'TEAM_USER',
            'agency_id': agency_id,
            'team_id': seo_team_id,
            'invited_by_id': admin_user_id,
            'token': invite1_token,
            'status': 'PENDING',
            'created_at': now,
            'expires_at': now + timedelta(days=7)
        },
        {
            'id': uuid.uuid4(),
            'email': 'social-manager@acmemarketing.com',
            'role': 'TEAM_ADMIN',
            'agency_id': agency_id,
            'team_id': social_team_id,
            'invited_by_id': admin_user_id,
            'token': invite2_token,
            'status': 'PENDING',
            'created_at': now,
            'expires_at': now + timedelta(days=7)
        }
    ])
    
    print(f"✅ Seeded test data:")
    print(f"   Agency: Acme Marketing ({agency_id})")
    print(f"   Admin: admin@acmemarketing.com")
    print(f"   Invite tokens: {invite1_token}, {invite2_token}")


def downgrade() -> None:
    """Remove test data"""
    op.execute("DELETE FROM invites WHERE email LIKE '%acmemarketing.com'")
    op.execute("DELETE FROM users WHERE email LIKE '%acmemarketing.com'")
    op.execute("DELETE FROM teams WHERE name IN ('SEO Department', 'Social Media Team')")
    op.execute("DELETE FROM agencies WHERE name = 'Acme Marketing'")
