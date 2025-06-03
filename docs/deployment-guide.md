# Microsoft Teams Bot Deployment Guide

This guide provides step-by-step instructions for deploying the Claude Code Execution Bot to Microsoft Teams using Azure.

## Prerequisites

1. **Azure Account**: An active Azure subscription
2. **Microsoft 365 Account**: Access to Teams with admin privileges
3. **Azure CLI**: Install from [here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
4. **Python 3.8+**: Installed on your development machine
5. **Anthropic API Key**: Get from [Anthropic Console](https://console.anthropic.com/)

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Microsoft      │────▶│   Azure Bot     │────▶│  Azure App      │
│  Teams          │     │   Service       │     │  Service        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │  Claude API     │
                                                 └─────────────────┘
```

## Step 1: Set Up Azure Resources

### 1.1 Create Resource Group

```bash
az login
az group create --name rg-claude-bot --location eastus
```

### 1.2 Create Azure Bot

```bash
# Create App Registration
az ad app create --display-name "ClaudeCodeExecutionBot" --available-to-other-tenants

# Note the appId from the output
APP_ID=<your-app-id>

# Create password
az ad app credential reset --id $APP_ID --credential-description "BotSecret"

# Note the password from the output
APP_PASSWORD=<your-password>

# Create Bot Channels Registration
az bot create \
    --resource-group rg-claude-bot \
    --name claude-code-bot \
    --kind registration \
    --appid $APP_ID \
    --location global \
    --sku F0
```

### 1.3 Create App Service Plan & Web App

```bash
# Create App Service Plan
az appservice plan create \
    --name asp-claude-bot \
    --resource-group rg-claude-bot \
    --sku B1 \
    --is-linux

# Create Web App
az webapp create \
    --resource-group rg-claude-bot \
    --plan asp-claude-bot \
    --name claude-code-bot-app \
    --runtime "PYTHON:3.9"
```

## Step 2: Configure Application

### 2.1 Set Environment Variables

```bash
az webapp config appsettings set \
    --resource-group rg-claude-bot \
    --name claude-code-bot-app \
    --settings \
        MicrosoftAppId=$APP_ID \
        MicrosoftAppPassword=$APP_PASSWORD \
        ANTHROPIC_API_KEY=<your-anthropic-api-key>
```

### 2.2 Update Bot Messaging Endpoint

```bash
az bot update \
    --resource-group rg-claude-bot \
    --name claude-code-bot \
    --endpoint "https://claude-code-bot-app.azurewebsites.net/api/messages"
```

## Step 3: Deploy the Bot Code

### 3.1 Prepare for Deployment

Create a `.env` file (DO NOT commit to git):

```env
MicrosoftAppId=<your-app-id>
MicrosoftAppPassword=<your-password>
ANTHROPIC_API_KEY=<your-anthropic-api-key>
```

Create `startup.txt` file:

```
gunicorn --bind 0.0.0.0:8000 --worker-class aiohttp.GunicornWebWorker --timeout 600 app:app
```

Create `app.py` for Azure deployment:

```python
#!/usr/bin/env python3
"""
Azure App Service entry point for Teams Bot
"""

import os
import logging
from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import TurnContext
from botbuilder.schema import Activity

# Import our bot components
from bot import adapter, bot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_messages(req: Request) -> Response:
    """Handle incoming messages from Teams"""
    if req.headers.get("Content-Type") == "application/json":
        body = await req.json()
        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")
        
        try:
            invoke_response = await adapter.process_activity(
                activity, auth_header, bot.on_turn
            )
            if invoke_response:
                return web.json_response(
                    data=invoke_response.body,
                    status=invoke_response.status
                )
            return web.Response(status=201)
        except Exception as e:
            logger.error(f"Error: {e}")
            return web.Response(status=500)
    else:
        return web.Response(status=415)

# Create the application
app = web.Application()
app.router.add_post("/api/messages", handle_messages)

# Health check endpoint
async def health_check(request):
    return web.Response(text="OK", status=200)

app.router.add_get("/", health_check)

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 8000))
        web.run_app(app, host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise
```

### 3.2 Deploy to Azure

Using Azure CLI:

```bash
# Create deployment package
zip -r deployment.zip . -x "*.pyc" -x "__pycache__/*" -x ".env" -x ".git/*" -x "tests/*"

# Deploy
az webapp deployment source config-zip \
    --resource-group rg-claude-bot \
    --name claude-code-bot-app \
    --src deployment.zip
```

Or using Git deployment:

```bash
# Configure deployment user
az webapp deployment user set \
    --user-name <deployment-username> \
    --password <deployment-password>

# Get Git URL
az webapp deployment source config-local-git \
    --resource-group rg-claude-bot \
    --name claude-code-bot-app

# Add Azure as remote and push
git remote add azure <deployment-git-url>
git push azure main
```

## Step 4: Configure Teams Channel

### 4.1 Enable Teams Channel

```bash
az bot msteams create \
    --resource-group rg-claude-bot \
    --name claude-code-bot
```

### 4.2 Create Teams App Manifest

Create `manifest.json`:

```json
{
    "$schema": "https://developer.microsoft.com/en-us/json-schemas/teams/v1.14/MicrosoftTeams.schema.json",
    "manifestVersion": "1.14",
    "version": "1.0.0",
    "id": "<generate-a-guid>",
    "packageName": "com.company.claudecodebot",
    "developer": {
        "name": "Your Company",
        "websiteUrl": "https://your-website.com",
        "privacyUrl": "https://your-website.com/privacy",
        "termsOfUseUrl": "https://your-website.com/terms"
    },
    "icons": {
        "color": "color.png",
        "outline": "outline.png"
    },
    "name": {
        "short": "Claude Code Bot",
        "full": "Claude Code Execution Assistant"
    },
    "description": {
        "short": "AI assistant with code execution",
        "full": "Claude AI assistant that can execute Python code, analyze data, and generate reports directly in Teams."
    },
    "accentColor": "#FFFFFF",
    "bots": [
        {
            "botId": "<your-app-id>",
            "scopes": [
                "personal",
                "team",
                "groupchat"
            ],
            "supportsFiles": true,
            "isNotificationOnly": false,
            "commandLists": [
                {
                    "scopes": ["personal", "team", "groupchat"],
                    "commands": [
                        {
                            "title": "help",
                            "description": "Show available commands and features"
                        },
                        {
                            "title": "reset",
                            "description": "Clear conversation history"
                        },
                        {
                            "title": "files",
                            "description": "List uploaded files"
                        }
                    ]
                }
            ]
        }
    ],
    "permissions": [
        "identity",
        "messageTeamMembers"
    ],
    "validDomains": [
        "claude-code-bot-app.azurewebsites.net"
    ]
}
```

### 4.3 Upload to Teams

1. Create a ZIP file containing:
   - `manifest.json`
   - `color.png` (192x192 icon)
   - `outline.png` (32x32 icon)

2. In Teams:
   - Go to Apps → Manage your apps
   - Click "Upload an app"
   - Select "Upload a custom app"
   - Upload your ZIP file

## Step 5: Testing

### 5.1 Test in Teams

1. Search for "Claude Code Bot" in Teams
2. Start a conversation
3. Try these commands:
   - `/help` - View available commands
   - `Create a simple bar chart` - Test code execution
   - Upload a CSV file and ask for analysis

### 5.2 Monitor Logs

```bash
# View application logs
az webapp log tail \
    --resource-group rg-claude-bot \
    --name claude-code-bot-app

# View deployment logs
az webapp log deployment show \
    --resource-group rg-claude-bot \
    --name claude-code-bot-app
```

## Step 6: Production Considerations

### 6.1 Security

1. **Enable Managed Identity**:
```bash
az webapp identity assign \
    --resource-group rg-claude-bot \
    --name claude-code-bot-app
```

2. **Use Key Vault for Secrets**:
```bash
# Create Key Vault
az keyvault create \
    --name kv-claude-bot \
    --resource-group rg-claude-bot \
    --location eastus

# Add secrets
az keyvault secret set \
    --vault-name kv-claude-bot \
    --name "AnthropicApiKey" \
    --value "<your-api-key>"

# Grant access to Web App
az keyvault set-policy \
    --name kv-claude-bot \
    --object-id <managed-identity-object-id> \
    --secret-permissions get list
```

### 6.2 Scaling

1. **Configure Autoscaling**:
```bash
az monitor autoscale create \
    --resource-group rg-claude-bot \
    --name autoscale-claude-bot \
    --resource claude-code-bot-app \
    --resource-type Microsoft.Web/serverfarms \
    --min-count 1 \
    --max-count 5 \
    --count 1
```

2. **Use Azure Redis Cache** for conversation state
3. **Use Cosmos DB** for persistent storage

### 6.3 Monitoring

1. **Enable Application Insights**:
```bash
az monitor app-insights component create \
    --app insights-claude-bot \
    --location eastus \
    --resource-group rg-claude-bot

# Connect to Web App
az webapp config appsettings set \
    --resource-group rg-claude-bot \
    --name claude-code-bot-app \
    --settings APPINSIGHTS_INSTRUMENTATIONKEY=<instrumentation-key>
```

2. **Set up Alerts** for:
   - High error rates
   - Response time degradation
   - API quota usage

## Troubleshooting

### Common Issues

1. **Bot not responding**:
   - Check messaging endpoint in Bot Configuration
   - Verify App ID and Password are correct
   - Check application logs

2. **Authentication errors**:
   - Ensure App Registration has correct permissions
   - Verify credentials in environment variables

3. **File upload issues**:
   - Check file size limits (Teams: 20MB)
   - Verify bot has file permissions in manifest

### Debug Mode

Enable detailed logging:

```python
# In bot.py
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Next Steps

1. **Customize the bot**:
   - Add more commands
   - Integrate with other services
   - Customize report templates

2. **Enhance security**:
   - Implement rate limiting
   - Add user authentication
   - Enable audit logging

3. **Optimize performance**:
   - Implement caching
   - Use async operations
   - Optimize Claude API calls

## Support

For issues specific to:
- **Bot Framework**: [Bot Framework Documentation](https://docs.microsoft.com/en-us/azure/bot-service/)
- **Teams Apps**: [Teams Developer Documentation](https://docs.microsoft.com/en-us/microsoftteams/platform/)
- **Claude API**: [Anthropic Documentation](https://docs.anthropic.com/)

Remember to monitor your Azure costs and Claude API usage regularly!