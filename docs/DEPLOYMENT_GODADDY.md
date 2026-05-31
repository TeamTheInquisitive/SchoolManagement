# Deploying School ERP FastAPI Backend on GoDaddy cPanel

## ⚠️ Important: cPanel Limitations

GoDaddy's shared hosting with cPanel is **NOT ideal** for FastAPI because:
- cPanel is designed for PHP apps, not Python ASGI apps
- No root/SSH access on basic shared plans
- No systemd for process management
- Limited Python version support

**You need one of these GoDaddy plans:**
- **VPS Hosting** (recommended) — gives SSH + root access
- **Business/Pro Hosting with SSH** — limited but workable via Passenger
- **Dedicated Server** — full control

---

## Option A: GoDaddy VPS (Recommended)

### Prerequisites
- GoDaddy VPS or Dedicated Server with SSH access
- Domain pointed to your server IP

### Step 1: SSH into your server

```bash
ssh root@your-server-ip
```

### Step 2: Install system dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.12
apt install -y software-properties-common
add-apt-repository ppa:deadsnakes/ppa -y
apt install -y python3.12 python3.12-venv python3.12-dev

# Install MySQL
apt install -y mysql-server

# Install Redis
apt install -y redis-server

# Install Nginx
apt install -y nginx

# Install Git
apt install -y git
```

### Step 3: Configure MySQL

```bash
# Secure MySQL installation
mysql_secure_installation

# Create database and user
mysql -u root -p <<EOF
CREATE DATABASE SchoolManagement CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'school_erp'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';
GRANT ALL PRIVILEGES ON SchoolManagement.* TO 'school_erp'@'localhost';
FLUSH PRIVILEGES;
EOF
```

### Step 4: Upload your project

```bash
# Option 1: Git clone (if you have a repo)
cd /opt
git clone https://github.com/your-username/SchoolManagement.git
cd SchoolManagement

# Option 2: SCP from local machine (run on your Mac)
# scp -r /Users/kskvamsi/Documents/Vamsi/Personal/BusinessIdea/SchoolManagementPlatform/SchoolManagement root@your-server-ip:/opt/SchoolManagement
```

### Step 5: Setup Python environment

```bash
cd /opt/SchoolManagement
python3.12 -m venv venv
source venv/bin/activate
pip install -e .
pip install gunicorn
```

### Step 6: Configure environment

```bash
cat > .env << 'EOF'
# App
APP_NAME=School ERP Backend
ENVIRONMENT=production
DEBUG=false

# Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=school_erp
MYSQL_PASSWORD=YourStrongPassword123!
MYSQL_DB=SchoolManagement

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT - CHANGE THIS! Generate with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=CHANGE_ME_TO_A_RANDOM_64_CHAR_STRING
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS - Update with your actual frontend domain
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@yourdomain.com

# File Upload
UPLOAD_DIR=/opt/SchoolManagement/uploads
MAX_FILE_SIZE_MB=10
EOF
```

### Step 7: Create database tables and seed data

```bash
source venv/bin/activate

# Create tables
python -c "
import asyncio
from src.core.database import engine
from src.core.base_model import Base
from src.models import *
async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
asyncio.run(create_all())
"

# Seed initial data
python -m src.seeds.initial

# (Optional) Seed demo data
python -m src.seeds.demo_data
```

### Step 8: Create systemd service (auto-start on boot)

```bash
cat > /etc/systemd/system/school-erp.service << 'EOF'
[Unit]
Description=School ERP FastAPI Backend
After=network.target mysql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/SchoolManagement
Environment="PATH=/opt/SchoolManagement/venv/bin"
ExecStart=/opt/SchoolManagement/venv/bin/gunicorn src.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/school-erp/access.log \
    --error-logfile /var/log/school-erp/error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Create log directory
mkdir -p /var/log/school-erp
chown www-data:www-data /var/log/school-erp

# Set permissions
chown -R www-data:www-data /opt/SchoolManagement

# Enable and start
systemctl daemon-reload
systemctl enable school-erp
systemctl start school-erp

# Check status
systemctl status school-erp
```

### Step 9: Configure Nginx (reverse proxy + SSL)

```bash
cat > /etc/nginx/sites-available/school-erp << 'EOF'
server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Proxy to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Serve uploaded files
    location /uploads/ {
        alias /opt/SchoolManagement/uploads/;
    }

    # Max upload size
    client_max_body_size 10M;
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/school-erp /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload
nginx -t
systemctl reload nginx
```

### Step 10: Install SSL certificate (Let's Encrypt - free)

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d api.yourdomain.com
```

