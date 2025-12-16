"""
Generate test JWT tokens for authentication testing

Usage:
    docker-compose exec backend python backend/tests/generate_test_tokens.py
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.security import create_access_token
from app.config import settings

# Test user IDs from seed data
test_users = {
    "admin": {
        "email": "admin@acmemarketing.com",
        "role": "AGENCY_ADMIN",
        "user_id": "google-admin-123"  # This should match external_id from seed
    },
    "team_admin": {
        "email": "seo-lead@acmemarketing.com",
        "role": "TEAM_ADMIN",
        "user_id": "google-seo-lead-456"
    },
    "team_user": {
        "email": "john@acmemarketing.com",
        "role": "TEAM_USER",
        "user_id": "google-john-789"
    }
}

print("🔑 Test JWT Tokens for Authentication\n")
print("=" * 80)

for user_type, user_data in test_users.items():
    token = create_access_token(data={"sub": user_data["user_id"]})
    
    print(f"\n{user_type.upper()} ({user_data['role']}):")
    print(f"Email: {user_data['email']}")
    print(f"Token: {token}")
    print(f"\nTest with curl:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/auth/me')
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/invites')
    print("-" * 80)

print("\n💡 Note: Tokens expire in 30 minutes. Re-run this script to generate fresh tokens.")
