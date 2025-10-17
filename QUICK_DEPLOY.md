# 🚀 TPS19 QUICK DEPLOYMENT GUIDE

## Choose Your Platform

---

## ⭐ OPTION 1: Railway.app (RECOMMENDED - 5 MINUTES)

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub

### Step 2: Deploy
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose this repository
4. Railway auto-detects Python and deploys
5. **Done!** Your bot is running 24/7

### Step 3: Add Environment Variables
1. Click on your project
2. Go to "Variables" tab
3. Add variables from `.env.example`
4. Click "Deploy" to restart

### Cost:
- Free: $5 credit/month
- Paid: ~$5-10/month

### Files Used:
- ✅ `railway.json` (auto-detected)
- ✅ `requirements_phase1.txt`

---

## 🔵 OPTION 2: Render.com (FREE TIER - 10 MINUTES)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub

### Step 2: Deploy
1. Click "New" → "Background Worker"
2. Connect your GitHub repository
3. Name: `tps19-trading-bot`
4. Environment: `Python 3`
5. Build Command: `pip install -r requirements_phase1.txt`
6. Start Command: `python3 tps19_main.py`
7. Click "Create Background Worker"

### Step 3: Add Environment Variables
1. Go to "Environment" tab
2. Add variables from `.env.example`
3. Save changes

### Step 4: Add Database (Optional)
1. Click "New" → "PostgreSQL"
2. Name: `tps19-db`
3. Copy the "Internal Database URL"
4. Add to environment as `DATABASE_URL`

### Cost:
- Free tier available (may sleep after inactivity)
- Always-on: $7/month

### Files Used:
- ✅ `render.yaml` (optional, auto-detected)
- ✅ `requirements_phase1.txt`

---

## 🟣 OPTION 3: Fly.io (FREE 24/7 - 15 MINUTES)

### Step 1: Install Fly CLI
```bash
# On Linux/Mac:
curl -L https://fly.io/install.sh | sh

# On Windows:
iwr https://fly.io/install.ps1 -useb | iex
```

### Step 2: Login
```bash
fly auth login
```

### Step 3: Create App
```bash
cd /workspace
fly launch
# Answer prompts:
# - App name: tps19-trading-bot
# - Region: Choose closest to you
# - PostgreSQL: Yes (optional)
# - Redis: No (or Yes if needed)
```

### Step 4: Set Environment Variables
```bash
fly secrets set EXCHANGE_API_KEY=your_key_here
fly secrets set EXCHANGE_API_SECRET=your_secret_here
# ... add other variables from .env.example
```

### Step 5: Deploy
```bash
fly deploy
```

### Step 6: Check Status
```bash
fly status
fly logs
```

### Cost:
- Free tier: Good for small bots
- Paid: ~$2-5/month if you exceed free tier

### Files Used:
- ✅ `Dockerfile`
- ✅ `fly.toml`
- ✅ `requirements_phase1.txt`

---

## 🔵 OPTION 4: DigitalOcean Droplet ($4/month - 20 MINUTES)

### Step 1: Create Droplet
1. Go to https://digitalocean.com
2. Create account
3. Click "Create" → "Droplets"
4. Choose:
   - Image: Ubuntu 22.04
   - Plan: Basic ($4/month)
   - Region: Closest to you
5. Add SSH key or use password
6. Click "Create Droplet"

### Step 2: SSH Into Droplet
```bash
ssh root@YOUR_DROPLET_IP
```

### Step 3: Install Dependencies
```bash
# Update system
apt update && apt upgrade -y

# Install Python and Git
apt install -y python3 python3-pip git

# Clone repository
cd /opt
git clone YOUR_REPO_URL tps19
cd tps19

# Install dependencies
bash install_phase1_dependencies.sh
```

### Step 4: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

### Step 5: Run Bot
```bash
# Test run
python3 tps19_main.py

# Run in background (tmux)
apt install -y tmux
tmux new -s tps19
python3 tps19_main.py
# Press Ctrl+B, then D to detach

# Or use systemd service
cp services/tps19_main.service /etc/systemd/system/
systemctl enable tps19_main
systemctl start tps19_main
systemctl status tps19_main
```

### Cost:
- $4/month (basic droplet)
- $6/month (1GB RAM - recommended)

---

## ⚙️ ENVIRONMENT VARIABLES SETUP

For ALL platforms, you need these environment variables:

### Required:
```
EXCHANGE_API_KEY=your_crypto_com_api_key
EXCHANGE_API_SECRET=your_crypto_com_secret
DATABASE_URL=<auto-provided-by-platform>
```

### Optional:
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
GOOGLE_SHEETS_CREDENTIALS_PATH=/app/config/google_credentials.json
REDIS_URL=<auto-provided-or-manual>
```

---

## 🧪 TESTING YOUR DEPLOYMENT

### Check if bot is running:
```bash
# Railway/Render: Check logs in dashboard

# Fly.io:
fly logs

# DigitalOcean:
systemctl status tps19_main
tail -f logs/main.log
```

### Test functionality:
1. Check logs for startup messages
2. Verify database connection
3. Confirm exchange API connection
4. Monitor for trades (if enabled)

---

## 🆘 TROUBLESHOOTING

### Bot crashes on startup:
1. Check logs for error messages
2. Verify environment variables are set
3. Ensure API keys are valid
4. Check database connection

### Dependencies not installing:
1. Verify `requirements_phase1.txt` exists
2. Check Python version (need 3.9+)
3. Try manual install: `pip install -r requirements_phase1.txt`

### Can't connect to exchange:
1. Verify API keys are correct
2. Check API key permissions (trading enabled)
3. Verify IP whitelist (if using)
4. Check exchange API status

---

## 📊 MONITORING

### Railway:
- Dashboard shows CPU/Memory usage
- Built-in logs viewer
- Metrics tab for performance

### Render:
- Logs tab shows real-time logs
- Metrics for resource usage
- Alerts for failures

### Fly.io:
```bash
fly status
fly logs
fly ssh console
```

### DigitalOcean:
```bash
systemctl status tps19_main
tail -f /opt/tps19/logs/main.log
htop  # Check resource usage
```

---

## 🎯 WHICH PLATFORM SHOULD I CHOOSE?

**Choose Railway if:**
- ✅ You want the absolute easiest setup
- ✅ 5 minutes is your goal
- ✅ You're okay with $5-10/month

**Choose Render if:**
- ✅ You want free (with limitations)
- ✅ You don't need 24/7 always-on
- ✅ Or willing to pay $7/month for always-on

**Choose Fly.io if:**
- ✅ You want free 24/7
- ✅ You're comfortable with CLI
- ✅ You want global deployment

**Choose DigitalOcean if:**
- ✅ You want full control
- ✅ $4-6/month is acceptable
- ✅ You're comfortable with Linux

---

## ✅ READY TO DEPLOY?

All configuration files are ready:
- ✅ `railway.json` - Railway configuration
- ✅ `render.yaml` - Render configuration
- ✅ `Dockerfile` - Docker/Fly.io configuration
- ✅ `fly.toml` - Fly.io configuration
- ✅ `.env.example` - Environment variables template

**Just choose your platform and follow the steps above!**
