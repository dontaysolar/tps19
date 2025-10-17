# 🚀 TPS19 - Google Cloud Platform Deployment Guide

## ✅ EXCELLENT CHOICE!

**Google Cloud is PERFECT for TPS19 because:**
- 💰 **$300 FREE CREDIT** for 90 days (covers ~3-6 months)
- 🚀 **Cloud Run** = Serverless containers (no VM management)
- 📊 **Cloud SQL** = Managed PostgreSQL
- 🔐 **Secret Manager** = Secure API key storage
- 📈 **Monitoring** = Built-in logging & metrics
- 🌍 **Global** = Deploy anywhere

---

## 📋 STEP-BY-STEP DEPLOYMENT

### **PHASE 1: Google Cloud Setup (5 minutes)**

#### Step 1.1: Activate Free Trial
1. Go to https://console.cloud.google.com
2. Sign in with Google account
3. Click "Activate" on the $300 free trial banner
4. Enter payment info (won't be charged during trial)
5. ✅ **You now have $300 credit for 90 days!**

#### Step 1.2: Create Project
1. Click project dropdown (top left)
2. Click "New Project"
3. Name: `tps19-trading-bot`
4. Click "Create"
5. Wait for project to be created
6. Select the new project

#### Step 1.3: Enable Required APIs
```bash
# Click "Enable APIs and Services" or run in Cloud Shell:
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  sql-component.googleapis.com \
  secretmanager.googleapis.com
```

---

### **PHASE 2: Install Google Cloud CLI (Optional - Can use Cloud Shell)**

#### Option A: Use Cloud Shell (Easiest)
1. Click the terminal icon (top right) in Google Cloud Console
2. Cloud Shell opens with `gcloud` pre-installed
3. Skip to Phase 3!

#### Option B: Install Locally (If you want local control)

**On Linux/Mac:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

**On Windows:**
1. Download: https://cloud.google.com/sdk/docs/install
2. Run installer
3. Open "Google Cloud SDK Shell"
4. Run: `gcloud init`

#### Authenticate:
```bash
gcloud auth login
gcloud config set project tps19-trading-bot
```

---

### **PHASE 3: Deploy to Google Cloud Run (10 minutes)**

#### Step 3.1: Upload Your Code

**Option A: Use Git (Recommended)**
```bash
# In Cloud Shell or local terminal:
git clone YOUR_REPOSITORY_URL
cd YOUR_REPOSITORY_NAME
```

**Option B: Upload Files**
1. In Cloud Shell, click "⋮" → "Upload file"
2. Upload all TPS19 files
3. Or create tarball and upload:
```bash
# On your local machine:
tar -czf tps19.tar.gz /workspace/*
# Upload tps19.tar.gz to Cloud Shell
# In Cloud Shell:
tar -xzf tps19.tar.gz
```

#### Step 3.2: Build and Deploy
```bash
# Set your project ID
export PROJECT_ID=tps19-trading-bot
gcloud config set project $PROJECT_ID

# Build the Docker image
gcloud builds submit --tag gcr.io/$PROJECT_ID/tps19-trading-bot

# Deploy to Cloud Run
gcloud run deploy tps19-trading-bot \
  --image gcr.io/$PROJECT_ID/tps19-trading-bot \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 1 \
  --min-instances 1 \
  --allow-unauthenticated
```

#### Step 3.3: Set Environment Variables
```bash
# Set your exchange API keys (DO THIS!)
gcloud run services update tps19-trading-bot \
  --region us-central1 \
  --set-env-vars "EXCHANGE_API_KEY=YOUR_CRYPTO_COM_API_KEY" \
  --set-env-vars "EXCHANGE_API_SECRET=YOUR_CRYPTO_COM_SECRET" \
  --set-env-vars "TPS19_ENV=production"
```

**Or use Secret Manager (More Secure):**
```bash
# Create secrets
echo -n "YOUR_API_KEY" | gcloud secrets create exchange-api-key --data-file=-
echo -n "YOUR_API_SECRET" | gcloud secrets create exchange-api-secret --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding exchange-api-key \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

# Update Cloud Run to use secrets
gcloud run services update tps19-trading-bot \
  --region us-central1 \
  --set-secrets "EXCHANGE_API_KEY=exchange-api-key:latest" \
  --set-secrets "EXCHANGE_API_SECRET=exchange-api-secret:latest"
```

---

### **PHASE 4: Setup Cloud SQL Database (Optional - 5 minutes)**

#### Step 4.1: Create PostgreSQL Instance
```bash
gcloud sql instances create tps19-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1
```

#### Step 4.2: Create Database
```bash
gcloud sql databases create tps19_production \
  --instance=tps19-db
```

#### Step 4.3: Connect Cloud Run to Cloud SQL
```bash
# Get connection name
gcloud sql instances describe tps19-db --format="value(connectionName)"

# Update Cloud Run with Cloud SQL connection
gcloud run services update tps19-trading-bot \
  --region us-central1 \
  --add-cloudsql-instances CONNECTION_NAME_FROM_ABOVE
```

---

### **PHASE 5: Monitor Your Bot (Ongoing)**

#### Check Logs:
```bash
# Real-time logs
gcloud run services logs tail tps19-trading-bot --region us-central1

# Or in Console:
# Navigation Menu → Cloud Run → tps19-trading-bot → Logs
```

#### Check Status:
```bash
gcloud run services describe tps19-trading-bot --region us-central1
```

#### View Metrics:
1. Go to Cloud Console
2. Navigation Menu → Cloud Run → tps19-trading-bot
3. Click "Metrics" tab
4. See CPU, Memory, Request count, etc.

---

## 💰 COST BREAKDOWN

### **During Free Trial (90 days):**
- **Cost:** $0 (uses your $300 credit)
- **Credit Usage:** ~$10-30/month
- **Remaining:** ~$270-290 after first month

### **After Free Trial:**

**Cloud Run:**
- First 2 million requests: FREE
- CPU: $0.00002400/vCPU-second
- Memory: $0.00000250/GiB-second
- **Estimate:** $10-20/month for 24/7 operation

**Cloud SQL (if used):**
- db-f1-micro: $7.67/month
- Storage: $0.17/GB/month
- **Estimate:** $8-10/month

**Total Monthly Cost After Trial:** $18-30/month

### **Free Tier (Always Free):**
- 2 million Cloud Run requests/month
- 360,000 vCPU-seconds/month
- 180,000 GiB-seconds/month
- **Your bot might fit in free tier!**

---

## 🎯 QUICK COMMANDS REFERENCE

### Deploy/Update:
```bash
# Build and deploy in one command
gcloud builds submit --tag gcr.io/PROJECT_ID/tps19-trading-bot && \
gcloud run deploy tps19-trading-bot \
  --image gcr.io/PROJECT_ID/tps19-trading-bot \
  --region us-central1
```

### View Logs:
```bash
gcloud run services logs tail tps19-trading-bot --region us-central1
```

### Update Environment Variables:
```bash
gcloud run services update tps19-trading-bot \
  --region us-central1 \
  --set-env-vars "KEY=VALUE"
```

### Stop Bot (Save Money):
```bash
gcloud run services update tps19-trading-bot \
  --region us-central1 \
  --min-instances 0
```

### Start Bot:
```bash
gcloud run services update tps19-trading-bot \
  --region us-central1 \
  --min-instances 1
```

### Delete Everything:
```bash
gcloud run services delete tps19-trading-bot --region us-central1
gcloud sql instances delete tps19-db
gcloud container images delete gcr.io/PROJECT_ID/tps19-trading-bot
```

---

## 🔧 CONFIGURATION FILES CREATED

All ready for you:
- ✅ `Dockerfile.cloudrun` - Optimized for Cloud Run
- ✅ `cloudbuild.yaml` - Automated build configuration
- ✅ `app.yaml` - Alternative App Engine config
- ✅ `.dockerignore` - Optimize build size
- ✅ `.env.example` - Environment variables template

---

## 🆘 TROUBLESHOOTING

### Bot crashes on startup:
```bash
# Check logs
gcloud run services logs tail tps19-trading-bot --region us-central1

# Check deployment status
gcloud run services describe tps19-trading-bot --region us-central1
```

### Can't connect to database:
```bash
# Verify Cloud SQL connection name is correct
gcloud sql instances describe tps19-db --format="value(connectionName)"

# Make sure Cloud Run has connection configured
gcloud run services describe tps19-trading-bot --region us-central1 \
  --format="value(spec.template.spec.containers[0].volumeMounts)"
```

### Out of memory:
```bash
# Increase memory to 4GB
gcloud run services update tps19-trading-bot \
  --region us-central1 \
  --memory 4Gi
```

### Need more CPU:
```bash
# Increase to 4 CPUs
gcloud run services update tps19-trading-bot \
  --region us-central1 \
  --cpu 4
```

---

## ✅ VERIFICATION CHECKLIST

After deployment, verify:
- [ ] Cloud Run service shows "Healthy" status
- [ ] Logs show TPS19 startup messages
- [ ] No error messages in logs
- [ ] Environment variables are set correctly
- [ ] Exchange API connection works
- [ ] Database connection works (if using Cloud SQL)
- [ ] Bot is making trading decisions (check logs)

---

## 🎉 SUCCESS!

Your TPS19 bot is now running 24/7 on Google Cloud!

**What's Happening:**
- ✅ Container runs continuously (min-instances=1)
- ✅ Auto-restarts on crashes
- ✅ Scales if needed
- ✅ Monitored by Google
- ✅ Using your $300 free credit

**Next Steps:**
1. Monitor logs regularly
2. Check trading performance
3. Adjust parameters as needed
4. Monitor your free credit usage

**Credit Dashboard:**
https://console.cloud.google.com/billing

---

## 📚 Additional Resources

- Cloud Run Docs: https://cloud.google.com/run/docs
- Cloud SQL Docs: https://cloud.google.com/sql/docs
- Secret Manager: https://cloud.google.com/secret-manager/docs
- Pricing Calculator: https://cloud.google.com/products/calculator

---

**Your bot is live! 🚀**
