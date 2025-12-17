# Azure Deployment Guide

**Last Updated:** December 17, 2025  
**Status:** Production deployment verified and working

---

## Current Azure Infrastructure

| Resource | Name | Region | Configuration |
|----------|------|--------|---------------|
| **Resource Group** | teamai-prod | East US | Contains all resources |
| **Container Apps Env** | teamai-env | East US | Shared networking |
| **Frontend** | teamai-frontend | East US | 1 vCPU, 2GB RAM, nginx |
| **Backend** | teamai-backend | East US | 2 vCPU, 4GB RAM, FastAPI |
| **PostgreSQL** | teamai-db | East US | Flexible Server, B2s |
| **Redis** | teamai-redis | East US | Basic C0, 250MB |
| **Key Vault** | teamai-vault | East US | Standard tier |
| **Container Registry** | teamairegistry | East US | Basic tier |

### Live URLs
- **Frontend:** https://teamai-frontend.grayisland-ba13f170.eastus.azurecontainerapps.io
- **Backend:** https://teamai-backend.grayisland-ba13f170.eastus.azurecontainerapps.io
- **API Docs:** https://teamai-backend.grayisland-ba13f170.eastus.azurecontainerapps.io/docs

---

## Critical Configuration Lessons

### 1. DATABASE_URL Password Encoding
**Problem:** Passwords with special characters (`@`, `!`, `#`, etc.) break connection strings.

**Solution:** URL-encode special characters in the password portion:
```bash
# Original password: MyP@ss!123
# Encoded password: MyP%40ss%21123

# Wrong:
DATABASE_URL=postgresql://user:MyP@ss!123@host:5432/db

# Correct:
DATABASE_URL=postgresql://user:MyP%40ss%21123@host:5432/db
```

**Common encodings:**
| Character | Encoded |
|-----------|---------|
| `@` | `%40` |
| `!` | `%21` |
| `#` | `%23` |
| `$` | `%24` |
| `%` | `%25` |
| `&` | `%26` |
| `+` | `%2B` |
| `/` | `%2F` |
| `=` | `%3D` |

### 2. PostgreSQL Firewall for Container Apps
**Problem:** Azure Container Apps cannot connect to PostgreSQL by default.

**Solution:** Add firewall rule to allow Azure services:
```bash
az postgres flexible-server firewall-rule create \
  --resource-group teamai-prod \
  --name teamai-db \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

**Note:** This allows all Azure services. For stricter security, use VNet integration.

### 3. Redis SSL Scheme
**Problem:** Azure Redis requires TLS. Using `redis://` fails silently or refuses connection.

**Solution:** Use `rediss://` (double 's') for SSL connections:
```bash
# Wrong:
REDIS_URL=redis://:password@host:6380

# Correct:
REDIS_URL=rediss://:password@host:6380
```

### 4. Backend Environment Variables
**Problem:** OAuth redirects fail if backend doesn't know its public URL.

**Required env vars in Azure Container App:**
```bash
# For OAuth redirect_uri (where Google sends auth code)
BACKEND_URL=https://teamai-backend.grayisland-ba13f170.eastus.azurecontainerapps.io

# For post-auth redirect (where user lands after login)
FRONTEND_URL=https://teamai-frontend.grayisland-ba13f170.eastus.azurecontainerapps.io
```

**Set via Azure CLI:**
```bash
az containerapp update --name teamai-backend --resource-group teamai-prod \
  --set-env-vars \
    "BACKEND_URL=https://teamai-backend.grayisland-ba13f170.eastus.azurecontainerapps.io" \
    "FRONTEND_URL=https://teamai-frontend.grayisland-ba13f170.eastus.azurecontainerapps.io"
```

### 5. Frontend API URL Injection
**Problem:** Vite's `import.meta.env` doesn't work reliably in Docker builds.

**Solution:** Use Vite's `define` feature in `vite.config.ts`:
```typescript
export default defineConfig({
  define: {
    '__API_BASE_URL__': JSON.stringify(
      process.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
    )
  },
  // ...
});
```

Then in TypeScript files:
```typescript
declare const __API_BASE_URL__: string;
const API_BASE_URL = __API_BASE_URL__;
```

The Dockerfile sets the env var at build time:
```dockerfile
ENV VITE_API_BASE_URL=https://teamai-backend.../api
RUN npm run build
```

---

## Key Vault Secrets

Required secrets stored in `teamai-vault`:

