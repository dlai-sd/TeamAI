# TeamAI Development Progress

**Last Updated:** December 16, 2025 - End of Day  
**Current Phase:** Agent Runtime Complete + ML/AI Strategy Defined  
**Status:** Production infrastructure deployed, agent system functional, ready for architecture refactor and ML implementation

---

## 🎯 Today's Accomplishments (December 16, 2025)

### ✅ Agent Runtime Engine - Fully Functional
1. **Custom Recipe Evaluator (No LangChain Dependency):**
   - Built custom DAG executor for YAML recipe workflows
   - Implemented node execution with dependency resolution
   - Added template variable resolution with type coercion
   - Supports parallel execution and error handling

2. **Component Library Implemented:**
   - **WebCrawler:** Async HTTP client with BeautifulSoup parsing, SEO metadata extraction, rate limiting, mock mode
   - **LLMProcessor:** Groq API integration with automatic fallback (llama-3.1-8b-instant → llama-3.3-70b-versatile)
   - **ReportGenerator:** Markdown/JSON/HTML output formats with template support

3. **Groq API Integration:**
   - API key stored in backend/.env and Azure Key Vault
   - Successfully tested with real API (880 tokens, $0.000066 cost)
   - Fixed model naming (removed 'groq-' prefix)
   - Enhanced type handling for integer parameters
   - Added lxml parser for HTML parsing

4. **SEO Site Audit Recipe Tested:**
   - Executed site-audit.yaml on real website
   - WebCrawler → LLMProcessor → ReportGenerator workflow verified
   - Quality report generated with SEO analysis and recommendations
   - Mock mode functional for testing without API costs

### ✅ ML/AI Strategy Document Created
**Comprehensive planning document:** [docs/AI_ML_STRATEGY.md](docs/AI_ML_STRATEGY.md)

**Key Highlights:**
- **Strategic Rationale:** ML intelligence layer as competitive moat (not just automation)
- **Yashus Integration:** Lessons learned from single-user system (8 samples → 50% accuracy)
- **TeamAI Advantage:** Multi-tenant data flywheel (100K+ samples/month vs 600/year)
- **Traditional ML:** RandomForest for tabular prediction (quality scores, success rates)
- **Deep Learning Blend:** BERT for report quality, sentence-transformers for recommendations
- **Cost Analysis:** $150-300/month for full ML+DL stack (99.9% savings vs human labor)
- **Bootstrap Strategy:** Synthetic data → manual labeling → live collection → production excellence
- **Phased Roadmap:** MVP (Month 1) → Light DL (Month 3) → Full DL (Month 6) → Agent Designer (Month 12)
- **Milestone Planning:** Week-by-week deliverables with success metrics

**Game-Changing Vision:** Recipe generation from natural language ("Create agent for competitor backlink analysis" → executable YAML in 30 seconds)

---

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

### ✅ Complete Authentication System (Dec 16, 2025)
**Backend:**
- Google OAuth2 integration with JWT tokens (30min expiry)
- Role-Based Access Control (agency_admin, team_admin, team_user)
- Invite system for controlled user onboarding
- PostgreSQL with 3 Alembic migrations
- Sync SQLAlchemy (no async/await issues)
- Redis for OAuth state management
- Test data seeded (1 agency, 2 teams, 3 users, 2 pending invites)

**Frontend:**
- React 18 + TypeScript + Vite
- AuthContext for global auth state
- Protected routes with admin-level checks
- Login page with Google SSO button
- OAuth callback handler with token exchange
- Dashboard with stats and quick actions
- Admin invites page (create/list/revoke)
- Header with navigation and user menu

**Testing:**
- 23 comprehensive tests (all passed)
- Backend API tests (10 endpoints)
- Frontend UI tests (8 components)
- Integration tests (5 scenarios)
- Browser verification completed

**Azure Production Deployment:**
- Frontend: https://teamai-frontend.grayisland-ba13f170.eastus.azurecontainerapps.io/
- Backend: https://teamai-backend.grayisland-ba13f170.eastus.azurecontainerapps.io/
- PostgreSQL: teamai-db.postgres.database.azure.com (West US)
- Redis: teamai-redis.redis.cache.windows.net (East US)
- Container Registry: teamairegistry.azurecr.io
- All secrets stored in Azure Key Vault
- Automatic database migrations on startup
- Monthly cost: ~$143 (pre-startup credits)

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

