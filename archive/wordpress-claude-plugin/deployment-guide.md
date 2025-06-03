# Quick Deployment Guide

## Fastest Deployment Method: Using Vercel/Railway for Python Backend

### Step 1: Deploy Python Backend to Railway (5 minutes)

1. **Create a Railway account** at https://railway.app

2. **Prepare your backend:**
   ```bash
   cd python-backend
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Create `railway.json`:**
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "gunicorn --bind 0.0.0.0:$PORT claude_backend_server:app"
     }
   }
   ```

4. **Deploy to Railway:**
   - Go to https://railway.app/new
   - Choose "Deploy from GitHub repo" or "Deploy from CLI"
   - If using CLI:
     ```bash
     npm install -g @railway/cli
     railway login
     railway init
     railway up
     ```

5. **Get your backend URL** from Railway dashboard (e.g., `https://your-app.railway.app`)

### Step 2: Install WordPress Plugin (10 minutes)

1. **Download the plugin:**
   ```bash
   cd claude-code-execution
   zip -r claude-code-execution.zip . -x "*.git*"
   ```

2. **Install via WordPress Admin:**
   - Go to Plugins → Add New → Upload Plugin
   - Choose the `claude-code-execution.zip` file
   - Click "Install Now" then "Activate"

3. **Configure the plugin:**
   - Go to Claude AI → Settings
   - Enter your Anthropic API Key
   - Enter the Railway backend URL
   - Save settings

4. **Add to a page:**
   - Create a new page
   - Add the shortcode: `[claude_chat]`
   - Publish the page

## Alternative: One-Click Deployment Options

### Using Replit (Easiest for Testing)

1. **Fork this Replit:** https://replit.com/@YourUsername/claude-backend
2. **Set environment variables:**
   - `ANTHROPIC_API_KEY` (optional, can be sent per request)
3. **Click "Run"**
4. **Use the Replit URL** in WordPress settings

### Using Vercel (Serverless)

1. **Create `vercel.json`:**
   ```json
   {
     "builds": [
       {
         "src": "python-backend/claude_backend_server.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "python-backend/claude_backend_server.py"
       }
     ]
   }
   ```

2. **Deploy:**
   ```bash
   npm i -g vercel
   vercel
   ```

### Using Heroku (Traditional)

1. **Create `Procfile`:**
   ```
   web: gunicorn claude_backend_server:app
   ```

2. **Deploy:**
   ```bash
   heroku create your-claude-backend
   git push heroku main
   ```

## Minimum Requirements Deployment

### For Testing/Development Only:

1. **Run Python backend locally:**
   ```bash
   cd python-backend
   pip install -r requirements.txt
   python claude_backend_server.py
   ```

2. **Use ngrok for public URL:**
   ```bash
   ngrok http 5000
   ```

3. **Use the ngrok URL** in WordPress settings

⚠️ **Warning:** This method is only for testing. Not suitable for production.

## WordPress.com Business Plan Deployment

If you're using WordPress.com (not self-hosted):

1. You need at least the **Business plan** to install custom plugins
2. Upload the plugin via SFTP or use the Code Editor
3. The Python backend must be hosted separately (use Railway/Vercel)

## Troubleshooting Quick Fixes

**Backend not responding:**
```bash
curl https://your-backend-url/health
```

**CORS issues:**
Add your WordPress domain to the backend's CORS settings.

**SSL/HTTPS errors:**
Both WordPress and the backend must use HTTPS in production.

## 5-Minute Setup Checklist

- [ ] Deploy Python backend to Railway/Vercel
- [ ] Get backend URL
- [ ] Install WordPress plugin
- [ ] Add Anthropic API key
- [ ] Configure backend URL
- [ ] Add `[claude_chat]` to a page
- [ ] Test the chat interface

That's it! Your Claude AI chat with code execution should now be live on your WordPress site.