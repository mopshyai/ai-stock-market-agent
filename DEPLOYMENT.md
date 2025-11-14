# 🚀 Deployment Guide

How to deploy AI Stock Market Agent to production (cloud, VPS, or local server).

---

## 📋 Pre-Deployment Checklist

- [ ] All features tested locally
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] Dependencies documented
- [ ] Security considerations reviewed
- [ ] Backup strategy planned

---

## 🖥️ Local Server Deployment

### Option 1: Run as Background Service (Linux/macOS)

**Using systemd (Linux):**

1. Create service file:
```bash
sudo nano /etc/systemd/system/stock-agent.service
```

2. Add configuration:
```ini
[Unit]
Description=AI Stock Market Agent
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/ai_stock_agent_fresh2
Environment="PATH=/path/to/ai_stock_agent_fresh2/.venv/bin"
ExecStart=/path/to/ai_stock_agent_fresh2/.venv/bin/python scheduler.py --time 09:30 --timezone US/Eastern
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start:
```bash
sudo systemctl enable stock-agent
sudo systemctl start stock-agent
sudo systemctl status stock-agent
```

**Using launchd (macOS):**

1. Create plist file:
```bash
nano ~/Library/LaunchAgents/com.stockagent.scheduler.plist
```

2. Add configuration:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.stockagent.scheduler</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/ai_stock_agent_fresh2/.venv/bin/python</string>
        <string>/path/to/ai_stock_agent_fresh2/scheduler.py</string>
        <string>--time</string>
        <string>09:30</string>
        <string>--timezone</string>
        <string>US/Eastern</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/ai_stock_agent_fresh2</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/path/to/ai_stock_agent_fresh2/scheduler.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/ai_stock_agent_fresh2/scheduler.error.log</string>
</dict>
</plist>
```

3. Load service:
```bash
launchctl load ~/Library/LaunchAgents/com.stockagent.scheduler.plist
launchctl start com.stockagent.scheduler
```

---

## ☁️ Cloud Deployment Options

### Option 1: AWS EC2

**Steps:**

1. **Launch EC2 instance:**
   - Ubuntu 22.04 LTS
   - t2.micro (free tier) or t3.small
   - Security group: Allow SSH (22) and HTTP (8501)

2. **Connect and setup:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip -y

# Clone repository
git clone your-repo-url
cd ai_stock_agent_fresh2

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Setup environment variables
nano .env
# Add your TELEGRAM_BOT_TOKEN, etc.

# Initialize database
python -c "from database import init_database; init_database()"
```

3. **Run scheduler:**
```bash
# Using screen or tmux
screen -S stock-agent
source .venv/bin/activate
python scheduler.py --time 09:30 --timezone US/Eastern
# Press Ctrl+A, then D to detach
```

4. **Run dashboard (optional):**
```bash
# Install nginx as reverse proxy
sudo apt install nginx -y

# Configure nginx
sudo nano /etc/nginx/sites-available/stock-agent
```

Nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/stock-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Run Streamlit
streamlit run dashboard.py --server.port 8501 --server.address 127.0.0.1
```

---

### Option 2: Google Cloud Platform (GCP)

**Using Cloud Run (Serverless):**

1. **Create Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "scheduler.py", "--time", "09:30", "--timezone", "US/Eastern"]
```

2. **Deploy:**
```bash
# Install gcloud CLI
# Then:
gcloud run deploy stock-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars TELEGRAM_BOT_TOKEN=xxx,TELEGRAM_CHAT_ID=xxx
```

**Note:** Cloud Run is serverless, so scheduler needs adjustment for persistent execution.

---

### Option 3: DigitalOcean Droplet

**Steps:**

1. **Create Droplet:**
   - Ubuntu 22.04
   - $6/month (1GB RAM) minimum
   - Add SSH key

2. **Follow EC2 setup steps** (same as AWS)

3. **Use systemd** for service management (see Local Server section)

---

### Option 4: Heroku

**Note:** Heroku free tier discontinued. Requires paid dyno.

1. **Create Procfile:**
```
worker: python scheduler.py --time 09:30 --timezone US/Eastern
web: streamlit run dashboard.py --server.port $PORT --server.address 0.0.0.0
```

2. **Deploy:**
```bash
heroku create your-app-name
heroku config:set TELEGRAM_BOT_TOKEN=xxx
heroku config:set TELEGRAM_CHAT_ID=xxx
git push heroku main
```

---

### Option 5: Railway

**Steps:**

1. **Connect GitHub repo** to Railway
2. **Set environment variables** in Railway dashboard
3. **Configure start command:**
   ```
   python scheduler.py --time 09:30 --timezone US/Eastern
   ```
4. **Deploy** (automatic on git push)

---

## 🐳 Docker Deployment

**Create Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p charts

# Expose port (for dashboard)
EXPOSE 8501

# Default command (scheduler)
CMD ["python", "scheduler.py", "--time", "09:30", "--timezone", "US/Eastern"]
```

