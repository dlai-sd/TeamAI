# TeamAI

**Virtual AI Workforce for Digital Marketing Agencies**

TeamAI is a B2B SaaS platform that enables digital marketing agencies to scale infinitely by deploying specialized AI agents as an "inorganic" workforce—eliminating the traditional bottlenecks of hiring costs and physical office space.

## The Problem

Digital marketing agencies face a critical growth challenge: **revenue growth is linearly dependent on the cost of acquiring new human talent and physical infrastructure**. This creates an artificial ceiling on scalability.

## The Solution

TeamAI provides a **Virtual Staffing Marketplace** where agencies can instantly "hire" (subscribe to) AI agents specialized in roles like SEO Specialists, Content Writers, and Lead Qualifiers. These agents are:

- **Immediately deployable** (minutes vs months for human hiring)
- **Dynamically allocatable** (assign to different teams based on workload)
- **Accountable and measurable** (mandatory audit logs, performance tracking)
- **Cost-effective** (multifold savings vs human equivalents with 40%+ platform profit margins)

## Architecture Overview

### Three-Tier Hierarchy

```
Platform (Marketplace)
  └─> Agency (Subscription Management)
       └─> Teams (Agent Operators)
            └─> Agent Instances (Customized Workers)
```

### The "Kitchen" Architecture

**Agents are composed of modular building blocks:**

1. **Data Sources** - External systems (CRMs, Analytics, Databases)
2. **Connectors** - API adapters (HubSpot, Google Analytics, Semrush)
3. **Processors** - Data transformers (LLM wrappers, parsers, analyzers)
4. **Components** - Utilities (Authentication, Rate Limiting, Caching)
5. **Recipes** - Executable workflows (LangGraph DAGs)
6. **Cookbooks** - Capability packages (bundled recipes)
7. **Agents** - Deployed products (1+ Cookbooks + Subscription Tracking)

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend** | Python + FastAPI | Async support, lightweight, auto-docs |
| **Agent Framework** | LangChain + LangGraph | Recipe orchestration, DAG workflows |
| **Frontend** | React + TypeScript | Industry standard, type safety |
| **Runtime** | Azure Functions (Consumption) | JIT scaling, pay-per-execution |
| **LLM** | Groq (primary), OpenAI (fallback) | Cost efficiency ($0.05-$0.60/1M tokens) |
| **Database** | Self-managed PostgreSQL | ACID compliance, cost optimization |
| **Secrets** | Azure Key Vault | Multi-tenant with agency namespacing |
| **Deployment** | Docker + Azure Container Apps | Flexibility, containerized services |
| **CI/CD** | GitHub Actions | Free tier, integrated workflows |

**Cost Optimization:** Target 40%+ profit margin through Groq inference, consumption-based Functions, self-managed DB, single Key Vault, free tooling (BeautifulSoup, httpx, pypdf2).

## MVP Scope (1-Month Timeline)

### Initial Agent Offerings

1. **SEO Specialist** - Site audits, broken link checks, meta tag analysis
2. **Social Media Scheduler** - Content generation, trend analysis
3. **Lead Qualifier** - CRM scoring, email drafting

### Core Features

- **Agency Admin Portal** - Marketplace browsing, agent purchase, secret management, billing dashboard
- **Team Config Portal** - Task scheduling, agent interaction, performance monitoring
- **A/B Testing Framework** - Recipe versioning, parallel execution, ML-driven optimization (product differentiator)
- **Subscription Tracking** - Usage metering, audit logging, billing accuracy

### Deferred to Phase 2

- Customer-built cookbooks/recipes
- Modular pricing topups
- Scheduled/cron-based tasks
- Post-execution quality scoring (user ratings)

## Project Structure

```
TeamAI/
├── backend/                 # FastAPI application
│   ├── app/                # API routes and business logic
│   ├── agents/             # Agent orchestration
│   ├── components/         # Reusable building blocks
│   ├── tests/              # pytest suites
│   └── pyproject.toml      # Python dependencies
├── frontend/               # React + TypeScript
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── pages/         # Admin/Team portals
│   │   └── state/         # Redux/Zustand
│   ├── package.json
│   └── tsconfig.json
├── cookbooks/              # YAML agent definitions
├── recipes/                # YAML workflow templates
├── migrations/             # Alembic DB migrations
├── .github/workflows/      # CI/CD pipelines
├── docker-compose.yml      # Local development
└── Dockerfile              # Container builds
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Poetry (Python dependency management)
- Make (optional, for convenience commands)

### Quick Start (Docker)

```bash
# Clone repository
git clone https://github.com/dlai-sd/TeamAI.git
cd TeamAI

# Copy environment template
cp .env.example .env
# Edit .env with your configuration

