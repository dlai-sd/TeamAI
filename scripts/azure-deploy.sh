#!/bin/bash
set -e

# TeamAI Azure Deployment Script
# This script builds Docker images and deploys to Azure Container Apps

echo "🚀 TeamAI Azure Deployment"
echo "=========================="
echo ""

# Configuration Variables
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-teamai-prod}"
LOCATION="${AZURE_LOCATION:-eastus}"
ACR_NAME="${AZURE_ACR_NAME:-teamairegistry}"
KEYVAULT_NAME="${AZURE_KEYVAULT_NAME:-teamai-vault}"
CONTAINER_ENV="${AZURE_CONTAINER_ENV:-teamai-env}"

echo "📋 Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Container Registry: $ACR_NAME"
echo "  Key Vault: $KEYVAULT_NAME"
echo ""

# Check if logged in to Azure
echo "🔐 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run:"
    echo "   az login --use-device-code"
    exit 1
fi

echo "✅ Logged in to Azure"
echo ""

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --query loginServer -o tsv)

echo "🐳 ACR Login Server: $ACR_LOGIN_SERVER"
echo ""

# Step 1: Login to ACR
echo "🔐 Step 1/5: Logging into Azure Container Registry..."
az acr login --name $ACR_NAME
echo "✅ Logged into ACR"
echo ""

# Step 2: Build and push backend image
echo "🏗️  Step 2/5: Building backend Docker image..."
docker build \
    -f infrastructure/docker/Dockerfile.backend \
    -t $ACR_LOGIN_SERVER/backend:latest \
    -t $ACR_LOGIN_SERVER/backend:$(date +%Y%m%d-%H%M%S) \
    .

echo "📤 Pushing backend image to ACR..."
docker push $ACR_LOGIN_SERVER/backend:latest
echo "✅ Backend image pushed"
echo ""

# Step 3: Build and push frontend image
echo "🏗️  Step 3/5: Building frontend Docker image..."
docker build \
    -f infrastructure/docker/Dockerfile.frontend \
    -t $ACR_LOGIN_SERVER/frontend:latest \
    -t $ACR_LOGIN_SERVER/frontend:$(date +%Y%m%d-%H%M%S) \
    .

echo "📤 Pushing frontend image to ACR..."
docker push $ACR_LOGIN_SERVER/frontend:latest
echo "✅ Frontend image pushed"
echo ""

# Step 4: Create Container Apps Environment (if not exists)
echo "🌍 Step 4/5: Setting up Container Apps Environment..."
if ! az containerapp env show --name $CONTAINER_ENV --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating Container Apps environment (5 mins)..."
    az containerapp env create \
        --name $CONTAINER_ENV \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --output table
    echo "✅ Environment created"
else
    echo "✅ Environment already exists"
fi
echo ""

# Get ACR credentials
ACR_USERNAME=$(az acr credential show \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --query username -o tsv)

ACR_PASSWORD=$(az acr credential show \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --query passwords[0].value -o tsv)

# Fetch secrets from Key Vault
echo "🔐 Fetching secrets from Key Vault..."
DATABASE_URL=$(az keyvault secret show --vault-name $KEYVAULT_NAME --name DATABASE-URL --query value -o tsv)
REDIS_URL=$(az keyvault secret show --vault-name $KEYVAULT_NAME --name REDIS-URL --query value -o tsv)
JWT_SECRET_KEY=$(az keyvault secret show --vault-name $KEYVAULT_NAME --name JWT-SECRET-KEY --query value -o tsv)
GOOGLE_CLIENT_ID=$(az keyvault secret show --vault-name $KEYVAULT_NAME --name GOOGLE-CLIENT-ID --query value -o tsv 2>/dev/null || echo "")
GOOGLE_CLIENT_SECRET=$(az keyvault secret show --vault-name $KEYVAULT_NAME --name GOOGLE-CLIENT-SECRET --query value -o tsv 2>/dev/null || echo "")