**Create docker-compose.yml:**
```yaml
version: '3.8'

services:
  scheduler:
    build: .
    container_name: stock-agent-scheduler
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
    volumes:
      - ./stock_agent.db:/app/stock_agent.db
      - ./charts:/app/charts
      - ./scan_results.csv:/app/scan_results.csv
    restart: unless-stopped

  dashboard:
    build: .
    container_name: stock-agent-dashboard
    command: streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
    ports:
      - "8501:8501"
    volumes:
      - ./stock_agent.db:/app/stock_agent.db
      - ./charts:/app/charts
      - ./scan_results.csv:/app/scan_results.csv
    restart: unless-stopped
    depends_on:
      - scheduler
```

**Deploy:**
```bash
docker-compose up -d
```

---

## 🔒 Security Considerations

### 1. Environment Variables
- **Never commit** `.env` file
- Use secure secret management (AWS Secrets Manager, GCP Secret Manager)
- Rotate tokens regularly

### 2. Database Security
- Backup database regularly
- Use encrypted storage if sensitive
- Restrict file permissions: `chmod 600 stock_agent.db`

### 3. Network Security
- Use HTTPS for dashboard (Let's Encrypt SSL)
- Restrict dashboard access (firewall, VPN)
- Use strong passwords for server access

### 4. API Security
- Rate limit API calls
- Monitor for abuse
- Use API keys if exposing endpoints

---

## 📊 Monitoring & Logging

### Setup Logging

```python
# Add to scheduler.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
```

### Monitor Health

Create `health_check.py`:
```python
import requests
import sqlite3
from datetime import datetime, timedelta

def check_health():
    # Check database
    conn = sqlite3.connect('stock_agent.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM scans WHERE scan_date > ?", 
                   (datetime.now() - timedelta(days=1),))
    recent_scans = cursor.fetchone()[0]
    conn.close()
    
    # Check if scans are running
    if recent_scans == 0:
        print("⚠️ WARNING: No scans in last 24 hours")
        return False
    
    print(f"✅ Health OK: {recent_scans} scans in last 24 hours")
    return True

if __name__ == "__main__":
    check_health()
```

### Setup Alerts

- Use monitoring services (UptimeRobot, Pingdom)
- Email alerts on failures
- Telegram alerts for critical issues

---

## 💾 Backup Strategy

### Automated Backups

**Create backup script:**
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"

# Backup database
cp stock_agent.db "$BACKUP_DIR/stock_agent_$DATE.db"

# Backup config
cp config.yaml "$BACKUP_DIR/config_$DATE.yaml"

# Keep only last 7 days
find "$BACKUP_DIR" -name "*.db" -mtime +7 -delete
```

**Schedule with cron:**
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh
```

---

## 🔄 Updates & Maintenance

### Update Process

1. **Pull latest code:**
```bash
git pull origin main
```

2. **Update dependencies:**
```bash
source .venv/bin/activate
pip install -r requirements.txt --upgrade
```

3. **Restart services:**
```bash
# systemd
sudo systemctl restart stock-agent

# docker
docker-compose restart
```

### Maintenance Window

- Schedule updates during off-market hours
- Test updates in staging first
- Keep backups before major updates

---

## 📈 Scaling Considerations

### For High Volume

1. **Database optimization:**
   - Index frequently queried columns
   - Archive old data
   - Use PostgreSQL for production

2. **Caching:**
   - Cache scan results
   - Use Redis for session data

3. **Load balancing:**
   - Multiple dashboard instances
   - Use nginx load balancer

4. **Queue system:**
   - Use Celery for async tasks
   - Process scans in background

---

## ✅ Post-Deployment Checklist

- [ ] Scheduler running and logging
- [ ] Dashboard accessible
- [ ] Telegram alerts working
- [ ] Database storing data
- [ ] Backups configured
- [ ] Monitoring active
- [ ] Documentation updated
- [ ] Team notified

---

## 🆘 Rollback Plan

If deployment fails:

1. **Stop new deployment:**
```bash
sudo systemctl stop stock-agent
# or
docker-compose down
```

2. **Restore from backup:**
```bash
cp backup/stock_agent_YYYYMMDD.db stock_agent.db
```

3. **Revert code:**
```bash
git checkout previous-commit-hash
```

4. **Restart:**
```bash
sudo systemctl start stock-agent
```

---

*Last updated: January 2025*

