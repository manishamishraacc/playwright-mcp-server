# Azure App Service Deployment Script for Playwright MCP Server (PowerShell)

param(
    [string]$ResourceGroup = "playwright-mcp-rg",
    [string]$AppName = "playwright-mcp-server",
    [string]$Location = "eastus",
    [string]$Sku = "B1",
    [string]$Runtime = "PYTHON:3.9"
)

Write-Host "🚀 Starting Azure App Service deployment..." -ForegroundColor Green

# Check if Azure CLI is installed
try {
    $null = Get-Command az -ErrorAction Stop
} catch {
    Write-Host "❌ Azure CLI is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Check if logged in to Azure
try {
    $null = az account show 2>$null
} catch {
    Write-Host "🔐 Please log in to Azure..." -ForegroundColor Yellow
    az login
}

Write-Host "📋 Creating resource group: $ResourceGroup" -ForegroundColor Green
az group create --name $ResourceGroup --location $Location

Write-Host "🏗️ Creating App Service plan..." -ForegroundColor Green
az appservice plan create `
    --name "${AppName}-plan" `
    --resource-group $ResourceGroup `
    --sku $Sku `
    --is-linux

Write-Host "🌐 Creating web app..." -ForegroundColor Green
az webapp create `
    --name $AppName `
    --resource-group $ResourceGroup `
    --plan "${AppName}-plan" `
    --runtime $Runtime `
    --deployment-local-git

Write-Host "⚙️ Configuring app settings..." -ForegroundColor Green
az webapp config appsettings set `
    --resource-group $ResourceGroup `
    --name $AppName `
    --settings `
    WEBSITES_PORT=8000 `
    SCM_DO_BUILD_DURING_DEPLOYMENT=true `
    ENABLE_ORYX_BUILD=true

Write-Host "🔧 Configuring startup command..." -ForegroundColor Green
az webapp config set `
    --resource-group $ResourceGroup `
    --name $AppName `
    --startup-file "uvicorn main:app --host 0.0.0.0 --port 8000"

Write-Host "📦 Deploying application..." -ForegroundColor Green
# Get the deployment URL
$DeploymentUrl = az webapp deployment source config-local-git --name $AppName --resource-group $ResourceGroup --query url --output tsv

Write-Host "🔗 Deployment URL: $DeploymentUrl" -ForegroundColor Cyan

# Add Azure remote if not exists
try {
    $null = git remote get-url azure 2>$null
} catch {
    git remote add azure $DeploymentUrl
}

# Deploy to Azure
Write-Host "🚀 Pushing to Azure..." -ForegroundColor Green
git push azure master

Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host "🌐 Your app is available at: https://$AppName.azurewebsites.net" -ForegroundColor Cyan
Write-Host "📚 API Documentation: https://$AppName.azurewebsites.net/docs" -ForegroundColor Cyan
Write-Host "🔍 Health Check: https://$AppName.azurewebsites.net/health" -ForegroundColor Cyan
Write-Host "🛠️ Tools API: https://$AppName.azurewebsites.net/api/v1/tools" -ForegroundColor Cyan

Write-Host ""
Write-Host "📋 Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs: az webapp log tail --name $AppName --resource-group $ResourceGroup" -ForegroundColor White
Write-Host "  Restart app: az webapp restart --name $AppName --resource-group $ResourceGroup" -ForegroundColor White
Write-Host "  Delete resources: az group delete --name $ResourceGroup --yes" -ForegroundColor White 