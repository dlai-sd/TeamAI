# 🚀 Deployment Guide - Assessment Tool

## Quick Deployment Options

### Option 1: Docker Compose (Local/Dev)
**Time**: 5 minutes  
**Cost**: $0

```bash
# Start services
cd /workspaces/TeamAI/assessment-tool
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

### Option 2: Azure Container Apps (Production)
**Time**: 30 minutes  
**Cost**: ~$115/month

#### Prerequisites
- Azure CLI installed
- Azure subscription active
- Docker installed

#### Step 1: Build Images
```bash
cd /workspaces/TeamAI/assessment-tool

# Backend
docker build -f infrastructure/docker/Dockerfile.backend -t assessment-backend:latest .

# Frontend
docker build -f infrastructure/docker/Dockerfile.frontend -t assessment-frontend:latest .
```

#### Step 2: Push to Azure Container Registry
```bash
# Login
az login
az acr login --name teamairegistry

# Tag images
docker tag assessment-backend:latest teamairegistry.azurecr.io/assessment-backend:latest
docker tag assessment-frontend:latest teamairegistry.azurecr.io/assessment-frontend:latest

# Push
docker push teamairegistry.azurecr.io/assessment-backend:latest
docker push teamairegistry.azurecr.io/assessment-frontend:latest
```

#### Step 3: Deploy to Container Apps
```bash
# Deploy backend
az containerapp create \
  --name assessment-backend \
  --resource-group teamai-prod \
  --environment teamai-env \
  --image teamairegistry.azurecr.io/assessment-backend:latest \
  --target-port 8000 \
  --ingress external \
  --cpu 2 --memory 4Gi \
  --env-vars \
    "ENVIRONMENT=production" \
    "DATABASE_URL=secretref:database-url" \
    "GROQ_API_KEY=secretref:groq-api-key"

# Deploy frontend
az containerapp create \
  --name assessment-frontend \
  --resource-group teamai-prod \
  --environment teamai-env \
  --image teamairegistry.azurecr.io/assessment-frontend:latest \
  --target-port 3000 \
  --ingress external \
  --cpu 1 --memory 2Gi \
  --env-vars \
    "VITE_API_BASE_URL=https://assessment-backend.grayisland-ba13f170.eastus.azurecontainerapps.io/api"
```

#### Step 4: Verify Deployment
```bash
# Get URLs
az containerapp show --name assessment-backend --resource-group teamai-prod --query properties.configuration.ingress.fqdn
az containerapp show --name assessment-frontend --resource-group teamai-prod --query properties.configuration.ingress.fqdn

# Test backend
curl https://assessment-backend.<region>.azurecontainerapps.io/health

# Test frontend
# Open browser to https://assessment-frontend.<region>.azurecontainerapps.io
```

---

### Option 3: Manual Deployment (VPS/EC2)
**Time**: 45 minutes  
**Cost**: ~$20/month

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3.12 python3-pip nodejs npm nginx

# Clone repo
git clone <repo-url>
cd assessment-tool

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &

# Setup frontend
cd ../frontend-v1
npm install
npm run build

# Configure Nginx
sudo cp infrastructure/nginx/assessment.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/assessment.conf /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

---

## Environment Configuration

### Backend (.env)
```bash
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@host:5432/assessment_db

# Security
SECRET_KEY=<generate-secure-key-here>

# AI
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL_PRIMARY=llama-3.1-8b-instant

# CORS
CORS_ORIGINS=https://assessment.yashusdm.com

# External APIs
MCA_API_KEY=<your-mca-api-key>
GST_API_KEY=<your-gst-api-key>
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=https://api.assessment.yashusdm.com/api
VITE_CONFIG_URL=https://api.assessment.yashusdm.com/config
VITE_ENVIRONMENT=production
VITE_ENABLE_ANALYTICS=true
```

---

## Database Setup

### SQLite (Development)
```bash
cd backend
source venv/bin/activate
python -c "from database import init_db; init_db()"
```

### PostgreSQL (Production)
```bash
# Create database
psql -U postgres
CREATE DATABASE assessment_db;
CREATE USER assessment_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE assessment_db TO assessment_user;

# Run migrations
cd backend
alembic upgrade head
```

---

## Secrets Management

### Azure Key Vault
```bash
# Store secrets
az keyvault secret set --vault-name teamai-vault --name "DATABASE-URL" --value "postgresql://..."
az keyvault secret set --vault-name teamai-vault --name "GROQ-API-KEY" --value "gsk_..."
az keyvault secret set --vault-name teamai-vault --name "JWT-SECRET-KEY" --value "..."

# Reference in Container Apps
az containerapp update \
  --name assessment-backend \
  --resource-group teamai-prod \
  --set-env-vars "DATABASE_URL=secretref:database-url"
