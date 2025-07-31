# Azure App Service Deployment Guide

This guide will help you deploy your Playwright MCP Server to Azure App Service.

## 🚀 Prerequisites

1. **Azure Account**: You need an active Azure subscription
2. **Azure CLI**: Install Azure CLI from [here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
3. **Git**: Ensure Git is installed and configured

## 📋 Deployment Options

### Option 1: Quick Deployment (Recommended)

#### For Windows (PowerShell):
```powershell
# Run the PowerShell deployment script
.\azure-deploy.ps1
```

#### For Linux/Mac (Bash):
```bash
# Make the script executable
chmod +x azure-deploy.sh

# Run the deployment script
./azure-deploy.sh
```

### Option 2: Manual Deployment

#### Step 1: Login to Azure
```bash
az login
```

#### Step 2: Create Resource Group
```bash
az group create --name playwright-mcp-rg --location eastus
```

#### Step 3: Create App Service Plan
```bash
az appservice plan create \
    --name playwright-mcp-server-plan \
    --resource-group playwright-mcp-rg \
    --sku B1 \
    --is-linux
```

#### Step 4: Create Web App
```bash
az webapp create \
    --name playwright-mcp-server \
    --resource-group playwright-mcp-rg \
    --plan playwright-mcp-server-plan \
    --runtime "PYTHON:3.9" \
    --deployment-local-git
```

#### Step 5: Configure App Settings
```bash
az webapp config appsettings set \
    --resource-group playwright-mcp-rg \
    --name playwright-mcp-server \
    --settings \
    WEBSITES_PORT=8000 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    ENABLE_ORYX_BUILD=true
```

#### Step 6: Configure Startup Command
```bash
az webapp config set \
    --resource-group playwright-mcp-rg \
    --name playwright-mcp-server \
    --startup-file "uvicorn main:app --host 0.0.0.0 --port 8000"
```

#### Step 7: Deploy Application
```bash
# Get deployment URL
DEPLOYMENT_URL=$(az webapp deployment source config-local-git --name playwright-mcp-server --resource-group playwright-mcp-rg --query url --output tsv)

# Add Azure remote
git remote add azure $DEPLOYMENT_URL

# Deploy
git push azure master
```

### Option 3: Azure DevOps Pipeline

1. **Create Azure DevOps Project**
2. **Import your repository**
3. **Update the `azure-pipelines.yml` file**:
   - Replace `'Your-Azure-Subscription'` with your actual subscription name
4. **Create the pipeline** using the YAML file
5. **Run the pipeline**

## 🔧 Configuration

### Environment Variables

You can set these in Azure App Service Configuration:

```bash
# Required
WEBSITES_PORT=8000

# Optional
LOG_LEVEL=INFO
ENABLE_PLAYWRIGHT_TOOLS=true
ENABLE_AZURE_DEVOPS_TOOLS=true
```

### Custom Domain (Optional)

```bash
# Add custom domain
az webapp config hostname add \
    --webapp-name playwright-mcp-server \
    --resource-group playwright-mcp-rg \
    --hostname your-domain.com
```

## 🌐 Accessing Your Application

After successful deployment, your application will be available at:

- **Main URL**: `https://playwright-mcp-server.azurewebsites.net`
- **API Documentation**: `https://playwright-mcp-server.azurewebsites.net/docs`
- **Health Check**: `https://playwright-mcp-server.azurewebsites.net/health`
- **Tools API**: `https://playwright-mcp-server.azurewebsites.net/api/v1/tools`

## 📊 Monitoring and Logs

### View Application Logs
```bash
az webapp log tail --name playwright-mcp-server --resource-group playwright-mcp-rg
```

### Download Logs
```bash
az webapp log download --name playwright-mcp-server --resource-group playwright-mcp-rg
```

### Application Insights (Optional)
```bash
# Create Application Insights
az monitor app-insights component create \
    --app playwright-mcp-insights \
    --location eastus \
    --resource-group playwright-mcp-rg \
    --application-type web

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show --app playwright-mcp-insights --resource-group playwright-mcp-rg --query instrumentationKey --output tsv)

# Add to app settings
az webapp config appsettings set \
    --resource-group playwright-mcp-rg \
    --name playwright-mcp-server \
    --settings APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY
```

## 🔄 Continuous Deployment

### GitHub Actions (Alternative to Azure DevOps)

Create `.github/workflows/azure-deploy.yml`:

```yaml
name: Deploy to Azure
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'playwright-mcp-server'
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port Configuration**
   - Ensure `WEBSITES_PORT=8000` is set in app settings
   - Check that the application listens on `0.0.0.0:8000`

2. **Playwright Installation**
   - The startup script automatically installs Playwright browsers
   - Check logs for any installation errors

3. **Memory Issues**
   - Consider upgrading to a higher SKU (B2 or S1) if you encounter memory issues
   - Monitor memory usage in Azure Portal

4. **Startup Timeout**
   - Increase startup timeout in app settings if needed
   - Check that all dependencies are properly installed

### Debug Commands

```bash
# Check app status
az webapp show --name playwright-mcp-server --resource-group playwright-mcp-rg

# Restart app
az webapp restart --name playwright-mcp-server --resource-group playwright-mcp-rg

# Check app settings
az webapp config appsettings list --name playwright-mcp-server --resource-group playwright-mcp-rg
```

## 💰 Cost Optimization

### App Service Plans

- **Free (F1)**: Not recommended for production
- **Basic (B1)**: Good for development/testing (~$13/month)
- **Standard (S1)**: Recommended for production (~$73/month)
- **Premium (P1)**: For high-performance needs (~$146/month)

### Scaling Options

```bash
# Scale up (change plan)
az appservice plan update \
    --name playwright-mcp-server-plan \
    --resource-group playwright-mcp-rg \
    --sku S1

# Scale out (add instances)
az appservice plan update \
    --name playwright-mcp-server-plan \
    --resource-group playwright-mcp-rg \
    --number-of-workers 2
```

## 🧹 Cleanup

To delete all resources when no longer needed:

```bash
az group delete --name playwright-mcp-rg --yes
```

## 📞 Support

If you encounter issues:

1. Check the application logs
2. Review Azure App Service documentation
3. Check the troubleshooting section above
4. Open an issue in the GitHub repository

## 🔗 Useful Links

- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Python on Azure](https://docs.microsoft.com/en-us/azure/developer/python/)
- [Azure CLI Documentation](https://docs.microsoft.com/en-us/cli/azure/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/) 