## Next Steps (Priority Order)

### ✅ Completed - Azure Production Deployment
1. **Infrastructure Setup:**
   - ✅ Created Azure Resource Group (teamai-prod)
   - ✅ Deployed Container Apps (backend + frontend)
   - ✅ Configured PostgreSQL Flexible Server
   - ✅ Set up Redis Cache
   - ✅ Stored secrets in Azure Key Vault
   - ✅ Built and pushed Docker images to ACR
   - ✅ Added Google OAuth production redirect URI
   - ✅ Configured automatic database migrations

2. **Deployment Scripts Created:**
   - ✅ `scripts/azure-setup.sh` - Create all Azure resources
   - ✅ `scripts/azure-deploy.sh` - Build and deploy containers
   - ✅ `scripts/azure-cleanup.sh` - Teardown resources
   - ✅ `infrastructure/docker/startup.sh` - Auto-run migrations on backend start

## 📊 Progress Tracking

### Completed Phases ✅
- [x] **Phase 0:** Project setup, Docker infrastructure, database schema
- [x] **Phase 1:** Google OAuth2 authentication, JWT tokens, RBAC, invite system
- [x] **Phase 1.5:** Azure production deployment (Container Apps, PostgreSQL, Redis, Key Vault)
- [x] **Phase 1.75:** Agent runtime engine (Recipe Evaluator, Component Library, Groq API)
- [x] **Phase 1.9:** ML/AI strategic planning and roadmap definition

### Current Focus 🎯
**Architecture Compliance (Week of Dec 17-23, 2025):**
- [ ] Refactor to proper separation of concerns (Connectors vs Processors)
- [ ] Build Connectors library (WebsiteConnector, SemrushConnector, HubSpotConnector)
- [ ] Create Utils library (RateLimiter, CacheManager)
- [ ] Implement mandatory SubscriptionTracker component
- [ ] Update recipe evaluator to enforce compliance
- [ ] Create proper Cookbook YAML structure

**Architectural Gaps Identified:**
- ❌ `backend/components/connectors/` is empty (logic mixed into WebCrawler)
- ❌ `backend/components/utils/` is empty (no RateLimiter, CacheManager)
- ❌ No SubscriptionTracker component (mandatory compliance layer)
- ❌ Recipe YAML doesn't reference Connectors properly

---

## 🎯 Next Milestones (Priority Order)

### Immediate (Tomorrow - December 17, 2025)
1. **Test Production OAuth Flow:**
   - Open: https://teamai-frontend.grayisland-ba13f170.eastus.azurecontainerapps.io/
   - Click "Sign in with Google"
   - Authenticate with yogeshkhandge@gmail.com
   - Verify redirect to dashboard with JWT tokens
   - Test invite acceptance flow

2. **Verify Database Migrations:**
   - Check backend logs for Alembic migration output
   - Confirm all 3 migrations applied successfully
   - Test user creation and role assignment
   - Validate foreign key relationships

### Week 1 (December 17-23, 2025) - Architecture Refactor
**Goal:** Full compliance with "Kitchen Architecture" before building more features

**Tasks:**
1. **Extract Connectors (4 hours):**
   - Move HTTP client logic from WebCrawler to WebsiteConnector
   - Create base Connector class with auth/rate-limiting hooks
   - Build SemrushConnector skeleton (for future SEO data)
   - Update WebCrawler to use WebsiteConnector

2. **Build Utils Library (2 hours):**
   - RateLimiter: Redis-backed token bucket algorithm
   - CacheManager: Redis TTL cache for API responses
   - Logger: Structured logging with correlation IDs

3. **Mandatory SubscriptionTracker (30 minutes):**
   - Component that wraps every recipe execution
   - Meters: execution count, tokens used, execution time, cost incurred
   - Writes to audit_logs table after every run
   - Cannot be bypassed (enforced in recipe evaluator)

4. **Update Recipe YAML (15 minutes):**
   - Add explicit Connector references
   - Separate Connectors from Processors
   - Document required secrets per Connector

