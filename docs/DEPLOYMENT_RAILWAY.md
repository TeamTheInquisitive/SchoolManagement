# Deploying School ERP Backend on Railway.app

## Overview

Railway gives you a managed platform with MySQL, Redis, and Python — no server management needed. Free tier available, then $5/month.

---

## Step 1: Push code to GitHub

```bash
cd /Users/kskvamsi/Documents/Vamsi/Personal/BusinessIdea/SchoolManagementPlatform/SchoolManagement
git add -A
git commit -m "Ready for Railway deployment"
git remote add origin https://github.com/YOUR_USERNAME/school-erp-backend.git
git push -u origin main
```

---

## Step 2: Create Railway account & project

1. Go to [railway.app](https://railway.app) and sign up with GitHub
2. Click **"New Project"**
3. Choose **"Deploy from GitHub Repo"**
4. Select your `school-erp-backend` repo

---

## Step 3: Add MySQL service

1. In your Railway project, click **"+ New"** → **"Database"** → **"MySQL"**
2. Railway auto-creates the database and gives you connection variables
3. Click on the MySQL service → **"Variables"** tab → note these:
   - `MYSQL_HOST`
   - `MYSQL_PORT`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_DATABASE`

---

## Step 4: Add Redis service

1. Click **"+ New"** → **"Database"** → **"Redis"**
2. Note the `REDIS_URL` variable

---

## Step 5: Configure environment variables

Click on your **app service** → **"Variables"** tab → **"Raw Editor"** and paste:

```env
APP_NAME=School ERP Backend
ENVIRONMENT=production
DEBUG=false

MYSQL_HOST=${{MySQL.MYSQLHOST}}
MYSQL_PORT=${{MySQL.MYSQLPORT}}
MYSQL_USER=${{MySQL.MYSQLUSER}}
MYSQL_PASSWORD=${{MySQL.MYSQLPASSWORD}}
MYSQL_DB=${{MySQL.MYSQLDATABASE}}

REDIS_URL=${{Redis.REDIS_URL}}

JWT_SECRET_KEY=GENERATE_A_RANDOM_STRING_HERE
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

ALLOWED_ORIGINS=["https://yourdomain.com","https://your-frontend.railway.app"]

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=noreply@school.com

UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=10
```

> Generate JWT secret: `python -c "import secrets; print(secrets.token_hex(32))"`

---

## Step 6: Add required files to your repo

### `requirements.txt` (Railway uses this by default)

```bash
cd /Users/kskvamsi/Documents/Vamsi/Personal/BusinessIdea/SchoolManagementPlatform/SchoolManagement
source venv/bin/activate
pip freeze > requirements.txt
```

### `Procfile` (tells Railway how to start the app)

Create `Procfile` in project root:

```
web: gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### `runtime.txt` (optional, specify Python version)

```
python-3.12.8
```

---

## Step 7: Deploy

Push the new files:

```bash
git add requirements.txt Procfile runtime.txt
git commit -m "Add Railway deployment files"
git push
```

Railway auto-detects the push and deploys.

---

## Step 8: Create tables & seed data

Once deployed, open the Railway **app service** → click **"Shell"** (or use `railway run`):

```bash
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

---

## Step 9: Add custom domain (optional)

1. Click your app service → **"Settings"** → **"Networking"**
2. Click **"Generate Domain"** (gives you `*.railway.app` URL)
3. Or click **"Custom Domain"** → add `api.yourdomain.com`
4. Add the CNAME record in your DNS provider

---

## Step 10: Verify

```bash
curl https://your-app.railway.app/health
# → {"status":"healthy","app":"School ERP Backend"}
```

---

## Project structure for Railway

```
SchoolManagement/
├── Procfile              ← tells Railway how to start
├── requirements.txt      ← Python dependencies
├── runtime.txt           ← Python version
├── pyproject.toml
├── src/
│   ├── main.py
│   ├── core/
│   ├── models/
│   ├── admin/
│   ├── teacher/
│   └── student/
└── ...
```

---

## Costs (Railway pricing)

| Service | Free Tier | Paid |
|---------|-----------|------|
| App | 500 hours/month | $5/month |
| MySQL | 1GB storage | $5/month |
| Redis | 256MB | $3/month |
| **Total** | **Free to start** | **~$13/month** |

---

## Troubleshooting

### View logs
Click your app service → **"Logs"** tab

### Redeploy
Push a new commit or click **"Redeploy"** in Railway dashboard

### Connect to MySQL locally
```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway link  # link to your project
railway run mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -h $MYSQL_HOST $MYSQL_DB
```
