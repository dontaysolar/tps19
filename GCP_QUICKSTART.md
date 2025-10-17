# ⚡ Google Cloud Platform - 5-Minute Quickstart

## 🎯 FASTEST PATH TO DEPLOYMENT

### **Prerequisites:**
- ✅ Google account
- ✅ Credit card (for $300 free trial - won't be charged)
- ✅ This TPS19 code

---

## 🚀 DEPLOY IN 5 STEPS

### **STEP 1: Activate Free Trial (2 minutes)**
1. Go to https://console.cloud.google.com
2. Click "Activate" on $300 free trial banner
3. Enter payment info
4. ✅ **You now have $300 credit!**

### **STEP 2: Create Project (30 seconds)**
1. Click project dropdown (top left)
2. Click "New Project"
3. Name: `tps19-trading-bot`
4. Click "Create"

### **STEP 3: Open Cloud Shell (10 seconds)**
1. Click terminal icon (top right): `>_`
2. Cloud Shell opens in browser
3. ✅ **`gcloud` is pre-installed!**

### **STEP 4: Upload & Deploy (2 minutes)**

**In Cloud Shell, run these commands:**

```bash
# Clone your repository (replace with your actual repo)
git clone https://github.com/YOUR_USERNAME/tps19.git
cd tps19

# Or upload files directly:
# Click ⋮ → Upload → Select all TPS19 files

# Deploy (ONE COMMAND!)
gcloud builds submit --tag gcr.io/tps19-trading-bot/tps19-trading-bot && \
gcloud run deploy tps19-trading-bot \
  --image gcr.io/tps19-trading-bot/tps19-trading-bot \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 1 \
  --allow-unauthenticated
```

### **STEP 5: Add Your API Keys (1 minute)**

```bash
# Set your Crypto.com API credentials
gcloud run services update tps19-trading-bot \
  --region us-central1 \
  --set-env-vars "EXCHANGE_API_KEY=YOUR_ACTUAL_API_KEY_HERE" \
  --set-env-vars "EXCHANGE_API_SECRET=YOUR_ACTUAL_SECRET_HERE"
```

---

## ✅ DONE! Your bot is running!

**Check it's working:**
```bash
# View real-time logs
gcloud run services logs tail tps19-trading-bot --region us-central1
```

**You should see:**
```
🚀 Starting TPS19 Definitive Unified System...
✅ Phase 1 AI/ML modules imported successfully
✅ SIUL initialized
✅ Trading engine started
💓 TPS19 Unified System running...
```

---

## 📊 Monitor Your Bot

### **View Logs (Real-time):**
```bash
gcloud run services logs tail tps19-trading-bot --region us-central1 --follow
```

### **Check Status:**
```bash
gcloud run services describe tps19-trading-bot --region us-central1
```

### **View in Console:**
https://console.cloud.google.com/run

---

## 🛠️ Common Tasks

### **Update Code:**
```bash
# Pull latest changes
git pull

# Rebuild and redeploy
gcloud builds submit --tag gcr.io/tps19-trading-bot/tps19-trading-bot
gcloud run services update tps19-trading-bot \
  --image gcr.io/tps19-trading-bot/tps19-trading-bot \
  --region us-central1
```

### **Stop Bot (Save Money):**
```bash
gcloud run services update tps19-trading-bot \
  --region us-central1 \
  --min-instances 0
```

### **Start Bot:**
```bash
gcloud run services update tps19-trading-bot \
  --region us-central1 \
  --min-instances 1
```

### **Change Memory/CPU:**
```bash
# Increase to 4GB RAM, 4 CPUs
gcloud run services update tps19-trading-bot \
  --region us-central1 \
  --memory 4Gi \
  --cpu 4
```

---

## 💰 Cost Tracking

**Monitor your free credit:**
1. Go to https://console.cloud.google.com/billing
2. Click "Reports"
3. See credit usage

**Expected usage:**
- First month: ~$10-20 of credit
- Remaining: $280-290 for next 2-3 months

---

## 🆘 Need Help?

**Bot not starting?**
```bash
gcloud run services logs tail tps19-trading-bot --region us-central1
# Look for error messages
```

**Can't find project?**
```bash
gcloud projects list
gcloud config set project tps19-trading-bot
```

**Need to delete everything?**
```bash
gcloud run services delete tps19-trading-bot --region us-central1
gcloud projects delete tps19-trading-bot
```

---

## ✅ THAT'S IT!

Your TPS19 crypto trading bot is now running 24/7 on Google Cloud Platform using your $300 free credit!

**No VM needed. No server management. Just works.** 🎉