**Success Criteria:**
- ✅ All agent executions write to audit_logs
- ✅ WebCrawler only handles processing, not HTTP
- ✅ Rate limiting functional (prevent API throttling)
- ✅ Recipe YAML matches architectural diagram

---

### Month 1 (January 2026) - Traditional ML MVP
**Goal:** Ship working ML layer with 60%+ accuracy (Traditional ML only, no DL yet)

**Week 1-2: Data Generation & Pipeline**
- [ ] Build synthetic training data generator (1,000 samples: 500 rule-based + 500 Groq-generated)
- [ ] Create RandomForest training pipeline (scikit-learn)
- [ ] Implement A/B testing engine (recipe variant comparison)
- [ ] Build quality scoring system (1-5 star ratings → labels)
- [ ] Database schema: Create `ab_test_results`, `quality_feedback` tables

**Week 3: Manual Labeling & Retraining**
- [ ] Run 100 real website audits (volunteer agencies or internal)
- [ ] Manual rating: Review reports, assign 1-5 stars (8 hours total)
- [ ] Retrain model: 500 synthetic + 100 real = 600 samples
- [ ] Expected accuracy: 70% (vs 60% baseline)

**Week 4: Production Integration**
- [ ] Integrate ML inference into agent execution flow
- [ ] Admin dashboard: Model performance metrics, feature importance charts
- [ ] Capture user feedback on every execution (implicit + explicit)
- [ ] Weekly automated retraining pipeline (every Sunday)

**Deliverables:**
- ✅ Traditional ML layer operational (CPU inference, $0 cost)
- ✅ A/B testing framework functional (compare recipe v1 vs v2)
- ✅ Quality prediction API (<100ms latency)
- ✅ 60%+ accuracy on quality scoring

**Success Metrics:**
- 60% quality prediction accuracy (baseline with synthetic data)
- 80% A/B test winner selection correctness
- <100ms ML inference latency
- 0% increase in infrastructure cost (CPU-only)

---

### Month 2-3 (February-March 2026) - Light Deep Learning
**Goal:** Add user-visible DL features (quality badges, smart recommendations)

**Week 1-2: DL Infrastructure**
- [ ] Install DL stack: PyTorch 2.1.0, Transformers 4.35.0, ONNX runtime
- [ ] Fine-tune DistilBERT on 500 synthetic + 100 real reports
- [ ] Implement quality badge system ("Excellent Report (92% confidence)")
- [ ] Optimize: Batching, caching, lazy loading (95% use ML, 5% use DL)

**Week 3-4: Smart Recommendations**
- [ ] Generate recipe embeddings (sentence-transformers all-MiniLM-L6-v2)
- [ ] Build semantic similarity engine (cosine similarity)
- [ ] "What to run next" feature (based on recent results)
- [ ] A/B test: DL recommendations vs random suggestions

**Week 5-8: Production Tuning**
- [ ] Weekly DL retraining on GPU spot instances (Azure NC6s v3)
- [ ] Performance optimization: Sub-200ms DL inference latency
- [ ] User testing: 50 production agencies, collect feedback
- [ ] Cost monitoring: Target $150-200/month total

**Deliverables:**
- ✅ Report quality assessment (BERT classification)
- ✅ Quality badges visible in UI with confidence scores
- ✅ Smart recommendations with 40%+ click-through rate
- ✅ Optimized DL inference (<200ms latency)

**Success Metrics:**
- 75% quality badge accuracy (validated against human ratings)
- 40% recommendation CTR (vs 10% random baseline)
- <200ms DL inference latency
- User feedback: "System feels smart, not just automated"

---

### Month 4-6 (April-June 2026) - Full Deep Learning
**Goal:** Production-grade ML ops with 85%+ accuracy

**Advanced DL Features:**
- [ ] Anomaly detection (flag unusual patterns in execution logs)
- [ ] LLM-powered explanations ("Report quality is low because...")
- [ ] Recipe versioning intelligence (auto-promote winning variants)
- [ ] Cross-agency learning (anonymized pattern aggregation)
- [ ] Daily DL retraining (production ML ops)

**Performance Targets:**
- 85%+ quality prediction accuracy
- 60% recommendation CTR (6x baseline)
- <150ms combined ML+DL latency
- Net Promoter Score: +50 (industry-leading)

