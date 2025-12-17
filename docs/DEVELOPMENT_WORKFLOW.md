# Development Workflow Comparison

## Current Docker Approach vs. Local Hybrid

### Option 1: Full Docker Stack (Current)

**Workflow:**
```bash
# Make code change
vim backend/agents/recipe_evaluator.py

# Rebuild and restart (SLOW)
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d

# Run tests
docker exec teamai-backend pytest tests/
```

**Pros:**
- ✅ Consistent environment across all developers
- ✅ Matches production setup exactly
- ✅ No local Python/Node installation needed
- ✅ Database isolation

**Cons:**
- ❌ **Slow iteration**: 30-60s rebuild cycle per change
- ❌ **Cache issues**: Docker layer caching can be unreliable
- ❌ **Resource heavy**: Multiple containers + full images
- ❌ **Debugging harder**: Logs buried in containers
- ❌ **Test execution**: 5-10s overhead to exec into container

**Time per iteration**: ~45 seconds (rebuild) + 10 seconds (test) = **55 seconds**

---

### Option 2: Local Hybrid (Recommended for Iteration)

**Workflow:**
```bash
# One-time setup (5 minutes)
./scripts/dev-setup.sh

# Terminal 1 - Backend (auto-reload)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend (auto-reload)
cd frontend
npm run dev

# Terminal 3 - Tests (instant)
./scripts/test-fast.sh tests/test_agents/
```

**Pros:**
- ✅ **Instant iteration**: Edit → Save → Auto-reload (< 2s)
- ✅ **Fast tests**: Run pytest directly (no Docker exec)
- ✅ **Better debugging**: Direct access to logs, pdb, breakpoints
- ✅ **IDE integration**: Full IntelliSense, linting, type checking
- ✅ **Watch mode**: Auto-run tests on file change

**Cons:**
- ⚠️ Requires local Python 3.11+ and Node.js 18+
- ⚠️ Still uses Docker for databases (manageable)
- ⚠️ Environment differences possible (mitigated with venv)

**Time per iteration**: Edit → **< 2 seconds** (auto-reload) + **1 second** (test) = **3 seconds**

---

## Speed Comparison

| Action | Docker | Local Hybrid | Speedup |
|--------|--------|--------------|---------|
| Initial setup | 10 min | 5 min | 2x faster |
| Code change → Test | 55s | 3s | **18x faster** |
| Backend restart | 30s | < 2s | **15x faster** |
| Frontend rebuild | 45s | < 1s (HMR) | **45x faster** |
| Single test | 8s | 1s | **8x faster** |
| Full test suite | 60s | 15s | **4x faster** |

---

## Recommended Setup for Intense Testing Session

### Step 1: Initial Setup (One-time, 5 minutes)
```bash
./scripts/dev-setup.sh
```

This will:
- Start PostgreSQL and Redis in Docker
- Create Python venv
- Install all dependencies
- Run database migrations
- Create .env files

### Step 2: Start Development Servers

**Terminal 1 - Backend (with auto-reload):**
```bash
cd /workspaces/TeamAI/backend
source venv/bin/activate
export DATABASE_URL="postgresql://teamai:teamai_dev_password@localhost:5432/teamai"
export REDIS_URL="redis://localhost:6379/0"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend (with HMR):**
```bash
cd /workspaces/TeamAI/frontend
npm run dev
```

**Terminal 3 - Watch Tests (auto-run on change):**
```bash
cd /workspaces/TeamAI/backend
source venv/bin/activate
pip install pytest-watch
ptw tests/ -- -x --tb=short
```

### Step 3: Rapid Iteration Loop

```
Edit file → Save → Tests auto-run → Fix → Save → Tests auto-run
```

**No manual commands needed!**

---

## Hybrid Architecture Diagram

```
┌─────────────────────────────────────────────┐
│  Local Development (Fast Iteration)         │
├─────────────────────────────────────────────┤
│                                             │
│  Terminal 1: Backend (uvicorn --reload)    │
│  └─ Python venv with hot reload            │
│     └─ Edit .py → Auto-restart (< 2s)      │
│                                             │
│  Terminal 2: Frontend (npm run dev)        │
│  └─ Vite dev server with HMR               │
│     └─ Edit .tsx → Hot reload (< 1s)       │
│                                             │
│  Terminal 3: Tests (pytest-watch)          │
│  └─ Auto-run on file change                │
│     └─ Edit test → Auto-test (< 1s)        │
│                                             │
└─────────────────────────────────────────────┘
                    ▼
        Network: localhost
                    ▼
