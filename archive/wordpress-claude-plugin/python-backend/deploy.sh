#!/bin/bash
# Quick deployment script for DigitalOcean

echo "=== Claude Backend Deployment Script ==="
echo "This script will help deploy your Flask backend to a DigitalOcean droplet"
echo ""

# Check if running as claude user
if [ "$USER" != "claude" ]; then
    echo "Please run this script as the 'claude' user"
    exit 1
fi

# Install dependencies
echo "1. Installing system dependencies..."
sudo apt update
sudo apt install -y python3-pip python3-venv nginx supervisor git

# Create project directory
echo "2. Setting up project directory..."
cd ~
mkdir -p claude-backend

# Set up Python environment
echo "3. Creating Python virtual environment..."
cd claude-backend
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "4. Installing Python dependencies..."
pip install --upgrade pip
pip install flask flask-cors anthropic gunicorn python-dotenv rich click

# Create necessary files if they don't exist
echo "5. Creating configuration files..."

# Create .env file
if [ ! -f .env ]; then
    cat > .env << 'EOF'
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=*
EOF
    echo "Created .env file - please update CORS_ORIGINS with your WordPress URL"
fi

# Create supervisor config
sudo tee /etc/supervisor/conf.d/claude-backend.conf > /dev/null << 'EOF'
[program:claude-backend]
command=/home/claude/claude-backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 --timeout 300 claude_backend_server:app
directory=/home/claude/claude-backend
user=claude
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/claude-backend.log
environment=PATH="/home/claude/claude-backend/venv/bin",PYTHONPATH="/home/claude:/home/claude/claude-backend"
EOF

# Create nginx config
sudo tee /etc/nginx/sites-available/claude-backend > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

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
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        proxy_buffering off;
    }

    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
EOF

# Enable nginx site
echo "6. Configuring Nginx..."
sudo ln -sf /etc/nginx/sites-available/claude-backend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# Start services
echo "7. Starting services..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart claude-backend

# Configure firewall
echo "8. Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
echo "y" | sudo ufw enable

# Show status
echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Next steps:"
echo "1. Upload your Python files to ~/claude-backend/"
echo "2. Update the .env file with your settings"
echo "3. Set up SSL with: sudo certbot --nginx -d your-domain.com"
echo "4. Test the endpoint: curl http://your-server-ip/health"
echo ""
echo "Service status:"
sudo supervisorctl status claude-backend
echo ""
echo "Server IP: $(curl -s ifconfig.me)"