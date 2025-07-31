#!/bin/bash

# Azure App Service Deployment Script for Playwright MCP Server

set -e

# Configuration
RESOURCE_GROUP="playwright-mcp-rg"
APP_NAME="playwright-mcp-server"
LOCATION="eastus"
SKU="B1"
RUNTIME="PYTHON:3.9"

echo "🚀 Starting Azure App Service deployment..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "🔐 Please log in to Azure..."
    az login
fi

echo "📋 Creating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION

echo "🏗️ Creating App Service plan..."
az appservice plan create \
    --name "${APP_NAME}-plan" \
    --resource-group $RESOURCE_GROUP \
    --sku $SKU \
    --is-linux

echo "🌐 Creating web app..."
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan "${APP_NAME}-plan" \
    --runtime $RUNTIME \
    --deployment-local-git

echo "⚙️ Configuring app settings..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    WEBSITES_PORT=8000 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    ENABLE_ORYX_BUILD=true

echo "🔧 Configuring startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "uvicorn main:app --host 0.0.0.0 --port 8000"

echo "📦 Deploying application..."
# Get the deployment URL
DEPLOYMENT_URL=$(az webapp deployment source config-local-git --name $APP_NAME --resource-group $RESOURCE_GROUP --query url --output tsv)

echo "🔗 Deployment URL: $DEPLOYMENT_URL"

# Add Azure remote if not exists
if ! git remote get-url azure &> /dev/null; then
    git remote add azure $DEPLOYMENT_URL
fi

# Deploy to Azure
echo "🚀 Pushing to Azure..."
git push azure master

echo "✅ Deployment completed!"
echo "🌐 Your app is available at: https://$APP_NAME.azurewebsites.net"
echo "📚 API Documentation: https://$APP_NAME.azurewebsites.net/docs"
echo "🔍 Health Check: https://$APP_NAME.azurewebsites.net/health"
echo "🛠️ Tools API: https://$APP_NAME.azurewebsites.net/api/v1/tools"

echo ""
echo "📋 Useful commands:"
echo "  View logs: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo "  Restart app: az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo "  Delete resources: az group delete --name $RESOURCE_GROUP --yes" 