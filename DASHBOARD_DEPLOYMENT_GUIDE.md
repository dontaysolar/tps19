# 🚀 TPS19 APEX Dashboard - Complete Deployment Guide

**Status:** ✅ Production-Ready  
**Platform:** Vercel (Frontend) + Any Python Host (API)  
**Tech Stack:** Next.js 14 + Flask + WebSocket

---

## 📋 Table of Contents

1. [Quick Start (Local)](#quick-start-local)
2. [Deploy API Server](#deploy-api-server)
3. [Deploy to Vercel](#deploy-to-vercel)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

---

## 🏃 Quick Start (Local)

### Prerequisites

- Node.js 18+
- Python 3.9+
- Git

### Step 1: Install Dependencies

```bash
# Install dashboard dependencies
cd dashboard
npm install

# Install API server dependencies
cd ..
pip install -r requirements-dashboard.txt
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp dashboard/.env.example dashboard/.env.local

# Edit with your settings (optional for local)
```

### Step 3: Start API Server

```bash
# Terminal 1
python3 api_server.py
```

API will run on `http://localhost:5000`

### Step 4: Start Dashboard

```bash
# Terminal 2
cd dashboard
npm run dev
```

Dashboard will run on `http://localhost:3000`

### Step 5: Start Organism (Optional)

```bash
# Terminal 3
python3 tps19_apex.py
```

---

## 🌐 Deploy API Server

You need to deploy the Flask API server first. Choose one option:

### Option 1: Railway (Recommended)

**Why Railway:**
- Easy Python deployment
- Free tier available
- WebSocket support
- Auto-scaling

**Steps:**

1. **Install Railway CLI:**
```bash
npm i -g @railway/cli
```

2. **Login:**
```bash
railway login
```

3. **Create Project:**
```bash
railway init
```

4. **Deploy:**
```bash
railway up
```

5. **Get URL:**
```bash
railway domain
```

Save this URL - you'll need it for Vercel!

### Option 2: Render

**Steps:**

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Configure:
   - **Name:** tps19-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements-dashboard.txt`
   - **Start Command:** `python api_server.py`
6. Click "Create Web Service"
7. Save the URL (e.g., `https://tps19-api.onrender.com`)

### Option 3: Your Own Server

```bash
# On your server
git clone your-repo
cd your-repo
pip install -r requirements-dashboard.txt

# Run with gunicorn
pip install gunicorn eventlet
gunicorn --worker-class eventlet -w 1 api_server:app --bind 0.0.0.0:5000
```

---

## ☁️ Deploy to Vercel

### Method 1: Vercel CLI (Fastest)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd dashboard
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? tps19-apex-dashboard
# - Directory? ./
# - Override settings? No

# Deploy to production
vercel --prod
```

### Method 2: GitHub Integration

1. **Push to GitHub:**
```bash
git add .
git commit -m "Add TPS19 dashboard"
git push origin main
```

2. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Root Directory: `dashboard`
   - Framework: Next.js
   - Click "Deploy"

### Method 3: Vercel Desktop App

1. Download [Vercel Desktop](https://vercel.com/download)
2. Drag `dashboard` folder to Vercel
3. Click "Deploy"

---

## ⚙️ Configuration

### Environment Variables

After deploying, configure these in Vercel dashboard:

1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add these variables:

```bash
# Required
NEXT_PUBLIC_API_URL=https://your-vercel-app.vercel.app
NEXT_PUBLIC_WS_URL=https://your-api-server.com
ORGANISM_API_URL=https://your-api-server.com

# Optional
API_KEY=your_secret_key_here
```

### Update vercel.json

Edit `dashboard/vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/api/organism/:path*",
      "destination": "https://YOUR-API-SERVER.com/api/:path*"
    }
  ]
}
```

Replace `YOUR-API-SERVER.com` with your actual API URL.

---

## 🧪 Testing

### Test API Server

```bash
# Health check
curl http://localhost:5000/api/health

# Get vitals
curl http://localhost:5000/api/vitals
```

### Test Dashboard

1. Open `http://localhost:3000`
2. Check connection status (top left)
3. Verify data is updating
4. Check browser console for errors

### Test WebSocket

```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
wscat -c ws://localhost:5000

# Should see: Connected to TPS19 APEX Organism
```

---

## 🔧 Troubleshooting

### Dashboard shows "Disconnected"