┌─────────────────────────────────────────────┐
│  Docker Services (Stateful Data)           │
├─────────────────────────────────────────────┤
│                                             │
│  📦 PostgreSQL (port 5432)                  │
│  └─ Persistent data volume                 │
│                                             │
│  📦 Redis (port 6379)                       │
│  └─ Cache and rate limiting                │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Testing Strategies

### During Development (Fast)
```bash
# Run specific test while coding
./scripts/test-fast.sh tests/test_agents/test_recipe_evaluator.py::TestDAGExecution

# Watch mode (auto-run on save)
cd backend && ptw tests/test_agents/ -- -x
```

### Before Commit (Thorough)
```bash
# All backend tests
./scripts/test-fast.sh tests/ -v

# All frontend tests
cd frontend && npm run test

# Linting
cd backend && black . && pylint app/
cd frontend && npm run lint
```

### CI Pipeline (Full Docker)
```bash
# GitHub Actions uses full Docker for consistency
docker-compose build
docker-compose up -d
./scripts/run-tests.sh
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Activate venv
```bash
source backend/venv/bin/activate
```

### Issue: "Connection refused to localhost:5432"
**Solution**: Start Docker databases
```bash
docker compose up -d postgres redis
docker compose ps  # Verify running
```

### Issue: "Port already in use"
**Solution**: Stop conflicting services
```bash
# Check what's using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### Issue: Tests fail with DB errors
**Solution**: Run migrations
```bash
cd backend
source venv/bin/activate
export DATABASE_URL="postgresql://teamai:teamai_dev_password@localhost:5432/teamai"
alembic upgrade head
```

---

## Migration Path

### If you want to switch back to Docker:
```bash
# Stop local servers (Ctrl+C in terminals)
# Start Docker stack
docker-compose up -d

# Tests now run in Docker
docker exec teamai-backend pytest tests/
```

### Best of both worlds:
```bash
# Development: Use local hybrid (fast iteration)
./scripts/dev-setup.sh

# Production verification: Use Docker (exact environment)
docker-compose up -d
./scripts/run-tests.sh
```

---

## Recommendation for Intense Testing Session

**Use Local Hybrid Setup:**

1. **Setup**: `./scripts/dev-setup.sh` (one-time, 5 min)
2. **Start servers**: Backend + Frontend terminals (auto-reload)
3. **Watch tests**: `ptw tests/` (auto-run on save)
4. **Iterate**: Edit → Save → Tests run automatically

**Expected velocity**: 
- 10-20 test iterations per hour (Docker)
- **100-200 test iterations per hour (Local Hybrid)** ⚡

**Switch to Docker** only when:
- Need exact production environment
- Testing Docker-specific issues
- Running CI/CD pipeline
- Sharing environment with team

---

## Next Steps

Choose your path:

**A) Local Hybrid (Recommended)**
```bash
./scripts/dev-setup.sh
# Follow on-screen instructions
```

**B) Stay with Docker**
```bash
# Already configured - no changes needed
docker-compose up -d
```

**C) Hybrid for now, Docker for CI**
```bash
# Use local for development
./scripts/dev-setup.sh

# Commit includes Docker config for CI
# GitHub Actions will use docker-compose
```

What's your preference?