**Cost Target:** $200-300/month for full ML+DL stack

---

### Month 6-12 (July-December 2026) - Agent Designer (Game Changer)
**Goal:** Natural language → executable recipes (THE competitive moat)

**GPT-4 Fine-Tuning:**
- [ ] Collect 500 high-quality recipe examples
- [ ] Fine-tune GPT-4 on recipe YAML structures
- [ ] Build validation engine (safety checks, performance estimates)
- [ ] Create drag-drop UI with live preview

**Community Features:**
- [ ] User-generated recipe marketplace
- [ ] Recipe sharing and versioning
- [ ] Automated quality scoring for shared recipes
- [ ] Economic validation: Measure pricing power increase

**Expected Impact:**
- 80% first-attempt success rate (recipe executes without errors)
- 50% of new recipes are AI-generated (vs 0% today)
- 10x faster recipe creation (30 seconds vs 5 hours manual)
- 2-3x price increase justified ($250 → $600/agent)

**Competitive Moat:** 12-18 months to replicate (requires millions of training samples)

---

## 🔧 Technical Debt & Known Issues

### Critical (Must Fix Before Scale)
- ⚠️ **No SubscriptionTracker:** Agent executions don't write to audit_logs (billing risk)
- ⚠️ **Architecture Violation:** Connectors mixed into Processors (maintenance nightmare)
- ⚠️ **No Refresh Tokens:** Only 30min access tokens (poor UX, add refresh endpoint)
- ⚠️ **No Rate Limiting:** Components can hit API throttles (need Redis-backed limiter)

### Important (Fix in Phase 2)
- ⚠️ Database migrations run on every restart (add migration lock table)
- ⚠️ No monitoring/alerts configured (add Application Insights)
- ⚠️ No error boundary in frontend (unhandled exceptions crash app)
- ⚠️ Recipe YAML doesn't match architecture diagram (add explicit Connector refs)

### Nice-to-Have (Defer to Phase 3)
- ℹ️ Using Basic tier for Redis and PostgreSQL (upgrade for production scale)
- ℹ️ No custom domain (using *.azurecontainerapps.io URLs)
- ℹ️ No CI/CD pipeline (manual Docker builds/pushes)
- ℹ️ No automated backups for PostgreSQL (add point-in-time restore)

---

## 📁 Documentation Updates (Today)
- ✅ Created [docs/AI_ML_STRATEGY.md](docs/AI_ML_STRATEGY.md) - Comprehensive ML/AI roadmap
- ✅ Moved completion docs to docs/ folder:
  - `docs/AUTHENTICATION_COMPLETE.md`
  - `docs/DOCKER_SETUP_COMPLETE.md`
  - `docs/ENTERPRISE_SETUP_COMPLETE.md`
  - `docs/PROJECT_STRUCTURE.md`
  - `docs/UI_TEST_RESULTS.md`
- ✅ Updated README.md with current status and agent runtime progress
- ✅ Updated PROGRESS.md with detailed tracking and milestone planning

---

## 🎓 Key Learnings from Today

### Technical Insights
1. **Custom DAG executor > LangChain:** Simpler, faster, no dependency bloat (removed LangChain entirely)
2. **Type coercion matters:** YAML strings don't auto-convert to Python int/float (added explicit handling)
3. **Mock mode essential:** Test without API costs (saved $10+ in development)
4. **Groq is cheap & fast:** $0.000066 for 880 tokens (llama-3.1-8b-instant) vs OpenAI $0.001
5. **Multi-tenant data = moat:** 100K samples/month creates 24+ month competitive advantage

### Strategic Insights
1. **ML is THE differentiator:** Automation is commoditized, intelligence compounds over time
2. **User-visible features matter:** Quality badges > prompt optimization (users see badges, not prompts)
3. **Bootstrap with synthetic data:** Don't wait for real data (generate 1K samples in Week 0)
4. **Network effects dominate:** Each new agency makes ALL agents smarter (Yashus has no network effects)
5. **Recipe generation = game over:** Natural language → YAML is the magical feature competitors can't replicate