if [ -z "$GOOGLE_CLIENT_ID" ] || [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    echo "⚠️  WARNING: Google OAuth secrets not found in Key Vault"
    echo "Please store them with:"
    echo "  az keyvault secret set --vault-name $KEYVAULT_NAME --name 'GOOGLE-CLIENT-ID' --value 'YOUR_CLIENT_ID'"
    echo "  az keyvault secret set --vault-name $KEYVAULT_NAME --name 'GOOGLE-CLIENT-SECRET' --value 'YOUR_CLIENT_SECRET'"
fi
echo ""

# Step 5: Deploy Container Apps
echo "🚀 Step 5/5: Deploying Container Apps..."

# Deploy backend
echo "Deploying backend container app (3-5 mins)..."
if az containerapp show --name teamai-backend --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Updating existing backend app..."
    az containerapp update \
        --name teamai-backend \
        --resource-group $RESOURCE_GROUP \
        --image $ACR_LOGIN_SERVER/backend:latest
else
    echo "Creating new backend app..."
    az containerapp create \
        --name teamai-backend \
        --resource-group $RESOURCE_GROUP \
        --environment $CONTAINER_ENV \
        --image $ACR_LOGIN_SERVER/backend:latest \
        --target-port 8000 \
        --ingress external \
        --cpu 2 --memory 4Gi \
        --min-replicas 1 --max-replicas 3 \
        --registry-server $ACR_LOGIN_SERVER \
        --registry-username $ACR_USERNAME \
        --registry-password "$ACR_PASSWORD" \
        --secrets \
            database-url="$DATABASE_URL" \
            redis-url="$REDIS_URL" \
            jwt-secret-key="$JWT_SECRET_KEY" \
            google-client-id="$GOOGLE_CLIENT_ID" \
            google-client-secret="$GOOGLE_CLIENT_SECRET" \
        --env-vars \
            DATABASE_URL=secretref:database-url \
            REDIS_URL=secretref:redis-url \
            JWT_SECRET_KEY=secretref:jwt-secret-key \
            GOOGLE_CLIENT_ID=secretref:google-client-id \
            GOOGLE_CLIENT_SECRET=secretref:google-client-secret \
        --output table
fi
echo "✅ Backend deployed"
echo ""

# Get backend URL
BACKEND_URL=$(az containerapp show \
    --name teamai-backend \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

BACKEND_REDIRECT_URI="https://$BACKEND_URL/api/v1/auth/google/callback"

# Deploy frontend
echo "Deploying frontend container app (3-5 mins)..."
if az containerapp show --name teamai-frontend --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Updating existing frontend app..."
    az containerapp update \
        --name teamai-frontend \
        --resource-group $RESOURCE_GROUP \
        --image $ACR_LOGIN_SERVER/frontend:latest \
        --set-env-vars \
            VITE_API_URL="https://$BACKEND_URL"
else
    echo "Creating new frontend app..."
    az containerapp create \
        --name teamai-frontend \
        --resource-group $RESOURCE_GROUP \
        --environment $CONTAINER_ENV \
        --image $ACR_LOGIN_SERVER/frontend:latest \
        --target-port 3000 \
        --ingress external \
        --cpu 1 --memory 2Gi \
        --min-replicas 1 --max-replicas 2 \
        --registry-server $ACR_LOGIN_SERVER \
        --registry-username $ACR_USERNAME \
        --registry-password "$ACR_PASSWORD" \
        --env-vars \
            VITE_API_URL="https://$BACKEND_URL" \
        --output table
fi
echo "✅ Frontend deployed"
echo ""

# Get frontend URL
FRONTEND_URL=$(az containerapp show \
    --name teamai-frontend \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "🌐 Application URLs:"
echo "  Frontend: https://$FRONTEND_URL"
echo "  Backend:  https://$BACKEND_URL"
echo ""
echo "⚠️  NEXT STEPS:"
echo "1. Update Google OAuth redirect URI in Google Cloud Console:"
echo "   $BACKEND_REDIRECT_URI"
echo ""
echo "2. Update backend GOOGLE_REDIRECT_URI environment variable:"
echo "   az containerapp update \\"
echo "     --name teamai-backend \\"
echo "     --resource-group $RESOURCE_GROUP \\"
echo "     --set-env-vars GOOGLE_REDIRECT_URI='$BACKEND_REDIRECT_URI' \\"
echo "                    FRONTEND_URL='https://$FRONTEND_URL'"
echo ""
echo "3. Run database migrations:"
echo "   az containerapp exec \\"
echo "     --name teamai-backend \\"
echo "     --resource-group $RESOURCE_GROUP \\"
echo "     --command 'alembic upgrade head'"
echo ""
echo "4. Test the application:"
echo "   Open https://$FRONTEND_URL in your browser"
echo ""
