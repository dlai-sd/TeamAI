# Phase 1a Complete: Database Foundation ✅

## Docker-First Development Setup ✅

**All services running in Docker with hot reload:**
```bash
make up              # Start all services
make logs            # View logs (Ctrl+C to exit)
make shell-backend   # Open backend shell
make db-shell        # Open PostgreSQL shell
make down            # Stop all services
```

**Services:**
- **Backend**: http://localhost:8000 (FastAPI with auto-reload)
- **Backend Docs**: http://localhost:8000/docs (Swagger UI)
- **Frontend**: http://localhost:3000 (Vite dev server with HMR)
- **PostgreSQL**: localhost:5432 (teamai/teamai_dev_password)
- **Redis**: localhost:6379

**Hot Reload Enabled:**
- Edit `backend/app/**/*.py` → Backend reloads automatically
- Edit `frontend/src/**/*` → Frontend HMR updates browser
- No manual restarts needed!

**Multi-Stage Dockerfiles:**
- `development` target: Hot reload, debug mode, test dependencies
- `production` target: Optimized, multi-worker, non-root user, nginx for frontend

## What's Done

### 1. Database Models Created
All 11 tables with proper relationships:

**Core Entities:**
- ✅ `agencies` - Top-level tenant (agency_id is everywhere)
- ✅ `teams` - Departments within agencies
- ✅ `users` - Agency admins and team members (role: agency_admin | team_member)

**Agent System:**
- ✅ `agent_roles` - Agent templates (SEO Specialist, Social Media Scheduler, etc.)
- ✅ `cookbooks` - Capability bundles (references agent_roles)
- ✅ `recipes` - Executable workflows (YAML stored as JSONB)
- ✅ `agent_instances` - Deployed agents (custom_name, avatar_icon, configuration)

**Business Logic:**
- ✅ `subscriptions` - Track purchased/allocated/active agents per agency
- ✅ `secret_locker` - Store encrypted API keys (agency-scoped, team-scoped)

**Operations:**
- ✅ `audit_logs` - Execution tracking for billing (tokens, cost, execution time)
- ✅ `task_queue` - Pending/running/completed agent tasks
- ✅ `ab_test_results` - Recipe performance data for ML optimization

### 2. Database Infrastructure
- ✅ SQLAlchemy models with proper types (UUID, JSONB, Numeric)
- ✅ Foreign key relationships with CASCADE/SET NULL
- ✅ Indexes on critical columns (users.email, audit_logs.timestamp, task_queue.created_at)
- ✅ Alembic migration system configured
- ✅ Initial migration generated and applied
- ✅ PostgreSQL running in Docker (teamai-postgres container)

### 3. Multi-Tenancy Features
- ✅ All tables include agency_id for row-level security
- ✅ Teams scoped to agencies (team.agency_id FK)
- ✅ Users scoped to agencies + optional team assignment
- ✅ Secrets can be agency-wide or team-scoped (secret_locker.team_id nullable)
- ✅ Agent instances tied to teams (no cross-team access)

## Database Connection Info
```bash
# Local Docker
Host: localhost
Port: 5432
Database: teamai
User: teamai
Password: teamai_dev_password

# Connection String (already in .env.example)
DATABASE_URL=postgresql://teamai:teamai_dev_password@localhost:5432/teamai
```

## Verify Database
```bash
# Check all tables
docker exec teamai-postgres psql -U teamai -d teamai -c "\dt"

# Inspect a specific table
docker exec teamai-postgres psql -U teamai -d teamai -c "\d users"

# List all schemas
cd backend && PYTHONPATH=/workspaces/TeamAI/backend alembic history
```

## File Structure
```
backend/
├── app/
│   ├── models/
│   │   ├── __init__.py         # Exports all models
│   │   ├── agency.py           # Agency, Team, User
│   │   ├── agent.py            # AgentRole, Cookbook, Recipe, AgentInstance
│   │   ├── subscription.py     # Subscription, SecretLocker
│   │   └── audit.py            # AuditLog, TaskQueue, ABTestResult
│   └── utils/
│       └── db.py               # SQLAlchemy engine, session, Base
├── migrations/
│   ├── env.py                  # Alembic environment
│   ├── script.py.mako          # Migration template
│   └── versions/
│       └── 20251216_1059_initial_schema_*.py  # Generated migration
├── alembic.ini                 # Alembic configuration
└── pyproject.toml              # Dependencies (SQLAlchemy, Alembic, psycopg2)
```

## Next Steps (Phase 1b: Auth Backend)

### Create These Files:
1. `backend/app/utils/security.py` - Password hashing (bcrypt), JWT generation
2. `backend/app/models/schemas.py` - Pydantic request/response models
3. `backend/app/api/auth.py` - FastAPI routes: POST /auth/register, POST /auth/login, GET /auth/me
4. `backend/app/services/auth_service.py` - Business logic (create user, verify password)

### What We'll Build:
- **POST /auth/register** - Create new agency + admin user (atomic transaction)
- **POST /auth/login** - Email/password → JWT token (role in payload)
- **GET /auth/me** - Get current user info (requires JWT)
- **JWT Payload**: `{user_id, email, role, agency_id, team_id?}`

### Tools to Test:
- **Postman**: Manual API testing
- **pytest**: Automated tests in `backend/tests/test_api/test_auth.py`

---

**Status**: Database foundation complete. Ready for auth backend development!