| Secret Name | Description | Format |
|-------------|-------------|--------|
| `DATABASE-URL` | PostgreSQL connection | `postgresql://user:pass@host:5432/db` |
| `REDIS-URL` | Redis connection | `rediss://:password@host:6380` |
| `GOOGLE-CLIENT-ID` | OAuth client ID | From Google Console |
| `GOOGLE-CLIENT-SECRET` | OAuth client secret | From Google Console |
| `JWT-SECRET-KEY` | Token signing key | Random 64+ char string |
| `GROQ-API-KEY` | LLM API key | From Groq Console |

**Note:** Use hyphens (`-`) in Key Vault secret names, not underscores.

---

## CI/CD Pipeline

GitHub Actions workflow: `.github/workflows/azure-deploy.yml`

**Triggers:** Push to `main` branch

**Steps:**
1. Checkout code
2. Login to Azure (service principal)
3. Login to ACR
4. Build & push backend image (with `--no-cache` for consistency)
5. Build & push frontend image (with `--no-cache` for env var injection)
6. Deploy backend to Container Apps
7. Deploy frontend to Container Apps

**Required GitHub Secrets:**
- `AZURE_CREDENTIALS` - Service principal JSON
- `AZURE_SUBSCRIPTION_ID` - Subscription ID
- `AZURE_ACR_USERNAME` - Registry username
- `AZURE_ACR_PASSWORD` - Registry password

---

## Google OAuth Configuration

**Google Cloud Console:** https://console.cloud.google.com/apis/credentials

**Authorized redirect URIs:**
```
https://teamai-backend.grayisland-ba13f170.eastus.azurecontainerapps.io/api/v1/auth/google/callback
```

**Important:** The callback path is `/api/v1/auth/google/callback`, not `/oauth2/callback`.

---

## First User Setup (Bootstrap)

New deployments have no users. Use the bootstrap endpoint:

```bash
curl -X POST "https://teamai-backend.../api/v1/invites/bootstrap" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "bootstrap_secret": "teamai-bootstrap-2024"
  }'
```

This creates:
- A new agency ("Bootstrap Agency")
- An AGENCY_ADMIN invite for the email
- 7-day expiry

Then login via Google OAuth with that email.

---

## Deployment Commands

### Manual Deployment
```bash
# Login to Azure
az login

# Build and push images
az acr login --name teamairegistry
docker build -f infrastructure/docker/Dockerfile.backend -t teamairegistry.azurecr.io/backend:latest .
docker build -f infrastructure/docker/Dockerfile.frontend -t teamairegistry.azurecr.io/frontend:latest .
docker push teamairegistry.azurecr.io/backend:latest
docker push teamairegistry.azurecr.io/frontend:latest

# Deploy
az containerapp update --name teamai-backend --resource-group teamai-prod \
  --image teamairegistry.azurecr.io/backend:latest
az containerapp update --name teamai-frontend --resource-group teamai-prod \
  --image teamairegistry.azurecr.io/frontend:latest
```

### Check Logs
```bash
# Backend logs
az containerapp logs show --name teamai-backend --resource-group teamai-prod --type console --tail 100

# Frontend logs
az containerapp logs show --name teamai-frontend --resource-group teamai-prod --type console --tail 100
```

### Debug Config
```bash
curl https://teamai-backend.grayisland-ba13f170.eastus.azurecontainerapps.io/debug/config
```

---

## Cost Breakdown (Estimated Monthly)

| Service | Configuration | Cost |
|---------|--------------|------|
| Container Apps (Frontend) | 1 vCPU, 2GB | $15 |
| Container Apps (Backend) | 2 vCPU, 4GB | $30 |
| PostgreSQL Flexible Server | B2s | $30 |
| Redis Cache | Basic C0 | $15 |
| Key Vault | ~1000 ops/day | $1 |
| Container Registry | Basic | $5 |
| **Total** | | **~$96/month** |

---

## Troubleshooting

### Backend returns 502
- Check container logs for startup errors
- Verify DATABASE_URL is accessible (firewall rules)
- Verify REDIS_URL uses `rediss://` scheme

### OAuth redirect fails
- Verify BACKEND_URL env var is set
- Verify Google Console has correct redirect URI
- Check callback path matches (`/api/v1/auth/google/callback`)

### Frontend shows localhost API calls
- Rebuild frontend with `--no-cache`
- Verify VITE_API_BASE_URL in Dockerfile
- Check browser DevTools Network tab for actual URLs

### "No valid invitation found"
- Use bootstrap endpoint to create first admin
- Check invite hasn't expired (7-day default)
- Verify email matches exactly (case-sensitive)

### Database connection refused
- Add AllowAzureServices firewall rule
- Check password URL encoding
- Verify SSL mode in connection string