### Step 11: Verify deployment

```bash
# Check service is running
curl http://localhost:8000/health

# Check from outside
curl https://api.yourdomain.com/health
```

---

## Option B: GoDaddy cPanel with Passenger (Shared Hosting)

> ⚠️ This is a workaround. Performance will be limited.

### Prerequisites
- GoDaddy hosting plan with **SSH access** and **Python Selector** in cPanel
- Terminal/SSH access enabled

### Step 1: Enable SSH in cPanel

1. Login to cPanel
2. Go to **Security > SSH Access**
3. Generate or upload your SSH key

### Step 2: SSH into your hosting

```bash
ssh your-cpanel-username@your-server-ip -p 22
```

### Step 3: Setup Python app via cPanel

1. Login to cPanel
2. Go to **Software > Setup Python App**
3. Click **Create Application**:
   - Python version: 3.12 (or highest available)
   - Application root: `school-erp`
   - Application URL: `api.yourdomain.com` (or subdomain)
   - Application startup file: `passenger_wsgi.py`
4. Click **Create**

### Step 4: Upload project files

```bash
# Via SSH
cd ~/school-erp
# Upload your project files here (via File Manager or SCP)

# Or use Git
git clone https://github.com/your-username/SchoolManagement.git .
```

### Step 5: Install dependencies

```bash
# cPanel creates a virtual environment automatically
# Enter it:
source /home/your-username/virtualenv/school-erp/3.12/bin/activate

# Install
pip install -e .
```

### Step 6: Create Passenger WSGI file

Create `~/school-erp/passenger_wsgi.py`:

```python
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from src.main import app

# Passenger expects an ASGI application
application = app
```

### Step 7: Create `.htaccess` for routing

Create `~/school-erp/public/.htaccess`:

```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ /passenger_wsgi.py/$1 [QSA,L]
```

### Step 8: Configure MySQL via cPanel

1. Go to **Databases > MySQL Databases**
2. Create database: `SchoolManagement`
3. Create user: `school_erp` with strong password
4. Add user to database with ALL PRIVILEGES

### Step 9: Update .env

```bash
# Update MYSQL credentials with cPanel-created ones
# cPanel prefixes: yourusername_SchoolManagement, yourusername_school_erp
MYSQL_HOST=localhost
MYSQL_USER=yourusername_school_erp
MYSQL_PASSWORD=your-password
MYSQL_DB=yourusername_SchoolManagement
```

### Step 10: Create tables

```bash
source /home/your-username/virtualenv/school-erp/3.12/bin/activate
cd ~/school-erp
python -c "
import asyncio
from src.core.database import engine
from src.core.base_model import Base
from src.models import *
async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
asyncio.run(create_all())
"
python -m src.seeds.initial
```

### Step 11: Restart the app

In cPanel > Setup Python App > click **Restart**

---

## Post-Deployment Checklist

- [ ] Change `JWT_SECRET_KEY` to a random string: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] Set `ENVIRONMENT=production` and `DEBUG=false`
- [ ] Update `ALLOWED_ORIGINS` with your actual frontend URLs
- [ ] Setup MySQL backups (daily cron)
- [ ] Configure email credentials for notifications
- [ ] Test all login flows (admin, teacher, student)
- [ ] Setup domain DNS (A record pointing to server IP)
- [ ] Install SSL certificate

---

## Updating the Deployment

```bash
# SSH into server
ssh root@your-server-ip

# Pull latest code
cd /opt/SchoolManagement
git pull origin main

# Install any new dependencies
source venv/bin/activate
pip install -e .

# Run migrations if schema changed
python -c "
import asyncio
from src.core.database import engine
from src.core.base_model import Base
from src.models import *
async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
asyncio.run(create_all())
"

# Restart service
systemctl restart school-erp
```

---

## Troubleshooting

### App won't start
```bash
journalctl -u school-erp -f  # View logs
systemctl status school-erp   # Check status
```

### 502 Bad Gateway
```bash
# Check if app is running
curl http://localhost:8000/health

# Check nginx config
nginx -t
```

### Database connection refused
```bash
systemctl status mysql
mysql -u school_erp -p SchoolManagement -e "SELECT 1;"
```

### Redis connection refused
```bash
systemctl status redis
redis-cli ping
```