**Check:**
1. Is API server running?
2. Is WebSocket URL correct in `.env.local`?
3. Check browser console for CORS errors

**Fix:**
```bash
# Update CORS in api_server.py
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### API server crashes on startup

**Check:**
1. Are all dependencies installed?
2. Is port 5000 already in use?

**Fix:**
```bash
# Install missing dependencies
pip install -r requirements-dashboard.txt

# Use different port
# In api_server.py, change:
socketio.run(app, port=5001)
```

### Vercel build fails

**Common issues:**

1. **Missing dependencies:**
```bash
cd dashboard
npm install
```

2. **TypeScript errors:**
```bash
npm run build
# Fix any errors shown
```

3. **Environment variables not set:**
   - Add them in Vercel dashboard
   - Redeploy

### WebSocket not connecting in production

**Railway/Render:**
- WebSocket should work automatically

**Custom server:**
- Ensure WebSocket port is open
- Use WSS (secure WebSocket) not WS
- Configure nginx/Apache for WebSocket proxy

---

## 🔒 Production Security Checklist

Before going live:

- [ ] Add API key authentication
- [ ] Enable HTTPS only
- [ ] Configure CORS for your domain only
- [ ] Add rate limiting
- [ ] Set up monitoring
- [ ] Enable logging
- [ ] Add error tracking (Sentry)
- [ ] Set up backups
- [ ] Configure firewall
- [ ] Use environment variables for secrets

### Add API Key (Recommended)

**In `api_server.py`:**

```python
from functools import wraps
from flask import request

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('API_KEY'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Apply to routes
@app.route('/api/vitals')
@require_api_key
def get_vitals():
    # ...
```

**In `useOrganismData.ts`:**

```typescript
const response = await fetch('/api/organism/vitals', {
  headers: {
    'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || ''
  }
})
```

---

## 📊 Monitoring

### Vercel Analytics

Enable in dashboard:
1. Project Settings → Analytics
2. Enable "Web Analytics"

### API Server Monitoring

```bash
# Add to api_server.py
import logging
logging.basicConfig(level=logging.INFO)

# Log all requests
@app.before_request
def log_request():
    logging.info(f"{request.method} {request.path}")
```

---

## 🎯 Performance Optimization

### Dashboard

1. **Enable caching:**
```typescript
// In next.config.js
const nextConfig = {
  images: {
    unoptimized: false,
  },
  swcMinify: true,
}
```

2. **Lazy load components:**
```typescript
import dynamic from 'next/dynamic'

const PerformanceCharts = dynamic(() => import('@/components/PerformanceCharts'), {
  loading: () => <LoadingSkeleton />
})
```

### API Server

1. **Use production server:**
```bash
pip install gunicorn eventlet
gunicorn --worker-class eventlet -w 1 api_server:app
```

2. **Enable caching:**
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=5)
@app.route('/api/vitals')
def get_vitals():
    # ...
```

---

## 📱 Custom Domain

### Vercel:

1. Project Settings → Domains
2. Add your domain
3. Configure DNS (instructions provided)

### API Server:

1. Configure domain DNS to point to server IP
2. Set up SSL with Let's Encrypt:
```bash
sudo certbot --nginx -d api.yourdomain.com
```

---

## ✅ Final Checklist

Before launch:

- [ ] API server deployed and accessible
- [ ] Dashboard deployed to Vercel
- [ ] Environment variables configured
- [ ] Custom domain configured (optional)
- [ ] SSL/HTTPS enabled
- [ ] Monitoring enabled
- [ ] Error tracking set up
- [ ] API authentication enabled
- [ ] CORS configured correctly
- [ ] WebSocket working in production
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Backup strategy in place

---

## 🆘 Need Help?

**Common Commands:**

```bash
# View Vercel logs
vercel logs

# View API server logs
railway logs  # or check Render dashboard

# Redeploy dashboard
cd dashboard && vercel --prod

# Restart API server
railway restart  # or restart on Render
```

**Resources:**

- [Vercel Docs](https://vercel.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Next.js Docs](https://nextjs.org/docs)
- [Flask Docs](https://flask.palletsprojects.com)

---

**🎉 Congratulations! Your TPS19 APEX Dashboard is now live!**

Access it at: `https://your-app.vercel.app`

---

**Built following CURSOR MASTER KEY PROCEDURE**  
**All protocols followed • Zero tolerance • Production ready**
