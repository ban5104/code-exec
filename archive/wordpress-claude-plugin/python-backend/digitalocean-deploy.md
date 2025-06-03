# DigitalOcean VPS Deployment Guide

## Step 1: Create a Droplet

1. Log into DigitalOcean
2. Create a new Droplet:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($6/month is sufficient)
   - **Region**: Choose closest to your users
   - **Authentication**: SSH keys (recommended) or password
   - **Hostname**: `claude-backend`

## Step 2: Initial Server Setup

SSH into your droplet:
```bash
ssh root@your-droplet-ip
```

### 2.1 Create a non-root user:
```bash
adduser claude
usermod -aG sudo claude
su - claude
```

### 2.2 Update system:
```bash
sudo apt update && sudo apt upgrade -y
```

### 2.3 Install required packages:
```bash
sudo apt install python3-pip python3-venv nginx supervisor git -y
```

## Step 3: Deploy Your Application

### 3.1 Clone your code:
```bash
cd ~
git clone https://github.com/yourusername/your-repo.git claude-backend
# Or use SCP to upload files:
# scp -r /home/ben_anderson/projects/codeexec-test/wordpress-claude-plugin/python-backend/* claude@your-ip:~/claude-backend/
```

### 3.2 Set up Python environment:
```bash
cd ~/claude-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3.3 Copy your original Claude script:
```bash
# Copy the original code-exec.py to the server
scp /home/ben_anderson/projects/codeexec-test/code-exec.py claude@your-ip:~/
```

### 3.4 Update the import path in claude_wrapper.py:
```bash
nano claude_wrapper.py
# Change the sys.path.append line to:
# sys.path.append('/home/claude')
```

## Step 4: Configure Supervisor (Process Manager)

### 4.1 Create supervisor config:
```bash
sudo nano /etc/supervisor/conf.d/claude-backend.conf
```

Add this content:
```ini
[program:claude-backend]
command=/home/claude/claude-backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 --timeout 300 claude_backend_server:app
directory=/home/claude/claude-backend
user=claude
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/claude-backend.log
environment=PATH="/home/claude/claude-backend/venv/bin",PYTHONPATH="/home/claude:/home/claude/claude-backend"
```

### 4.2 Start the service:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start claude-backend
```

## Step 5: Configure Nginx (Reverse Proxy)

### 5.1 Create Nginx config:
```bash
sudo nano /etc/nginx/sites-available/claude-backend
```

Add this content:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings for long Claude responses
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Increase buffer sizes for streaming
        proxy_buffering off;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
```

### 5.2 Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/claude-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 6: Set Up SSL with Let's Encrypt

### 6.1 Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 6.2 Get SSL certificate:
```bash
sudo certbot --nginx -d your-domain.com
```

## Step 7: Configure Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Step 8: Environment Variables

### 8.1 Create .env file:
```bash
cd ~/claude-backend
nano .env
```

Add:
```env
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://your-wordpress-site.com
```

### 8.2 Update supervisor config to load .env:
```bash
sudo nano /etc/supervisor/conf.d/claude-backend.conf
# Add to environment line:
# ,DOTENV_PATH="/home/claude/claude-backend/.env"
```

## Step 9: Monitoring & Logs

### View logs:
```bash
# Application logs
sudo tail -f /var/log/claude-backend.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check service status
sudo supervisorctl status claude-backend
```

### Restart service:
```bash
sudo supervisorctl restart claude-backend
```

## Step 10: WordPress Configuration

In your WordPress admin:
1. Go to Claude AI → Settings
2. Set Python Backend URL to: `https://your-domain.com`
3. Save settings

## Quick Commands Reference

```bash
# SSH to server
ssh claude@your-droplet-ip

# Restart backend
sudo supervisorctl restart claude-backend

# View logs
sudo tail -f /var/log/claude-backend.log

# Update code
cd ~/claude-backend
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart claude-backend

# Check if service is running
curl http://localhost:5000/health
```

## Security Checklist

- [ ] Non-root user created
- [ ] SSH key authentication enabled
- [ ] Firewall configured
- [ ] SSL certificate installed
- [ ] Regular security updates scheduled
- [ ] Backup strategy in place

## Troubleshooting

**502 Bad Gateway:**
- Check if Gunicorn is running: `sudo supervisorctl status`
- Check logs: `sudo tail -f /var/log/claude-backend.log`

**Connection timeout:**
- Increase Nginx timeout values
- Check if firewall allows traffic

**Import errors:**
- Verify PYTHONPATH in supervisor config
- Check file permissions

Your Flask backend should now be running securely on DigitalOcean!