### Process Insights
1. **Document before implementing:** ML strategy doc prevents scope creep and misalignment
2. **Test with real API early:** Mock mode masks integration issues (model naming errors)
3. **Architecture compliance matters:** Cutting corners today = technical debt tomorrow
4. **Cost-conscious development:** $300/month ML is expensive until you compare to $400K/month humans (99.9% savings)

---

## 💰 Cost Analysis (Updated with ML/AI)

### Current Monthly Costs (100 Agencies)
| Component | Cost | Notes |
|-----------|------|-------|
| **Azure Container Apps (Frontend)** | $15 | 1 vCPU, 2GB RAM |
| **Azure Container Apps (Backend)** | $30 | 2 vCPU, 4GB RAM |
| **Azure Container Apps (PostgreSQL)** | $30 | Self-managed, 2 vCPU, 4GB RAM |
| **Azure Functions** | $20 | Consumption plan (1M executions) |
| **Azure Cache for Redis** | $15 | Basic C0 (250MB) |
| **Azure Blob Storage** | $2 | Hot tier (10GB) |
| **Azure Key Vault** | $1 | Standard tier |
| **Azure Container Registry** | $5 | Basic tier |
| **Groq API (LLM Inference)** | $50-100 | 100K executions × 1K tokens avg |
| **Traditional ML** | $0 | CPU inference (scikit-learn) |
| **Deep Learning (Future)** | $50-200 | DL inference + training |
| **Total (Current)** | **$168/month** | Infrastructure + Groq |
| **Total (With Light DL)** | **$218-268/month** | Add quality badges + recommendations |
| **Total (With Full DL)** | **$268-368/month** | Add anomaly detection + explanations |

**Per Agency Cost:** $1.68-3.68/month (vs human labor $6,667/month)  
**Gross Margin:** 90-98% (even with expensive DL)

### Revenue Projections (Conservative)
| Scenario | Agencies | ARPU | Monthly Revenue | Monthly Cost | Profit | Margin |
|----------|----------|------|-----------------|--------------|--------|--------|
| **MVP (Month 1)** | 10 | $250 | $2,500 | $180 | $2,320 | 92.8% |
| **Light DL (Month 3)** | 50 | $300 | $15,000 | $250 | $14,750 | 98.3% |
| **Full DL (Month 6)** | 100 | $400 | $40,000 | $368 | $39,632 | 99.1% |
| **Agent Designer (Month 12)** | 500 | $600 | $300,000 | $1,500 | $298,500 | 99.5% |

**Key Insight:** Even "expensive" $368/month ML stack delivers 99%+ margins at scale.

---

## 🚀 Deployment URLs (Quick Reference)

**Production Environment:**
- 🌐 **Frontend:** https://teamai-frontend.grayisland-ba13f170.eastus.azurecontainerapps.io/
- 🔧 **Backend:** https://teamai-backend.grayisland-ba13f170.eastus.azurecontainerapps.io/
- 📚 **API Docs:** https://teamai-backend.grayisland-ba13f170.eastus.azurecontainerapps.io/docs
- 💾 **PostgreSQL:** teamai-db.postgres.database.azure.com:5432
- ⚡ **Redis:** teamai-redis.redis.cache.windows.net:6379
- 🔐 **Key Vault:** https://teamai-vault.vault.azure.net/

**Local Development:**
- 🌐 **Frontend:** http://localhost:3000
- 🔧 **Backend:** http://localhost:8000
- 📚 **API Docs:** http://localhost:8000/docs
- 💾 **PostgreSQL:** localhost:5432
- ⚡ **Redis:** localhost:6379

---

## 📝 Git Commits (Today)
1. **Commit 823fb4f:** "feat: Configure Groq API integration and fix agent execution"
   - Added GROQ_API_KEY to backend/.env and Azure Key Vault
   - Fixed recipe YAML model names (removed 'groq-' prefix)
   - Enhanced recipe_evaluator type coercion (int, float, bool)
   - Added lxml==5.1.0 for BeautifulSoup HTML parsing
   - Successfully tested agent execution with real Groq API

2. **Final commit (pending):** "docs: Update README and PROGRESS with ML/AI strategy, move docs to docs/ folder"
   - Created comprehensive AI/ML strategy document
   - Moved 5 completion docs to docs/ folder
   - Updated README.md with agent runtime status
   - Updated PROGRESS.md with detailed milestone planning

---

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
