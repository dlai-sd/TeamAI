.PHONY: help install up down logs shell-backend shell-frontend test migrate clean format

# Default target
help:
	@echo "TeamAI Docker-First Development Commands"
	@echo "========================================="
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make up            - Start all services (PostgreSQL, Redis, Backend, Frontend)"
	@echo "  make logs          - View logs from all services"
	@echo "  make down          - Stop all services"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make shell-backend - Open bash shell in backend container"
	@echo "  make shell-frontend- Open shell in frontend container"
	@echo "  make test          - Run all tests in containers"
	@echo "  make test-backend  - Run backend tests only"
	@echo "  make test-frontend - Run frontend tests only"
	@echo ""
	@echo "🗄️  Database:"
	@echo "  make migrate       - Run Alembic migrations"
	@echo "  make migrate-make  - Create new migration (msg='description')"
	@echo "  make db-shell      - Open PostgreSQL shell"
	@echo "  make db-reset      - Reset database (WARNING: deletes all data)"
	@echo ""
	@echo "🐳 Docker Management:"
	@echo "  make build         - Rebuild Docker images"
	@echo "  make restart       - Restart all services"
	@echo "  make clean         - Remove containers, volumes, and build artifacts"
	@echo ""
	@echo "🎨 Code Quality:"
	@echo "  make format        - Format code (black + prettier)"
	@echo "  make lint          - Run linters (pylint + eslint)"
	@echo ""
	@echo "📊 Monitoring:"
	@echo "  make ps            - Show running containers"
	@echo "  make logs-backend  - View backend logs"
	@echo "  make logs-frontend - View frontend logs"

# Docker Compose Commands
up:
	docker-compose up -d
	@echo "✅ Services started. Access:"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   Docs:     http://localhost:8000/docs"

down:
	docker-compose down

restart:
	docker-compose restart

ps:
	docker-compose ps

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

# Shell Access
shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh

db-shell:
	docker-compose exec postgres psql -U teamai -d teamai

# Testing
test:
	docker-compose exec backend pytest -v
	docker-compose exec frontend npm test

test-backend:
	docker-compose exec backend pytest -v --cov=app

test-frontend:
	docker-compose exec frontend npm test

# Database Management
migrate:
	docker-compose exec backend sh -c "cd /app/backend && alembic upgrade head"

migrate-make:
	docker-compose exec backend sh -c "cd /app/backend && alembic revision --autogenerate -m '$(msg)'"

db-reset:
	@echo "⚠️  WARNING: This will delete ALL data. Continue? [y/N]" && read ans && [ $${ans:-N} = y ]
	docker-compose down -v
	docker-compose up -d postgres
	sleep 5
	docker-compose exec backend sh -c "cd /app/backend && alembic upgrade head"

# Build & Clean
build:
	docker-compose build --no-cache

clean:
	docker-compose down -v
	docker system prune -f
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true

# Code Quality
format:
	docker-compose exec backend black /app/backend
	docker-compose exec frontend npm run format

lint:
	docker-compose exec backend pylint app/
	docker-compose exec frontend npm run lint

# Health Checks
health:
	@echo "🏥 Health Check:"
	@curl -s http://localhost:8000/health || echo "❌ Backend unhealthy"
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend healthy" || echo "❌ Frontend unhealthy"

# Install (for CI/CD or local fallback)
install:
	@echo "⚠️  Using Docker-first workflow. Run 'make up' instead."
	@echo "   For local development without Docker:"
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	@echo "✓ Services started. Backend: http://localhost:8000, Frontend: http://localhost:3000"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-rebuild:
	docker-compose up -d --build

# Database
migrate:
	cd backend && poetry run alembic upgrade head

migrate-create:
	@read -p "Enter migration name: " name; \
	cd backend && poetry run alembic revision --autogenerate -m "$$name"

migrate-rollback:
	cd backend && poetry run alembic downgrade -1

# Code quality
format:
	@echo "Formatting Python code..."
	cd backend && poetry run black .
	@echo "Formatting TypeScript code..."
	cd frontend && npm run lint --fix
	@echo "✓ Code formatted"

lint:
	cd backend && poetry run pylint app/
	cd frontend && npm run lint

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleanup complete"

# Development helpers
dev:
	@echo "Starting full stack in development mode..."
	make docker-up
	@sleep 5
	make migrate
	@echo "✓ Development environment ready"
	@echo "  - Backend: http://localhost:8000"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - API Docs: http://localhost:8000/docs"
