# Docker-First Development Guide

## Quick Start
```bash
# 1. Start all services
make up

# 2. View logs (live tail)
make logs

# 3. Access services
# Backend:  http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

## Architecture Benefits

### 1. Development = Production
- **Same Dockerfile** used in dev, CI/CD, and Azure Container Apps
- **Same network topology** (backend → postgres, backend → redis)
- **Same environment variables** (DATABASE_URL format)
- Eliminates "works on my machine" issues

### 2. Hot Reload Enabled
```yaml
# Backend: Code mounted as volume
volumes:
  - ./backend:/app/backend:rw

# Frontend: Code mounted, node_modules cached
volumes:
  - ./frontend:/app:rw
  - /app/node_modules  # Use container's version
```

**Result**: Edit code → see changes instantly (no restart needed)

### 3. One Command Setup
```bash
git clone <repo>
cd TeamAI
make up
# Done! Backend + Frontend + DB + Redis all running
```

## Common Commands

### Development
```bash
make up              # Start all services
make down            # Stop all services
make restart         # Restart services
make ps              # Show running containers
make logs            # View all logs
make logs-backend    # View backend logs only
make logs-frontend   # View frontend logs only
```

### Database
```bash
make migrate         # Run pending migrations
make migrate-make msg="add users table"  # Create new migration
make db-shell        # Open PostgreSQL prompt
make db-reset        # ⚠️  Delete all data and re-migrate
```

### Shell Access
```bash
make shell-backend   # Bash in backend container
make shell-frontend  # Sh in frontend container (Alpine)

# Examples:
make shell-backend
> cd /app/backend && python
> from app.models import User
> User.__tablename__

make db-shell
> \dt  -- List tables
> SELECT * FROM users;
```

### Testing
```bash
make test            # Run all tests
make test-backend    # pytest in backend container
make test-frontend   # npm test in frontend container
```

### Code Quality
```bash
make format          # black + prettier
make lint            # pylint + eslint
```

### Cleanup
```bash
make clean           # Remove containers + volumes + cache
make build           # Rebuild images from scratch
```

## Docker Compose Structure

```yaml
services:
  postgres:
    image: postgres:15-alpine
    healthcheck: pg_isready
    # Data persisted in volume: teamai_postgres_data

  redis:
    image: redis:7-alpine
    healthcheck: redis-cli ping
    # Data persisted in volume: teamai_redis_data

  backend:
    build:
      target: development  # Use dev stage with hot reload
    volumes:
      - ./backend:/app/backend  # Mount code
    depends_on:
      - postgres
      - redis
    command: uvicorn --reload  # Auto-reload on changes

  frontend:
    build:
      target: development
    volumes:
      - ./frontend:/app
      - /app/node_modules  # Cached in container
    command: npm run dev -- --host 0.0.0.0
```

## Multi-Stage Dockerfile Pattern

### Backend (`infrastructure/docker/Dockerfile.backend`)
```dockerfile
# Development stage - hot reload
FROM python:3.11-slim AS development
RUN pip install fastapi uvicorn[standard] ...
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--reload"]

# Production stage - optimized
FROM python:3.11-slim AS production
RUN pip install --no-cache-dir ...
USER appuser  # Non-root
CMD ["uvicorn", "app.main:app", "--workers", "4"]
```

### Frontend (`infrastructure/docker/Dockerfile.frontend`)
```dockerfile
# Development stage - vite dev server
FROM node:18-alpine AS development
RUN npm install
CMD ["npm", "run", "dev"]

# Build stage - compile TypeScript
FROM node:18-alpine AS build
RUN npm ci --only=production
RUN npm run build

# Production stage - nginx static server
FROM nginx:alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]
```

## Troubleshooting

### Backend won't start
```bash
# Check logs
make logs-backend

# Common issues:
# 1. Database not ready → Wait 15s for healthcheck
# 2. Migration error → Check alembic output in logs
# 3. Import error → Make shell-backend and test imports
```

### Frontend build fails
```bash
# Rebuild node_modules
docker-compose down
docker-compose build --no-cache frontend
make up
```

### Database connection refused
```bash
# Check postgres health
make ps

# Should show:
# teamai-postgres   Up XX seconds (healthy)

# If unhealthy, check logs:
docker-compose logs postgres
```

### Port already in use
```bash
# Check what's using the port
lsof -i :8000  # or :3000, :5432

# Stop conflicting service or change port in docker-compose.yml
```

## CI/CD Integration

### GitHub Actions (planned)
```yaml
# .github/workflows/test.yml
- name: Build images
  run: docker-compose build

- name: Start services
  run: docker-compose up -d

- name: Run tests
  run: |
    docker-compose exec -T backend pytest
    docker-compose exec -T frontend npm test
```

### Azure Container Apps (planned)
```bash
# Same Dockerfile, production target
docker build --target production -f infrastructure/docker/Dockerfile.backend .
az containerapp create --image <registry>/teamai-backend:latest
```

## Development Workflow

### Day-to-day
```bash
# Morning
make up && make logs

# Code in VSCode
# - Edit backend/app/main.py → see changes at http://localhost:8000
# - Edit frontend/src/App.tsx → browser refreshes

# Need database changes?
make shell-backend
> cd /app/backend && alembic revision --autogenerate -m "add field"
exit
make migrate

# End of day
make down
```

### New developer onboarding
```bash
git clone <repo>
cd TeamAI
cp .env.example .env  # Edit if needed
make up
# ✅ Ready to code in 2 minutes
```

## Comparison: Before vs After

### Before (❌ Manual setup)
```bash
# Backend
cd backend
poetry install
poetry shell
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev

# Database (separate terminal)
docker run postgres...
# Configure connection string manually
```

### After (✅ Docker-first)
```bash
make up
# All services running, all connections configured
```

## Next Steps

With Docker infrastructure ready, now building:
- **Phase 1b**: Auth backend (JWT, password hashing) in containers
- **Phase 1c**: Login/Registration UI with hot reload
- **Phase 1d**: Protected dashboard
- All development happens inside containers
- Production deploy = same images, no surprises
