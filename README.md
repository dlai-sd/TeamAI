# TeamAI

**Virtual AI Workforce for Digital Marketing Agencies**

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/dlai-sd/TeamAI/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Azure](https://img.shields.io/badge/deployed-Azure%20Container%20Apps-0078D4)](https://teamai-frontend.grayisland-ba13f170.eastus.azurecontainerapps.io/)

TeamAI is a B2B SaaS platform that enables digital marketing agencies to scale infinitely by deploying specialized AI agents as an "inorganic" workforce—eliminating the traditional bottlenecks of hiring costs and physical office space.

## 🎉 Version 0.1.0 Release (December 17, 2025)

**First production release with working AI agent execution!**

### What's Working
- ✅ **SEO Site Audit Agent** - Analyze any website for SEO issues using Groq AI
- ✅ **Google OAuth Authentication** - Secure sign-in with role-based access
- ✅ **3-Panel Dashboard** - Collapsible sidebar, agents/teams view, info panel
- ✅ **Real-time AI Execution** - ~2 second audits, ~$0.00007 per run
- ✅ **Azure Production Deployment** - Fully containerized, auto-scaling

### Live Demo
- **Frontend:** https://teamai-frontend.grayisland-ba13f170.eastus.azurecontainerapps.io/
- **Backend API:** https://teamai-backend.grayisland-ba13f170.eastus.azurecontainerapps.io/docs

---

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

## Test Coverage

**Current Status:** Production-ready test suite  
**Metrics:** 131 tests | 105 passing (80%) | 67% coverage | 0 errors

### Achievements
- ✅ Fixed all hanging tests (UNIQUE constraint resolution)
- ✅ Converted 13 API tests to AsyncClient for async endpoints
- ✅ Added 14 cookbook_loader tests (87% coverage)
- ✅ Added 48 component tests (cache_manager + rate_limiter at ~95% coverage)
- ✅ Exceeded all goals (70%+ passing, 70%+ coverage targets)

**Details:** See [Test Results Documentation](docs/TEST_RESULTS.md)
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
- [Azure Deployment Guide](docs/AZURE_DEPLOYMENT.md) - Production deployment and troubleshooting
- [Google OAuth Setup](docs/GOOGLE_OAUTH_SETUP.md) - OAuth configuration steps
- [Development Progress](docs/PROGRESS.md) - Detailed progress tracking

## License

MIT License - see [LICENSE](LICENSE) for details

## Contact

Project maintained by [dlai-sd](https://github.com/dlai-sd)

## Current Status

**Version:** 0.1.0 (December 17, 2025)  
**Phase:** ✅ Production MVP with Working AI Agent

### v0.1.0 Features
| Feature | Status | Description |
|---------|--------|-------------|
| **SEO Site Audit** | ✅ Live | Enter any URL, get AI-powered SEO analysis |
| **Google OAuth** | ✅ Live | Secure authentication with JWT tokens |
| **Dashboard** | ✅ Live | 3-panel layout with sidebar, agents view, info panel |
| **Agent Execution** | ✅ Live | Real Groq API calls (~2s, ~870 tokens, ~$0.00007) |
| **Azure Deployment** | ✅ Live | Container Apps with CI/CD |
| **Recipe Engine** | ✅ Live | YAML-defined workflows with LangGraph DAG |

### Production Metrics
- **Execution Time:** ~1.7-2.5 seconds per audit
- **Token Usage:** ~800-900 tokens per audit
- **Cost per Audit:** ~$0.00007 (Groq llama-3.1-8b-instant)
- **Infrastructure:** ~$96/month (Azure Container Apps + PostgreSQL + Redis)

### Production URLs
- 🌐 **Frontend:** https://teamai-frontend.grayisland-ba13f170.eastus.azurecontainerapps.io/
- 🔧 **Backend:** https://teamai-backend.grayisland-ba13f170.eastus.azurecontainerapps.io/
- 📖 **API Docs:** https://teamai-backend.grayisland-ba13f170.eastus.azurecontainerapps.io/docs

---

## Roadmap

### v0.2.0 (Planned)
- [ ] Social Media Scheduler Agent
- [ ] Lead Qualifier Agent  
- [ ] A/B Testing Framework
- [ ] User feedback collection
- [ ] Scheduled/cron-based tasks

### Future
- Customer-built cookbooks/recipes
- Modular pricing topups
- ML-powered quality scoring
- Multi-region deployment

---

## Contributing

This project follows a modular architecture enabling parallel development:
- `shared/`: API contracts and schemas (start here)
- `backend/`: Python + FastAPI (independent development)
- `frontend/`: React + TypeScript (independent development)
- `cookbooks/` & `recipes/`: YAML definitions (no code execution)

See [Architecture Documentation](docs/architecture.md) for details.