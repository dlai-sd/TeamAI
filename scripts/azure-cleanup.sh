#!/bin/bash
set -e

# TeamAI Azure Cleanup Script
# This script deletes all Azure resources to avoid charges

echo "⚠️  TeamAI Azure Cleanup"
echo "======================="
echo ""
echo "This will DELETE all Azure resources for TeamAI."
echo "This action CANNOT be undone!"
echo ""

RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-teamai-prod}"

echo "Resource Group: $RESOURCE_GROUP"
echo ""

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run:"
    echo "   az login --use-device-code"
    exit 1
fi

# Show resources that will be deleted
echo "📋 Resources that will be deleted:"
az resource list --resource-group $RESOURCE_GROUP --output table

echo ""
read -p "Are you ABSOLUTELY SURE you want to delete everything? Type 'DELETE' to confirm: " -r
echo ""

if [ "$REPLY" != "DELETE" ]; then
    echo "❌ Cleanup cancelled"
    exit 1
fi

echo "🗑️  Deleting resource group and all resources..."
az group delete \
    --name $RESOURCE_GROUP \
    --yes \
    --no-wait

echo ""
echo "✅ Deletion initiated (will complete in background)"
echo ""
echo "To check status:"
echo "  az group show --name $RESOURCE_GROUP"
echo ""
echo "When fully deleted, you'll see: ResourceNotFound error"
echo ""
