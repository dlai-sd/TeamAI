"""
Seed data for testing authentication system

Usage:
    docker-compose exec backend python tests/seed_data.py
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.utils.db import engine
from app.models.agency import Agency, Team, User, UserRole, AuthProvider
from app.models.invite import Invite, InviteStatus


async def seed_test_data():
    """Create test agency, teams, users, and invites"""
    
    # Create session directly
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print("🌱 Seeding test data...")
        
        # Check if data already exists
        result = await db.execute(select(Agency).filter(Agency.name == "Acme Marketing"))
        existing_agency = result.scalar_one_or_none()
        
        if existing_agency:
            print("✅ Test data already exists. Skipping seed.")
            return
        
        # Create test agency
        agency = Agency(
            name="Acme Marketing",
            billing_email="admin@acmemarketing.com",
            subscription_plan="professional",
            is_active=True
        )
        db.add(agency)
        await db.flush()
        print(f"✅ Created agency: {agency.name} (ID: {agency.id})")
        
        # Create test teams
        seo_team = Team(
            name="SEO Department",
            description="Technical SEO and content optimization",
            agency_id=agency.id
        )
        social_team = Team(
            name="Social Media Team",
            description="Social media management and content creation",
            agency_id=agency.id
        )
        db.add_all([seo_team, social_team])
        await db.flush()
        print(f"✅ Created teams: {seo_team.name}, {social_team.name}")
        
        # Create admin user (pre-registered with Google SSO)
        admin_user = User(
            email="admin@acmemarketing.com",
            full_name="Alex Admin",
            auth_provider=AuthProvider.GOOGLE,
            external_id="google-admin-123",
            email_verified=True,
            is_active=True,
            role=UserRole.AGENCY_ADMIN,
            agency_id=agency.id,
            team_id=None  # Admins not tied to specific team
        )
        db.add(admin_user)
        await db.flush()
        print(f"✅ Created admin user: {admin_user.email} (ID: {admin_user.id})")
        
        # Create team admin user
        team_admin_user = User(
            email="seo-lead@acmemarketing.com",
            full_name="Sarah SEO Lead",
            auth_provider=AuthProvider.GOOGLE,
            external_id="google-seo-lead-456",
            email_verified=True,
            is_active=True,
            role=UserRole.TEAM_ADMIN,
            agency_id=agency.id,
            team_id=seo_team.id
        )
        db.add(team_admin_user)
        await db.flush()
        print(f"✅ Created team admin: {team_admin_user.email}")
        
        # Create regular team user
        team_user = User(
            email="john@acmemarketing.com",
            full_name="John Doe",
            auth_provider=AuthProvider.GOOGLE,
            external_id="google-john-789",
            email_verified=True,
            is_active=True,
            role=UserRole.TEAM_USER,
            agency_id=agency.id,
            team_id=seo_team.id
        )
        db.add(team_user)
        await db.flush()
        print(f"✅ Created team user: {team_user.email}")
        
        # Create pending invites
        invite1 = Invite(
            email="newuser@acmemarketing.com",
            role=UserRole.TEAM_USER.value,
            agency_id=agency.id,
            team_id=seo_team.id,
            invited_by_id=admin_user.id,
            status=InviteStatus.PENDING
        )
        
        invite2 = Invite(
            email="social-manager@acmemarketing.com",
            role=UserRole.TEAM_ADMIN.value,
            agency_id=agency.id,
            team_id=social_team.id,
            invited_by_id=admin_user.id,
            status=InviteStatus.PENDING
        )
        
        db.add_all([invite1, invite2])
        await db.commit()
        print(f"✅ Created pending invites:")
        print(f"   - {invite1.email} → {seo_team.name} (Token: {invite1.token})")
        print(f"   - {invite2.email} → {social_team.name} (Token: {invite2.token})")
        
        print("\n🎉 Seed complete!")
        print(f"\n📋 Test Credentials:")
        print(f"   Agency: {agency.name}")
        print(f"   Admin: {admin_user.email} (Google SSO)")
        print(f"   Team Admin: {team_admin_user.email} (Google SSO)")
        print(f"   Team User: {team_user.email} (Google SSO)")
        print(f"\n🔗 Invite Links:")
        print(f"   - http://localhost:3000/accept-invite?token={invite1.token}")
        print(f"   - http://localhost:3000/accept-invite?token={invite2.token}")


if __name__ == "__main__":
    asyncio.run(seed_test_data())
