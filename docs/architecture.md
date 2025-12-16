# TeamAI Architecture

## System Overview

TeamAI is a B2B SaaS platform that provides digital marketing agencies with a virtual AI workforce. The platform enables agencies to "hire" specialized AI agents (SEO Specialist, Social Media Scheduler, Lead Qualifier) that can be dynamically allocated to different teams within the agency.

## Key Architectural Principles

### 1. Multi-Tenancy
- Single infrastructure serves multiple agencies
- Row-level security in PostgreSQL enforces data isolation
- Team-scoped secrets prevent cross-team access
- Redis keys namespaced by agency ID

### 2. Modular Composition
- Agents composed of: Cookbooks → Recipes → Components
- YAML-based configuration for cookbooks and recipes
- Global component library (shared across all agents)
- Recipes are parameterized templates (no code changes by customers)

### 3. Cost Optimization
- Groq for cheap LLM inference ($0.05-$0.60 per 1M tokens)
- Azure Functions Consumption Plan (JIT scaling)
- Self-managed PostgreSQL (~$30/month vs $100+ for managed)
- Single Azure Key Vault with namespacing ($0.03/10k ops)

### 4. Product Differentiators
- A/B Testing Framework (ML-driven recipe optimization)
- Mandatory Subscription Tracking (usage-based billing accuracy)
- Stateful Execution (Azure Durable Functions)

## Component Layers

See diagrams in `.github/copilot-instructions.md` for visual representation.

## Development Workflow

1. **Contracts-First**: Define OpenAPI specs in `shared/contracts/`
2. **Parallel Development**: Backend, frontend, and components developed independently
3. **Mock Mode**: All components support mock data for testing without external dependencies
4. **Integration**: Use Docker Compose for local full-stack testing

## Deployment

- **Development**: Docker Compose
- **Production**: Azure Container Apps (frontend/backend), Azure Functions (agents)
- **Database**: Self-managed PostgreSQL in Azure Container Apps
- **CI/CD**: GitHub Actions

See `docs/deployment-guide.md` for detailed instructions (coming soon).
