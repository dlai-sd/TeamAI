#!/usr/bin/env python3
"""
Quick script to add a pending invite for OAuth testing
Usage: python add_invite.py your.email@gmail.com [ROLE]
"""
import sys
from datetime import datetime, timedelta
import uuid

sys.path.insert(0, '/workspaces/TeamAI/backend')
from app.utils.db import SessionLocal
from sqlalchemy import text

def add_invite(email: str, role: str = "AGENCY_ADMIN"):
    """Add a pending invite for the given email"""
    
    valid_roles = ["AGENCY_ADMIN", "TEAM_ADMIN", "TEAM_USER"]
    if role not in valid_roles:
        print(f"❌ Invalid role: {role}. Must be one of: {valid_roles}")
        return False
    
    db = SessionLocal()
    
    try:
        # Check if invite already exists
        result = db.execute(
            text("SELECT email, status FROM invites WHERE email = :email"),
            {"email": email}
        )
        existing = result.fetchone()
        
        if existing:
            print(f"⚠️  Invite already exists for {email} (status: {existing[1]})")
            
            # Update if expired/revoked
            if existing[1] in ['EXPIRED', 'REVOKED']:
                db.execute(
                    text("""
                        UPDATE invites 
                        SET status = 'PENDING', 
                            expires_at = :expires_at,
                            created_at = :created_at
                        WHERE email = :email
                    """),
                    {
                        "email": email,
                        "expires_at": datetime.utcnow() + timedelta(days=7),
                        "created_at": datetime.utcnow()
                    }
                )
                db.commit()
                print(f"✅ Updated invite to PENDING status")
                return True
            else:
                print(f"   No changes made (status is {existing[1]})")
                return True
        
        # Get agency info
        result = db.execute(text("""
            SELECT 
                a.id as agency_id,
                t.id as team_id,
                u.id as admin_id
            FROM agencies a
            LEFT JOIN teams t ON t.agency_id = a.id
            LEFT JOIN users u ON u.agency_id = a.id AND u.role = 'AGENCY_ADMIN'
            WHERE a.name = 'Acme Marketing'
            LIMIT 1
        """))
        row = result.fetchone()
        
        if not row:
            print("❌ No agency found. Run migrations first: docker-compose exec backend alembic upgrade head")
            return False
        
        agency_id, team_id, admin_id = row
        
        # Create invite
        invite_id = str(uuid.uuid4())
        token = str(uuid.uuid4())
        now = datetime.utcnow()
        expires = now + timedelta(days=7)
        
        # NULL team_id for AGENCY_ADMIN, use team_id for others
        team_id_value = None if role == "AGENCY_ADMIN" else team_id
        
        db.execute(text("""
            INSERT INTO invites (id, email, role, agency_id, team_id, invited_by_id, token, status, created_at, expires_at)
            VALUES (:id, :email, :role, :agency_id, :team_id, :invited_by_id, :token, 'PENDING', :created_at, :expires_at)
        """), {
            "id": invite_id,
            "email": email,
            "role": role,
            "agency_id": agency_id,
            "team_id": team_id_value,
            "invited_by_id": admin_id,
            "token": token,
            "created_at": now,
            "expires_at": expires
        })
        
        db.commit()
        
        print(f"✅ Created invite for {email}")
        print(f"   Role: {role}")
        print(f"   Agency: Acme Marketing")
        print(f"   Team: {'None (Agency Admin)' if role == 'AGENCY_ADMIN' else 'SEO Department'}")
        print(f"   Expires: {expires.strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"\n🔗 Now try OAuth login at:")
        print(f"   https://upgraded-space-engine-q7j949p6jqjw34jqj-3000.app.github.dev/login")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_invite.py <email> [ROLE]")
        print("\nExamples:")
        print("  python add_invite.py you@gmail.com")
        print("  python add_invite.py teammate@gmail.com TEAM_USER")
        print("\nRoles: AGENCY_ADMIN (default), TEAM_ADMIN, TEAM_USER")
        sys.exit(1)
    
    email = sys.argv[1]
    role = sys.argv[2] if len(sys.argv) > 2 else "AGENCY_ADMIN"
    
    add_invite(email, role)
