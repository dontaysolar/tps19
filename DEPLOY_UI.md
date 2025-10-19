# 🚀 TPS19 - WEB UI DEPLOYMENT GUIDE

**Two options: Streamlit (EASIEST) or Next.js (Advanced)**

---

## ⚡ OPTION 1: STREAMLIT (RECOMMENDED - 2 MINUTES)

### **What is Streamlit?**
- Python-based web framework
- No JavaScript needed
- Auto-deploys to Streamlit Cloud
- **3Commas-style interface included**

### **Run Locally:**
```bash
cd /workspace
streamlit run streamlit_dashboard.py
```

Opens automatically in browser at: http://localhost:8501

### **Deploy to Cloud (FREE):**

1. **Push to GitHub**
```bash
git add streamlit_dashboard.py
git commit -m "Add Streamlit dashboard"
git push
```

2. **Go to Streamlit Cloud**
- Visit: https://streamlit.io/cloud
- Click "New app"
- Connect GitHub
- Select repository
- Set main file: `streamlit_dashboard.py`
- Click "Deploy"

3. **Done!**
You'll get a URL like: `https://your-app.streamlit.app`

**Total time: 2 minutes**

---

## 🚀 OPTION 2: NEXT.JS + VERCEL (Advanced)

### **What is Next.js?**
- React-based framework
- Professional UI
- Highly customizable
- Deploy to Vercel

### **Run Locally:**
```bash
cd /workspace/web-dashboard
npm install
npm run dev
```

Opens at: http://localhost:3000

### **Deploy to Vercel:**

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Deploy**
```bash
cd /workspace/web-dashboard
vercel
```

3. **Follow prompts**
- Link to existing project: No
- Project name: tps19-dashboard
- Deploy!

**Total time: 5 minutes**

---

## 📊 COMPARISON

| Feature | Streamlit | Next.js |
|---------|-----------|---------|
| **Ease** | ⭐⭐⭐⭐⭐ Easy | ⭐⭐⭐ Moderate |
| **Speed** | ⭐⭐⭐⭐⭐ 2 min | ⭐⭐⭐ 5 min |
| **Language** | Python only | JS + Python |
| **Customization** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Deployment** | ⭐⭐⭐⭐⭐ Click deploy | ⭐⭐⭐⭐ Easy |
| **Cost** | FREE | FREE |

**Recommendation:** Start with Streamlit, upgrade to Next.js later if needed.

---

## 🎯 STREAMLIT QUICKSTART

### **1. Install (if needed)**
```bash
pip3 install streamlit
```

### **2. Run**
```bash
streamlit run streamlit_dashboard.py
```

### **3. Deploy**
```bash
# Push to Git
git push

# Go to streamlit.io/cloud
# Click "New app"
# Select your repo
# Deploy!
```

**That's it!**

---

## 🎨 WHAT YOU GET

### **Streamlit Dashboard Includes:**

**📊 Dashboard Page:**
- Total profit/loss metrics
- Trade count and win rate
- Active positions count
- Quick action buttons
- Performance chart
- Recent activity feed
- System health monitoring
- Live signal updates

**🤖 Bots Page:**
- All active bots
- Start/pause controls
- Performance metrics per bot
- Trade counts
- Profit tracking

**💼 Positions Page:**
- All open positions
- Real-time P&L
- Entry vs current prices
- Quick close buttons

**📜 History Page:**
- Complete trade history
- Filterable table
- Export to CSV
- Performance analytics

**📈 Analytics Page:**
- Sharpe ratio
- Max drawdown
- Profit factor
- Strategy performance breakdown
- Win rate by strategy

**⚙️ Settings Page:**
- API configuration
- Risk settings sliders
- Trading pairs selection
- System preferences toggles

---

## 🔧 CONNECT BACKEND

### **Start API Server:**
```bash
# Terminal 1: API
python3 api_server.py

# Terminal 2: Dashboard
streamlit run streamlit_dashboard.py
```

### **Or Combined:**
```bash
# Start both
python3 api_server.py &
streamlit run streamlit_dashboard.py
```

---

## 🌐 DEPLOY TO STREAMLIT CLOUD

### **Step-by-Step:**

1. **Create Streamlit Account**
   - Go to: https://streamlit.io
   - Sign up with GitHub
   - Free forever for public apps

2. **Deploy App**
   - Click "New app"
   - Choose repository
   - Branch: `cursor/update-api-credentials-for-live-trading-1399` (or your main branch)
   - Main file path: `streamlit_dashboard.py`
   - Click "Deploy"

3. **Wait 2 Minutes**
   - Streamlit builds and deploys
   - You get a public URL
   - Share with anyone!

4. **Done!**
   - Your dashboard is live
   - Auto-updates when you push to Git
   - Free hosting
   - HTTPS included

---

## 📱 FEATURES

### **Responsive Design:**
- ✅ Desktop
- ✅ Tablet
- ✅ Mobile

### **Real-time Updates:**
- Auto-refreshes data
- Live system metrics
- Current positions
- Latest trades

### **Interactive:**
- Start/stop bots
- Close positions
- Configure settings
- Export data

---

## 🎯 RECOMMENDED APPROACH

**For fastest deployment:**

```bash
# 1. Install Streamlit
pip3 install streamlit

# 2. Test locally
streamlit run streamlit_dashboard.py

# 3. Push to Git
git add streamlit_dashboard.py
git commit -m "Add Streamlit dashboard"
git push

# 4. Deploy on streamlit.io
# Go to streamlit.io/cloud
# Click deploy
# Done!
```

**Total time: Under 5 minutes**

---

## 🆘 TROUBLESHOOTING

### **"streamlit: command not found"**
```bash
pip3 install streamlit
# Or
pip install streamlit
```

### **Port already in use**
```bash
streamlit run streamlit_dashboard.py --server.port 8502
```

### **Can't connect to backend**
- Make sure `api_server.py` is running
- Check `http://localhost:8000/api/status`

---

## ✅ SUMMARY

**Streamlit = Easiest:**
- Python only
- 2-minute deployment
- Free hosting
- Auto-updates
- Professional UI

**Next.js = Most Powerful:**
- Full customization
- React ecosystem
- Production-grade
- Vercel deployment

**Both are ready to use!**

---

**Start with:** `streamlit run streamlit_dashboard.py`

*TPS19 v19.0*
