#!/bin/bash
set -e

# TeamAI Azure Infrastructure Setup Script
# This script creates all required Azure resources for production deployment

echo "🚀 TeamAI Azure Infrastructure Setup"
echo "===================================="
echo ""

# Configuration Variables
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-teamai-prod}"
LOCATION="${AZURE_LOCATION:-eastus}"
ACR_NAME="${AZURE_ACR_NAME:-teamairegistry}"
KEYVAULT_NAME="${AZURE_KEYVAULT_NAME:-teamai-vault}"
DB_SERVER_NAME="${AZURE_DB_SERVER:-teamai-db}"
DB_ADMIN_USER="${AZURE_DB_ADMIN_USER:-adminuser}"
DB_ADMIN_PASSWORD="${AZURE_DB_PASSWORD:-SecureP@ssw0rd123!}"
REDIS_NAME="${AZURE_REDIS_NAME:-teamai-redis}"

echo "📋 Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Container Registry: $ACR_NAME"
echo "  Key Vault: $KEYVAULT_NAME"
echo "  PostgreSQL Server: $DB_SERVER_NAME"
echo "  Redis Cache: $REDIS_NAME"
echo ""

read -p "Continue with these settings? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Setup cancelled"
    exit 1
fi

# Check if logged in to Azure
echo "🔐 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run:"
    echo "   az login --use-device-code"
    exit 1
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
echo "✅ Logged in to subscription: $SUBSCRIPTION_NAME ($SUBSCRIPTION_ID)"
echo ""

# Step 1: Create Resource Group
echo "📦 Step 1/5: Creating resource group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output table
echo "✅ Resource group created"
echo ""

# Step 2: Create Container Registry
echo "🐳 Step 2/5: Creating Azure Container Registry (3-5 mins)..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true \
    --output table
echo "✅ Container Registry created"
echo ""

# Step 3: Create Key Vault
echo "🔐 Step 3/5: Creating Azure Key Vault..."
az keyvault create \
    --resource-group $RESOURCE_GROUP \
    --name $KEYVAULT_NAME \
    --location $LOCATION \
    --enable-rbac-authorization false \
    --output table
echo "✅ Key Vault created"
echo ""

# Step 4: Create PostgreSQL Flexible Server
echo "🗄️  Step 4/5: Creating PostgreSQL Flexible Server (5-8 mins)..."
az postgres flexible-server create \
    --resource-group $RESOURCE_GROUP \
    --name $DB_SERVER_NAME \
    --location $LOCATION \
    --admin-user $DB_ADMIN_USER \
    --admin-password "$DB_ADMIN_PASSWORD" \
    --sku-name Standard_B2s \
    --tier Burstable \
    --storage-size 32 \
    --version 15 \
    --public-access All \
    --output table

# Create database
echo "Creating teamai database..."
az postgres flexible-server db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $DB_SERVER_NAME \
    --database-name teamai \
    --output table
echo "✅ PostgreSQL server created"
echo ""

# Step 5: Create Redis Cache
echo "⚡ Step 5/5: Creating Azure Cache for Redis (3-5 mins)..."
az redis create \
    --resource-group $RESOURCE_GROUP \
    --name $REDIS_NAME \
    --location $LOCATION \
    --sku Basic \
    --vm-size c0 \
    --enable-non-ssl-port true \
    --output table
echo "✅ Redis cache created"
echo ""

# Fetch connection strings
echo "📝 Fetching connection strings..."
DB_HOST=$(az postgres flexible-server show \
    --resource-group $RESOURCE_GROUP \
    --name $DB_SERVER_NAME \
    --query fullyQualifiedDomainName -o tsv)

REDIS_HOST=$(az redis show \
    --resource-group $RESOURCE_GROUP \
    --name $REDIS_NAME \
    --query hostName -o tsv)

REDIS_KEY=$(az redis list-keys \
    --resource-group $RESOURCE_GROUP \
    --name $REDIS_NAME \
    --query primaryKey -o tsv)

ACR_LOGIN_SERVER=$(az acr show \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --query loginServer -o tsv)

ACR_USERNAME=$(az acr credential show \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --query username -o tsv)

ACR_PASSWORD=$(az acr credential show \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --query passwords[0].value -o tsv)

# Build connection strings
DATABASE_URL="postgresql://$DB_ADMIN_USER:$DB_ADMIN_PASSWORD@$DB_HOST/teamai?sslmode=require"
REDIS_URL="redis://:$REDIS_KEY@$REDIS_HOST:6380"

echo ""
echo "✅ All infrastructure created successfully!"
echo ""
echo "📋 Save these values for deployment:"
echo "=================================="
echo ""
echo "Azure Container Registry:"
echo "  ACR_LOGIN_SERVER=$ACR_LOGIN_SERVER"
echo "  ACR_USERNAME=$ACR_USERNAME"
echo "  ACR_PASSWORD=$ACR_PASSWORD"
echo ""
echo "Database:"
echo "  DATABASE_URL=$DATABASE_URL"
echo ""
echo "Redis:"
echo "  REDIS_URL=$REDIS_URL"
echo ""
echo "Key Vault:"
echo "  KEYVAULT_NAME=$KEYVAULT_NAME"
echo ""
echo "=================================="
echo ""
echo "🔐 Storing secrets in Key Vault..."

# Store secrets in Key Vault
az keyvault secret set --vault-name $KEYVAULT_NAME --name "DATABASE-URL" --value "$DATABASE_URL" > /dev/null
az keyvault secret set --vault-name $KEYVAULT_NAME --name "REDIS-URL" --value "$REDIS_URL" > /dev/null
az keyvault secret set --vault-name $KEYVAULT_NAME --name "JWT-SECRET-KEY" --value "$(openssl rand -hex 32)" > /dev/null

echo "✅ Infrastructure secrets stored in Key Vault"
echo ""
echo "⚠️  MANUAL STEPS REQUIRED:"
echo "1. Store your Google OAuth credentials in Key Vault:"
echo "   az keyvault secret set --vault-name $KEYVAULT_NAME --name 'GOOGLE-CLIENT-ID' --value 'YOUR_CLIENT_ID'"
echo "   az keyvault secret set --vault-name $KEYVAULT_NAME --name 'GOOGLE-CLIENT-SECRET' --value 'YOUR_CLIENT_SECRET'"
echo ""
echo "2. Run './scripts/azure-deploy.sh' to build and deploy containers"
echo ""
echo "💰 Estimated monthly cost: ~$143"
