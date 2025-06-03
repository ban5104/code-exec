# Claude Code Execution WordPress Plugin

This plugin integrates Claude AI with code execution capabilities into your WordPress website.

## Architecture

The solution consists of two parts:
1. **WordPress Plugin** - Provides the frontend interface and API integration
2. **Python Backend Server** - Handles the actual Claude API calls and code execution

## Installation Guide

### Step 1: Deploy the Python Backend

#### Option A: Deploy to a Cloud Service (Recommended)

**Using Heroku:**
```bash
cd python-backend
heroku create your-claude-backend
heroku config:set FLASK_DEBUG=False
git push heroku main
```

**Using DigitalOcean App Platform:**
1. Create a new app in DigitalOcean
2. Connect your GitHub repository
3. Set the build command: `pip install -r requirements.txt`
4. Set the run command: `gunicorn --bind :$PORT claude_backend_server:app`

**Using AWS EC2:**
```bash
# On your EC2 instance
cd python-backend
pip install -r requirements.txt
sudo nano /etc/systemd/system/claude-backend.service
```

Create systemd service:
```ini
[Unit]
Description=Claude Backend Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/claude-backend
Environment="PATH=/home/ubuntu/.local/bin"
ExecStart=/home/ubuntu/.local/bin/gunicorn --bind 0.0.0.0:5000 claude_backend_server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl start claude-backend
sudo systemctl enable claude-backend
```

#### Option B: Deploy with Docker

```bash
cd python-backend
docker build -t claude-backend .
docker run -d -p 5000:5000 --env-file .env claude-backend
```

#### Option C: Local Development Server

```bash
cd python-backend
pip install -r requirements.txt
python claude_backend_server.py
```

### Step 2: Install the WordPress Plugin

1. Upload the `claude-code-execution` folder to `/wp-content/plugins/`
2. Activate the plugin through the WordPress admin panel
3. Go to **Claude AI** → **Settings** in the WordPress admin
4. Configure:
   - **Anthropic API Key**: Your Claude API key
   - **Python Backend URL**: The URL where you deployed the Python backend (e.g., `https://your-backend.herokuapp.com`)
   - **Model**: Select the Claude model to use
   - **Enable Code Execution**: Check to enable code execution features

### Step 3: Add Chat Interface to Your Site

Add the chat interface to any page or post using the shortcode:

```
[claude_chat]
```

With options:
```
[claude_chat height="700px" theme="light" show_upload="true" show_code_toggle="true"]
```

## Security Considerations

### 1. API Key Security
- Store your Anthropic API key securely in WordPress
- Never expose it in frontend code
- Use environment variables for the Python backend

### 2. HTTPS Required
- Always use HTTPS for both WordPress and the Python backend
- Configure CORS properly in the Python backend

### 3. Rate Limiting
- Implement rate limiting on the Python backend
- Consider using WordPress user roles to control access

### 4. Code Execution Safety
- The code execution runs in Anthropic's sandboxed environment
- No code runs on your servers

## Deployment Best Practices

### For Production:

1. **Use a CDN** for static assets
2. **Enable caching** for API responses where appropriate
3. **Set up monitoring** for the Python backend
4. **Use a reverse proxy** (nginx) for the Python backend
5. **Enable SSL/TLS** certificates

### Nginx Configuration Example:

```nginx
server {
    listen 443 ssl;
    server_name api.your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings for long-running requests
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

## Customization

### Styling the Chat Interface

Add custom CSS to your theme:

```css
/* Custom chat styling */
.cce-chat-container {
    font-family: 'Your Font', sans-serif;
}

.cce-message.user .cce-message-content {
    background: #your-color;
}
```

### Extending Functionality

Create a custom plugin that extends this one:

```php
// Add custom hooks
add_filter('cce_before_send_message', 'my_custom_filter', 10, 2);
add_action('cce_after_receive_response', 'my_custom_action', 10, 2);
```

## Troubleshooting

### Common Issues:

1. **"Failed to connect to backend"**
   - Check the Python backend URL in settings
   - Ensure the backend is running
   - Check CORS settings

2. **"API key invalid"**
   - Verify your Anthropic API key
   - Check if the key has the necessary permissions

3. **"Code execution not working"**
   - Ensure code execution is enabled in settings
   - Check if your API key supports code execution

### Debug Mode:

Enable WordPress debug mode in `wp-config.php`:
```php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);
```

Check logs at `/wp-content/debug.log`

## API Documentation

### REST API Endpoints:

**Send Message:**
```
POST /wp-json/cce/v1/chat
Headers: X-CCE-API-Key: your-client-api-key
Body: {
    "message": "Hello Claude",
    "conversation_id": "conv_123",
    "use_code_execution": true
}
```

**Upload File:**
```
POST /wp-json/cce/v1/upload
Headers: X-CCE-API-Key: your-client-api-key
Body: multipart/form-data with 'file' field
```

## Support

For issues and feature requests, please create an issue on GitHub.

## License

GPL-2.0+ License