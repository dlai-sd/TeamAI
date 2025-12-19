#!/bin/bash
# Production deployment script for Azure
# Builds and deploys both backend and frontend

set -e

echo "🚀 Deploying Assessment Tool to Azure..."

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Configuration
RESOURCE_GROUP="teamai-prod"
ACR_NAME="teamairegistry"
BACKEND_APP="assessment-backend"
FRONTEND_APP="assessment-frontend"

# Login check
echo "Checking Azure login..."
if ! az account show &> /dev/null; then
    echo "Please login to Azure:"
    az login
fi

# Build Docker images
echo ""
echo "🔨 Building Docker images..."

echo "Building backend..."
docker build -f infrastructure/docker/Dockerfile.backend -t assessment-backend:latest .

echo "Building frontend..."
docker build -f infrastructure/docker/Dockerfile.frontend -t assessment-frontend:latest .

# Login to ACR
echo ""
echo "🔐 Logging in to Azure Container Registry..."
az acr login --name $ACR_NAME

# Tag images
echo ""
echo "🏷️  Tagging images..."
docker tag assessment-backend:latest $ACR_NAME.azurecr.io/assessment-backend:latest
docker tag assessment-frontend:latest $ACR_NAME.azurecr.io/assessment-frontend:latest

# Push images
echo ""
echo "📤 Pushing images to registry..."
docker push $ACR_NAME.azurecr.io/assessment-backend:latest
docker push $ACR_NAME.azurecr.io/assessment-frontend:latest

# Deploy backend
echo ""
echo "🚀 Deploying backend to Container Apps..."
az containerapp update \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --image $ACR_NAME.azurecr.io/assessment-backend:latest

# Get backend URL
BACKEND_URL=$(az containerapp show \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

# Deploy frontend
echo ""
echo "🚀 Deploying frontend to Container Apps..."
az containerapp update \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --image $ACR_NAME.azurecr.io/assessment-frontend:latest \
  --set-env-vars "VITE_API_BASE_URL=https://$BACKEND_URL/api"

# Get frontend URL
FRONTEND_URL=$(az containerapp show \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

# Summary
echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 URLs:"
echo "   Frontend: https://$FRONTEND_URL"
echo "   Backend:  https://$BACKEND_URL"
echo "   API Docs: https://$BACKEND_URL/docs"
echo ""
echo "🧪 Test:"
echo "   curl https://$BACKEND_URL/health"
echo ""
