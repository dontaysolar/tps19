# 🚀 Deploy TPS19 Dashboard to Your Vercel Project

**Your Project ID:** `prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz`

---

## ⚡ QUICK DEPLOY (Recommended)

### Option 1: Automated Script

```bash
# Make script executable
chmod +x deploy-to-vercel.sh

# Run deployment
./deploy-to-vercel.sh
```

This script will:
1. ✅ Check you're in the right directory
2. ✅ Install dependencies
3. ✅ Build the project
4. ✅ Deploy to your specific Vercel project
5. ✅ Show you the deployment URL

---

### Option 2: Manual Deploy

```bash
# Navigate to dashboard
cd dashboard

# Install dependencies
npm install

# Build (test locally)
npm run build

# Deploy to your project
vercel --prod --project-id="prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz"
```

---

### Option 3: Via Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Find project: `prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz`
3. Go to **Deployments** tab
4. Click **"Redeploy"** button
5. Wait for build to complete

---

## ⚙️ CONFIGURE YOUR PROJECT

### Step 1: Set Root Directory

In Vercel Dashboard:

1. Go to your project
2. **Settings** → **General**
3. **Root Directory:** `dashboard`
4. Click **Save**

### Step 2: Add Environment Variables

1. **Settings** → **Environment Variables**
2. Add these:

```bash
# Required
NEXT_PUBLIC_API_URL=https://your-app.vercel.app
NEXT_PUBLIC_WS_URL=https://your-api-server.com
ORGANISM_API_URL=https://your-api-server.com
```

Replace `your-api-server.com` with your actual API server URL (Railway, Render, etc.)

### Step 3: Verify Build Settings

**Settings** → **General** → **Build & Development Settings**

```
Framework Preset: Next.js
Build Command: npm run build
Output Directory: .next
Install Command: npm install
Development Command: npm run dev
Node.js Version: 18.x
```

---

## 🧪 TEST BEFORE DEPLOYING

Always test locally first:

```bash
cd dashboard

# Install
npm install

# Build
npm run build

# Test production build
npm start

# Should work on http://localhost:3000
```

If it works locally, it will work on Vercel!

---

## 📊 CHECK DEPLOYMENT STATUS

### Via CLI:

```bash
# List recent deployments
vercel ls --project-id="prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz"

# View logs
vercel logs --project-id="prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz"
```

### Via Dashboard:

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on your project
3. View **Deployments** tab
4. Click latest deployment to see:
   - ✅ Build logs
   - ✅ Function logs
   - ✅ Deployment URL
   - ✅ Environment details

---

## 🔍 TROUBLESHOOTING

### Build Fails

```bash
# Clear everything and start fresh
cd dashboard
rm -rf node_modules package-lock.json .next
npm install
npm run build
vercel --prod --project-id="prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz"
```

### Still Getting 404

1. **Check Root Directory:**
   - Settings → General → Root Directory = `dashboard`

2. **Check Build Output:**
   - Deployments → Latest → Build Logs
   - Look for errors

3. **Verify Files Exist:**
   ```bash
   ls dashboard/src/app/page.tsx
   ls dashboard/src/app/layout.tsx
   # Should both exist
   ```

4. **Test Health Endpoint:**
   ```bash
   # After deployment
   curl https://your-app.vercel.app/api/health
   # Should return: {"status":"ok",...}
   ```

### Environment Variables Not Working

1. Go to Settings → Environment Variables
2. Make sure variables are set for **Production**
3. After adding variables, **redeploy**:
   ```bash
   vercel --prod --project-id="prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz"
   ```

---

## 🎯 EXPECTED RESULT

After successful deployment, you should see:

```
✅ Build completed
✅ Deployment ready
✅ https://your-app.vercel.app

Production: https://your-app.vercel.app [ready]
```

Then when you visit your URL:

1. ✅ Dashboard loads (no 404)
2. ✅ Shows "Connected" or "Disconnected" status
3. ✅ Components render correctly
4. ✅ `/api/health` returns `{"status": "ok"}`

---

## 🔐 LINK API SERVER

If your API server is deployed:

### Railway Example:

```bash
# Get your Railway URL
railway domain

# Add to Vercel environment variables:
# NEXT_PUBLIC_WS_URL=https://your-app.railway.app
# ORGANISM_API_URL=https://your-app.railway.app
```

### Render Example:

```bash
# Your Render URL (from dashboard)
# Add to Vercel:
# NEXT_PUBLIC_WS_URL=https://your-api.onrender.com
# ORGANISM_API_URL=https://your-api.onrender.com
```

---

## 📝 QUICK REFERENCE

### Your Project Details

```
Project ID: prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz
Framework: Next.js 14
Root Directory: dashboard
```

### Useful Commands

```bash
# Deploy
vercel --prod --project-id="prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz"

# View logs
vercel logs --project-id="prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz"

# List deployments
vercel ls --project-id="prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz"

# Remove deployment
vercel rm [deployment-url] --yes
```

### Important URLs

```
Dashboard: https://vercel.com/dashboard
Your Project: https://vercel.com/dashboard/prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz
Docs: https://vercel.com/docs
```

---

## ✅ DEPLOYMENT CHECKLIST

Before deploying:

- [ ] `npm install` works
- [ ] `npm run build` succeeds
- [ ] `npm start` shows dashboard locally
- [ ] Root directory set to `dashboard`
- [ ] Environment variables configured
- [ ] API server is deployed (or will use mock data)

After deploying:

- [ ] Build succeeded (green checkmark)
- [ ] No 404 error on homepage
- [ ] `/api/health` returns 200 OK
- [ ] Dashboard components render
- [ ] Check browser console for errors

---

## 🆘 NEED HELP?

If deployment fails:

1. **Check Build Logs:**
   - Vercel Dashboard → Deployments → Latest → Logs

2. **Run Script with Debug:**
   ```bash
   bash -x deploy-to-vercel.sh
   ```

3. **Manual Deploy Step-by-Step:**
   ```bash
   cd dashboard
   rm -rf node_modules .next
   npm install
   npm run build
   npm start  # Test locally first
   vercel --prod --project-id="prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz"
   ```

4. **View Detailed Logs:**
   ```bash
   vercel logs --follow --project-id="prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz"
   ```

---

## 🎉 SUCCESS!

Once deployed successfully:

```
✅ Dashboard live at: https://your-app.vercel.app
✅ API routes working: /api/health
✅ Real-time monitoring: WebSocket connected
✅ All components rendering
```

**Enjoy your TPS19 APEX Dashboard!** 🧬📊

---

**Project ID:** `prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz`  
**Status:** Ready to deploy ✅
