# Enterprise-Grade Development Setup - Complete!

## ✅ What's Been Created

### 1. DevContainer Integration (`.devcontainer/devcontainer.json`)
- VS Code runs inside backend container
- All extensions pre-installed (Python, Pylance, Black, Docker, Copilot)
- Debugger configured
- Auto-format on save
- All 4 ports forwarded (8000, 3000, 5432, 6379)

**Usage:**
```bash
# In VS Code, press F1 → "Dev Containers: Reopen in Container"
# Your IDE now runs inside Docker with exact production dependencies
```

### 2. Azure Key Vault Integration (`backend/app/utils/secrets.py`)
**Features:**
- Single source of truth for secrets
- Local dev: Falls back to `.env` file
- Production: Reads from Azure Key Vault
- Managed Identity support (Azure Container Apps)
- Agency-specific secrets (`agency-{id}-{key}`)
- Convenience functions for common secrets

**Usage:**
```python
from app.utils.secrets import get_secret_manager, get_database_url, get_groq_api_key

# Get any secret
manager = get_secret_manager()
api_key = manager.get_secret("GROQ_API_KEY")

# Or use convenience functions
db_url = get_database_url()  # Constructs from vault secrets
groq_key = get_groq_api_key()

# Agency-specific secrets
semrush_key = get_agency_secret("uuid-123", "semrush_api_key")
```

### 3. Pre-commit Hooks (`.pre-commit-config.yaml`)
**What it does:**
- ✅ Black (auto-format Python)
- ✅ isort (sort imports)
- ✅ Flake8 (linting)
- ✅ detect-secrets (prevent hardcoded secrets)
- ✅ Bandit (security scanning)
- ✅ Hadolint (Dockerfile linting)
- ✅ Prettier (format TypeScript/CSS/JSON)
- ✅ YAML/JSON validation
- ✅ Conventional Commits (enforced commit message format)

**Setup:**
```bash
# Install
pip install pre-commit
pre-commit install

# Now every commit will:
# 1. Auto-format your code
# 2. Run security checks
# 3. Validate commit message
# 4. Block commit if issues found
```

### 4. GitHub Actions CI/CD (`.github/workflows/ci.yml`)
**Pipeline Stages:**

1. **Code Quality** (runs on every PR)
   - Black, isort, Flake8, MyPy (Python)
   - ESLint, TypeScript check (Frontend)

2. **Security Scan** (runs on every PR)
   - Bandit (Python vulnerabilities)
   - Safety (dependency vulnerabilities)
   - detect-secrets (hardcoded secrets)
   - Trivy (filesystem scan)

3. **Tests** (runs on every PR)
   - pytest with coverage (backend)
   - Jest with coverage (frontend)
   - Uploads to Codecov

4. **Build & Push** (main branch only)
   - Multi-stage Docker build
   - Push to Azure Container Registry
   - Trivy image scan

5. **Deploy Staging** (main branch only)
   - Azure Container Apps update
   - Connects to Key Vault

6. **UI Tests** (staging)
   - Playwright E2E tests
   - Uploads test reports

7. **Deploy Production** (manual approval)
   - Requires GitHub environment approval
   - Creates GitHub release

### 5. Security Configuration
- `.bandit.yml` - Security scanner rules
- `.secrets.baseline` - Baseline for detect-secrets
- `requirements.txt` - All security tools included

### 6. Updated Config (`backend/app/config.py`)
- Added Key Vault settings
- JWT configuration
- LLM API keys
- Environment-aware settings

---

## 🚀 How to Use Everything

### Local Development (with Key Vault)
```bash
# Set environment variables
export USE_AZURE_KEYVAULT=true
export AZURE_KEYVAULT_URL=https://teamai-dev.vault.azure.net/

# Log in to Azure
az login

# Start services (Key Vault client will authenticate via Azure CLI)
make up
```

### Local Development (without Key Vault)
```bash
# Uses .env file for secrets (default)
export USE_AZURE_KEYVAULT=false

make up
# Reads from .env file
```