```

---

## Monitoring & Logging

### Azure Monitor
```bash
# Enable Application Insights
az containerapp logs show \
  --name assessment-backend \
  --resource-group teamai-prod \
  --type console \
  --tail 100
```

### Manual Logging
```bash
# Backend logs
cd backend
tail -f logs/assessment.log

# Frontend logs (browser console)
# Open DevTools → Console
```

---

## Health Checks

### Backend
```bash
curl https://assessment-backend.../health
# Expected: {"status": "healthy", "service": "assessment-backend"}
```

### Frontend
```bash
curl -I https://assessment-frontend.../
# Expected: HTTP 200 OK
```

### Database
```bash
# SQLite
sqlite3 backend/assessment.db "SELECT COUNT(*) FROM assessments;"

# PostgreSQL
psql -U assessment_user -d assessment_db -c "SELECT COUNT(*) FROM assessments;"
```

---

## Scaling Configuration

### Auto-scaling Rules (Azure Container Apps)
```bash
az containerapp update \
  --name assessment-backend \
  --resource-group teamai-prod \
  --min-replicas 1 \
  --max-replicas 10 \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 50
```

---

## CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy-assessment.yml
name: Deploy Assessment Tool

on:
  push:
    branches: [main]
    paths:
      - 'assessment-tool/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Build and push backend
        run: |
          cd assessment-tool
          docker build -f infrastructure/docker/Dockerfile.backend -t backend:${{ github.sha }} .
          docker tag backend:${{ github.sha }} teamairegistry.azurecr.io/assessment-backend:latest
          docker push teamairegistry.azurecr.io/assessment-backend:latest
      
      - name: Deploy to Container Apps
        run: |
          az containerapp update \
            --name assessment-backend \
            --resource-group teamai-prod \
            --image teamairegistry.azurecr.io/assessment-backend:latest
```

---

## Troubleshooting

### Backend not starting
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database connection failed → Check DATABASE_URL
# 2. Config files missing → Check config/ directory exists
# 3. Port 8000 already in use → Kill process: lsof -ti:8000 | xargs kill
```

### Frontend not loading
```bash
# Check logs
docker-compose logs frontend

# Common issues:
# 1. API_BASE_URL incorrect → Check .env file
# 2. npm dependencies missing → Run: npm install
# 3. Build failed → Check: npm run build
```

### CORS errors
```bash
# Verify CORS_ORIGINS in backend .env
# Should include frontend URL
CORS_ORIGINS=http://localhost:3000,https://assessment.yashusdm.com
```

---

## Backup Strategy

### Database Backup
```bash
# SQLite
cp backend/assessment.db backend/assessment.db.backup

# PostgreSQL
pg_dump -U assessment_user assessment_db > backup_$(date +%Y%m%d).sql
```

### Automated Backups (Azure)
```bash
az postgres server backup create \
  --resource-group teamai-prod \
  --server-name assessment-db \
  --backup-name backup-$(date +%Y%m%d)
```

---

## Cost Optimization

1. **Use SQLite for MVP** (saves $30/month on PostgreSQL)
2. **Skip Redis initially** (saves $15/month)
3. **Use consumption-based Functions** for agent runtime
4. **Groq API instead of OpenAI** (10X cheaper)

**Optimized MVP Cost**: ~$45/month (Backend + Frontend Container Apps)

---

## Performance Tuning

### Backend
```python
# Enable response compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
FastAPICache.init(RedisBackend(redis), prefix="assessment-cache")
```

### Frontend
```javascript
// Enable lazy loading
const Chapter2 = React.lazy(() => import('./chapters/Chapter2'));

// Add service worker for caching
// See: vite-plugin-pwa
```

---

## Security Checklist

- [ ] All secrets in Azure Key Vault (not .env files)
- [ ] HTTPS enabled (Azure handles automatically)
- [ ] CORS restricted to specific origins
- [ ] API rate limiting enabled
- [ ] Input validation with Pydantic
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] Authentication middleware (for admin)
- [ ] Regular security updates (`pip-audit`, `npm audit`)

---

## Post-Deployment Verification

```bash
# 1. Backend health
curl https://assessment-backend.../health

# 2. Config endpoints
curl https://assessment-backend.../config/chapters
curl https://assessment-backend.../config/ui

# 3. API functionality
curl -X POST https://assessment-backend.../api/v1/assessment/init \
  -H "Content-Type: application/json" \
  -d '{"industry": "restaurant"}'

# 4. Frontend loads
curl -I https://assessment-frontend.../

# 5. End-to-end test
# Open frontend URL in browser
# Search "Noya Foods" → Verify 3 candidates appear
```

---

**Deployment Status**: ✅ Ready for deployment  
**Estimated Deployment Time**: 30 minutes (Azure Container Apps)  
**Estimated Monthly Cost**: $115 (full stack) or $45 (MVP optimized)
