# Claude Code Execution Assistant for Microsoft Teams

A sophisticated Microsoft Teams bot that integrates Claude AI with code execution capabilities, providing intelligent assistance with data analysis, code generation, and document processing directly within Teams.

## 🏗️ Project Structure

```
codeexec-test/
├── src/                    # Source code
│   ├── __init__.py
│   ├── core/              # Core Claude integration
│   │   ├── __init__.py
│   │   └── claude_core.py # UI-agnostic Claude logic
│   ├── bot/               # Teams bot implementation
│   │   ├── __init__.py
│   │   └── bot.py         # Bot Framework integration
│   └── ui/                # UI components
│       ├── __init__.py
│       └── teams_formatter.py # Adaptive Cards formatting
├── tests/                 # Test suites
│   ├── __init__.py
│   ├── unit/             # Unit tests
│   │   ├── __init__.py
│   │   ├── test_claude_core.py
│   │   ├── test_bot.py
│   │   └── test_teams_formatter.py
│   └── integration/      # Integration tests
│       ├── __init__.py
│       └── test_ui_puppeteer.js
├── docs/                  # Documentation
│   └── API.md
├── demos/                 # UI demonstrations
│   ├── adaptive_cards_demo.html
│   └── screenshots/      # UI test screenshots
├── data/                  # Sample data files
│   ├── sample_data.csv
│   └── test_document.pdf
├── archive/              # Archived/old files
├── app.py               # Main application entry point
├── requirements.txt     # Python dependencies
├── package.json        # Node.js dependencies (for UI tests)
├── deployment.yaml     # Azure deployment configuration
└── .gitignore         # Git ignore patterns
```

## 🚀 Features

- **Claude AI Integration**: Leverages Claude's advanced capabilities for natural language understanding and code generation
- **Code Execution**: Safely executes Python code with isolated environments
- **File Processing**: Handles various file types (PDF, Excel, CSV, JSON)
- **Adaptive Cards UI**: Rich, interactive UI using Microsoft Teams Adaptive Cards
- **TCEL Branding**: Professional styling following TC TASMAN CONSULTING ENGINEERS template
- **Multi-turn Conversations**: Maintains context across multiple interactions
- **Web Search Integration**: Access to current information via web search
- **Error Handling**: Comprehensive error handling and user-friendly error messages

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+ (for UI testing)
- Azure subscription (for deployment)
- Microsoft Teams workspace
- Anthropic API key

## 🔧 Installation

### 1. Navigate to Project Directory
```bash
cd /home/ben_anderson/projects/codeexec-test
```

### 2. Set Up Python Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install Node Dependencies (for UI testing)
```bash
npm install
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key
MicrosoftAppId=your_bot_app_id
MicrosoftAppPassword=your_bot_app_password
```

## 🏃‍♂️ Running Locally

### Start the Bot Server
```bash
python app.py
```
The bot will start on `http://localhost:3978`

### Using Bot Framework Emulator
1. Download [Bot Framework Emulator](https://github.com/Microsoft/BotFramework-Emulator)
2. Connect to `http://localhost:3978/api/messages`
3. Enter your Microsoft App ID and Password

## 🧪 Testing

### Run Unit Tests
```bash
python -m pytest tests/unit/ -v
```

### Run UI Tests with Puppeteer
```bash
npm test
```

### Run Specific Test Suite
```bash
# Test Claude core functionality
python tests/unit/test_claude_core.py

# Test bot implementation
python tests/unit/test_bot.py

# Test Teams formatter
python tests/unit/test_teams_formatter.py
```

## 💬 Bot Commands

- `/help` - Display available commands and features
- `/reset` - Clear conversation history
- `/files` - List uploaded files
- `/nocode <message>` - Send message without code execution
- `/info` - Show bot information and status

## 📱 Teams Integration

### Setting Up in Teams

1. **Register Bot in Azure**
   - Create a new Bot Channels Registration in Azure Portal
   - Note the App ID and generate a password
   - Add Teams channel

2. **Configure Manifest**
   - Update `teams_manifest.json` with your bot ID
   - Package and upload to Teams

3. **Deploy to Azure**
   ```bash
   az webapp deployment source config-zip \
     --resource-group <resource-group> \
     --name <app-name> \
     --src deployment.zip
   ```

## 🎨 UI Components

The bot uses Adaptive Cards for rich interactions:

- **Welcome Card**: Displayed when users first interact
- **Help Card**: Shows available commands and examples
- **Report Card**: Displays analysis results with TCEL branding
- **Error Card**: User-friendly error messages
- **Files Card**: Lists uploaded files with metadata

## 🔒 Security Considerations

- Code execution happens in isolated environments
- File uploads are validated and scanned
- API keys are stored securely in environment variables
- Teams authentication ensures secure access
- Rate limiting prevents abuse

## 🚢 Deployment

### Azure App Service
```bash
# Build and deploy
./deploy.sh
```

### Docker Container
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

## 📊 Monitoring

- Application Insights integration for telemetry
- Structured logging with correlation IDs
- Performance metrics tracking
- Error reporting and alerting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary to TC TASMAN CONSULTING ENGINEERS.

## 🆘 Support

For issues and questions:
- Check the [docs](./docs) folder
- Review test files for examples
- Contact the development team

## 🔄 Recent Updates

- Reorganized project structure for better maintainability
- Added comprehensive test coverage
- Implemented TCEL branding in Adaptive Cards
- Enhanced error handling and user feedback
- Added Puppeteer UI testing framework