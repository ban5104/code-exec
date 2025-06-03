#!/bin/bash
# Deployment script for Azure App Service

echo "Claude Code Execution Teams Bot - Deployment Script"
echo "=================================================="

# Check required environment variables
if [ -z "$RESOURCE_GROUP" ] || [ -z "$APP_NAME" ]; then
    echo "Error: RESOURCE_GROUP and APP_NAME environment variables must be set"
    echo "Usage: RESOURCE_GROUP=mygroup APP_NAME=myapp ./deploy.sh"
    exit 1
fi

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check command success
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1 failed${NC}"
        exit 1
    fi
}

echo "Deploying to:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  App Name: $APP_NAME"
echo ""

# Step 1: Run tests
echo "Step 1: Running tests..."
python run_tests.py
check_status "Tests"

# Step 2: Create deployment package
echo -e "\nStep 2: Creating deployment package..."
rm -f deployment.zip
zip -r deployment.zip . \
    -x "*.git*" \
    -x "*node_modules*" \
    -x "*venv*" \
    -x "*__pycache__*" \
    -x "*.pyc" \
    -x "*test*" \
    -x "*demos/screenshots/*" \
    -x "deployment.zip" \
    -x ".env"
check_status "Package creation"

# Step 3: Deploy to Azure
echo -e "\nStep 3: Deploying to Azure..."
az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --src deployment.zip
check_status "Deployment"

# Step 4: Configure app settings
echo -e "\nStep 4: Configuring app settings..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    PYTHON_VERSION="3.9" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    WEBSITE_NODE_DEFAULT_VERSION="16.x"
check_status "App settings"

# Step 5: Restart the app
echo -e "\nStep 5: Restarting app..."
az webapp restart \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME
check_status "App restart"

# Step 6: Check deployment
echo -e "\nStep 6: Checking deployment..."
HEALTH_URL="https://$APP_NAME.azurewebsites.net/health"
echo "Checking health endpoint: $HEALTH_URL"

sleep 10  # Wait for app to start

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)
if [ "$HTTP_STATUS" -eq 200 ]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo -e "\n${GREEN}Deployment successful!${NC}"
    echo -e "Bot endpoint: https://$APP_NAME.azurewebsites.net/api/messages"
else
    echo -e "${RED}✗ Health check failed (HTTP $HTTP_STATUS)${NC}"
    echo "Checking logs..."
    az webapp log tail \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME \
        --provider http
fi

# Cleanup
rm -f deployment.zip
echo -e "\nDeployment complete!"