### Pre-commit Hooks
```bash
# Install hooks
pip install pre-commit
pre-commit install

# Test all files
pre-commit run --all-files

# Now every git commit will auto-check
git commit -m "feat: add user authentication"
# → Auto-formats, lints, security scans
```

### CI/CD Setup (One-time)
1. **Create Azure Container Registry**
```bash
az acr create --resource-group teamai-rg \
              --name teamairegistry \
              --sku Basic
```

2. **Create Azure Key Vault**
```bash
# Staging
az keyvault create --name teamai-kv-staging \
                   --resource-group teamai-staging-rg

# Production
az keyvault create --name teamai-kv-prod \
                   --resource-group teamai-prod-rg
```

3. **Add GitHub Secrets** (Settings → Secrets and variables → Actions)
```
ACR_REGISTRY=teamairegistry.azurecr.io
ACR_USERNAME=<registry-username>
ACR_PASSWORD=<registry-password>
AZURE_CREDENTIALS=<service-principal-json>
KEYVAULT_URL_STAGING=https://teamai-kv-staging.vault.azure.net/
KEYVAULT_URL_PROD=https://teamai-kv-prod.vault.azure.net/
```

4. **Store Secrets in Key Vault**
```bash
az keyvault secret set --vault-name teamai-kv-staging \
                       --name DATABASE-PASSWORD \
                       --value "secure-password-here"

az keyvault secret set --vault-name teamai-kv-staging \
                       --name GROQ-API-KEY \
                       --value "gsk_xxx"
```

### DevContainer (VS Code)
```bash
# Open VS Code
code /workspaces/TeamAI

# Press F1 → "Dev Containers: Reopen in Container"
# Wait for container to build
# ✅ You're now coding inside Docker!

# All benefits:
# - IntelliSense uses container's Python
# - Debugger works with breakpoints
# - Terminal is inside container
# - Extensions auto-installed
```

---

## 📊 Benefits Summary

### Security
- ✅ Zero hardcoded secrets (Key Vault + detect-secrets)
- ✅ Automated vulnerability scanning (Bandit, Safety, Trivy)
- ✅ Secret rotation support (Key Vault managed)
- ✅ Audit trail of secret access

### Quality
- ✅ Enforced code standards (Black, Flake8, ESLint)
- ✅ Pre-commit hooks (catch issues before push)
- ✅ 80% test coverage target
- ✅ Type checking (MyPy, TypeScript)

### CI/CD
- ✅ Automated testing on every PR
- ✅ Security gates (block merge if vulnerabilities)
- ✅ Multi-stage deployments (staging → production)
- ✅ Manual approval for production
- ✅ Automated releases

### Developer Experience
- ✅ DevContainer (IDE inside Docker)
- ✅ Hot reload (edit → see changes)
- ✅ 2-minute onboarding (`make up`)
- ✅ Auto-formatting (no bikeshedding)

---

## 📝 Next Steps

### Immediate
1. **Install pre-commit hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Test Key Vault locally** (if you have Azure access)
   ```bash
   az login
   export USE_AZURE_KEYVAULT=true
   export AZURE_KEYVAULT_URL=https://your-kv.vault.azure.net/
   make up
   ```

3. **Try DevContainer** (VS Code users)
   - F1 → "Dev Containers: Reopen in Container"

### Before First Deploy
1. Create Azure resources (ACR, Key Vault, Container Apps)
2. Add GitHub Secrets
3. Store application secrets in Key Vault
4. Enable required GitHub Actions permissions

### Ongoing
- Every PR triggers full pipeline (quality + security + tests)
- Merging to main → auto-deploy staging
- Production requires manual approval
- Weekly dependency updates (Dependabot)

---

## 🔍 Verification Commands

```bash
# Check pre-commit hooks installed
pre-commit run --all-files

# Test Key Vault connection
python -c "from app.utils.secrets import get_secret_manager; print(get_secret_manager().use_keyvault)"

# Run security scans locally
bandit -r backend/app -c .bandit.yml
detect-secrets scan

# Check pipeline syntax
act -l  # (if you have 'act' installed)
```

---

**Status: Enterprise-grade infrastructure complete! Ready for Phase 1b: Auth Backend.**