# Start all services
make docker-up
# Or: docker-compose up -d

# Run database migrations
make migrate

# Access the application
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Local Development Setup

**Backend:**
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
# Or: make backend
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Or: make frontend
```

**Run Tests:**
```bash
make test           # All tests
make test-be        # Backend only
make test-fe        # Frontend only
```

### Available Make Commands

```bash
make help           # Show all available commands
make install        # Install all dependencies
make backend        # Run backend dev server
make frontend       # Run frontend dev server
make docker-up      # Start Docker services
make test           # Run all tests
make migrate        # Run database migrations
make format         # Format code (Black, Prettier)
make clean          # Clean build artifacts
```

## Documentation

- [AI Coding Agent Instructions](.github/copilot-instructions.md) - Complete architecture and development guidelines

## License

MIT License - see [LICENSE](LICENSE) for details

## Contact

Project maintained by [dlai-sd](https://github.com/dlai-sd)

## Current Status

**Phase:** ✅ Agent Runtime Complete + ML/AI Strategy Defined - Ready for Architecture Refactor

**Completed (December 16, 2025):**
- ✅ Architecture finalization (see [AI Instructions](.github/copilot-instructions.md))
- ✅ Complete project structure (monorepo with backend/frontend/shared)
- ✅ Database schema with 11 tables (agencies, teams, users, agents, subscriptions, audit logs)
- ✅ 3 Alembic migrations (initial schema, Google SSO, test data)
- ✅ Google OAuth2 authentication with JWT tokens (30min expiry)
- ✅ Role-Based Access Control (agency_admin, team_admin, team_user)
- ✅ Invite system for controlled user onboarding
- ✅ Backend API (FastAPI + SQLAlchemy + Redis)
- ✅ Frontend UI (React + TypeScript + Vite with AuthContext)
- ✅ Protected routes with admin-level checks
- ✅ 23 passing tests (backend API + frontend UI + integration)
- ✅ Docker multi-stage builds (development + production)
- ✅ Azure production deployment (Container Apps + PostgreSQL + Redis + Key Vault)
- ✅ **Agent Runtime Engine (Recipe Evaluator with custom DAG executor)**
- ✅ **Component Library (WebCrawler, LLMProcessor, ReportGenerator)**
- ✅ **Groq API Integration (llama-3.1-8b-instant + llama-3.3-70b-versatile fallback)**
- ✅ **SEO Specialist Recipe (site-audit.yaml with real API testing)**
- ✅ **Comprehensive ML/AI Strategy Document ([docs/AI_ML_STRATEGY.md](docs/AI_ML_STRATEGY.md))**

**Production Environment:**
- 🌐 Frontend: https://teamai-frontend.grayisland-ba13f170.eastus.azurecontainerapps.io/
- 🔧 Backend: https://teamai-backend.grayisland-ba13f170.eastus.azurecontainerapps.io/
- 💾 PostgreSQL: teamai-db.postgres.database.azure.com (West US)
- ⚡ Redis: teamai-redis.redis.cache.windows.net (East US)
- 🔐 Secrets: Azure Key Vault (teamai-vault) with Groq API key
- 📦 Registry: teamairegistry.azurecr.io
- 💰 Monthly Cost: ~$143 infrastructure + $50-300 ML/AI (awaiting startup credits)

**Agent Runtime Verified:**
- Successfully executed SEO site-audit recipe on real website
- Groq LLM integration working (880 tokens, $0.000066 cost)
- Mock mode functional for testing without API costs
- Recipe evaluator handles type coercion and template variables

**Next Steps (Priority Order):**
1. **Tomorrow:** Test production OAuth flow + verify database migrations
2. **Week 1:** Refactor to architectural compliance (Connectors, Utils, SubscriptionTracker)
3. **Month 1:** Implement Traditional ML layer (RandomForest, A/B testing, quality scoring)
4. **Month 2-3:** Add Deep Learning features (quality badges, smart recommendations)
5. **Month 6+:** Recipe generation "Agent Designer" (natural language → YAML)

**Strategic Focus:** Building intelligent, self-improving agent system with multi-tenant data flywheel as competitive moat. See [AI/ML Strategy](docs/AI_ML_STRATEGY.md) for detailed roadmap.

**Timeline:** Architecture refactor (1 week) → ML MVP (4 weeks) → Light DL (8 weeks) → Full DL (16 weeks)

---

## Contributing

This project follows a modular architecture enabling parallel development:
- `shared/`: API contracts and schemas (start here)
- `backend/`: Python + FastAPI (independent development)
- `frontend/`: React + TypeScript (independent development)
- `cookbooks/` & `recipes/`: YAML definitions (no code execution)

See [Architecture Documentation](docs/architecture.md) for details.