# Quick Start Guide

Get the Claude Code Execution Teams Bot up and running in 5 minutes!

## 🚀 Local Development

### 1. Setup Project
```bash
# You're already in the project directory with an active virtual environment!
# Current directory: /home/ben_anderson/projects/codeexec-test
# Active environment: .anthropic-env

# Just install the dependencies
pip install -r requirements.txt

# Note: If you need to create a new environment later:
# python -m venv venv
# source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Configure Environment
Create `.env` file:
```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
MicrosoftAppId=optional-for-local
MicrosoftAppPassword=optional-for-local
```

### 3. Run the Bot
```bash
python app.py
```
Bot runs on http://localhost:3978

### 4. Test with Bot Framework Emulator
- Download [Bot Framework Emulator](https://github.com/Microsoft/BotFramework-Emulator)
- Connect to `http://localhost:3978/api/messages`
- Start chatting!

## 💬 Try These Commands

```
# Basic interaction
Hello Claude, can you help me analyze some data?

# Code execution
Create a visualization of sales data over time

# File handling
/files - List uploaded files
/help - Show all commands

# Without code execution
/nocode Explain machine learning concepts
```

## 🧪 Run Tests

```bash
# All tests
python run_tests.py

# Just Python tests
python -m pytest tests/unit/ -v

# Just UI tests
npm test
```

## ☁️ Deploy to Azure

```bash
# Set environment variables
export RESOURCE_GROUP=myResourceGroup
export APP_NAME=myClaudeBot

# Deploy
./deploy.sh
```

## 📱 Add to Teams

1. Package the bot manifest
2. Upload to Teams Admin Center
3. Add bot to your team/channel
4. Start using!

## 🆘 Troubleshooting

### Bot not responding?
- Check logs: `python app.py`
- Verify API key is set
- Check network connectivity

### Tests failing?
- Ensure all dependencies installed
- Check Python version (3.8+)
- Run `pip install -r requirements.txt`

### Deployment issues?
- Verify Azure CLI is logged in
- Check resource group exists
- Ensure app service plan is compatible

## 📚 Next Steps

- Read the full [README](./README.md)
- Check [API documentation](./docs/API.md)
- Review [deployment guide](./docs/deployment-guide.md)
- Explore test examples in `tests/`

Happy coding! 🚀