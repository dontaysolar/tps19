# 🚀 TPS19 ONE-PASTE DEPLOYMENT GUIDE

## 📋 OVERVIEW

You need to do 2 things:
1. Push code to GitHub (from your local machine)
2. Run one script on your VM

---

## PART 1: PUSH TO GITHUB (On your local machine - 2 minutes)

### **Open terminal on your LOCAL machine (where Cursor is):**

```bash
cd /workspace

# Initialize git if needed
git init

# Add all files
git add .

# Commit
git commit -m "TPS19 trading bot ready for deployment"

# Add GitHub remote (using YOUR username: dontaysolar)
git remote add origin https://github.com/dontaysolar/tps19.git

# Push to GitHub
git push -u origin main
```

### **⚠️ If you get an error "repository not found":**

1. Go to https://github.com/new
2. Repository name: `tps19`
3. Make it **Private** (keep your trading code secret!)
4. **DO NOT** initialize with README
5. Click "Create repository"
6. Run the commands above again

---

## PART 2: ONE-PASTE VM SETUP (On your VM - 10 minutes)

### **1. Connect to your VM:**
- Go to https://console.cloud.google.com/compute/instances
- Click **"SSH"** button next to your VM
- Terminal opens in browser

### **2. Copy and paste this ONE command:**

```bash
curl -sSL https://raw.githubusercontent.com/dontaysolar/tps19/main/auto_deploy_vm.sh | bash
```

### **⚠️ If that doesn't work, use this instead:**

**Copy and paste ALL of this at once:**

```bash
#!/bin/bash
set -e
echo "🚀 Installing TPS19..."

# Update system
sudo apt-get update -qq && sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -yqq

# Install prerequisites
sudo apt-get install -y -qq git python3-pip python3-dev build-essential

# Clone repository
cd ~
rm -rf tps19
git clone https://github.com/dontaysolar/tps19.git
cd tps19

# Upgrade pip
python3 -m pip install --upgrade pip -q

# Install dependencies (takes 5-10 minutes)
echo "⏳ Installing Python packages (this takes ~10 minutes)..."
pip3 install -q numpy pandas scikit-learn tensorflow redis python-dotenv requests
pip3 install -q google-auth google-auth-oauthlib google-api-python-client

# Create directories
mkdir -p data/models data/databases logs config
chmod -R 755 .

# Create config file
cat > .env << 'EOF'
EXCHANGE_API_KEY=YOUR_CRYPTO_COM_API_KEY_HERE
EXCHANGE_API_SECRET=YOUR_CRYPTO_COM_SECRET_HERE
TPS19_ENV=production
TRADING_ENABLED=true
LOG_LEVEL=INFO
EOF

echo ""
echo "✅ INSTALLATION COMPLETE!"
echo ""
echo "📝 NEXT: Edit your API keys:"
echo "   nano .env"
echo ""
echo "🚀 THEN START BOT:"
echo "   python3 tps19_main.py"
```

### **3. Wait for installation to complete (~10 minutes)**

You'll see:
```
🚀 Installing TPS19...
⏳ Installing Python packages (this takes ~10 minutes)...
✅ INSTALLATION COMPLETE!
```

### **4. Add your Crypto.com API keys:**

```bash
nano .env
```

- Change `YOUR_CRYPTO_COM_API_KEY_HERE` to your real API key
- Change `YOUR_CRYPTO_COM_SECRET_HERE` to your real secret
- Press **Ctrl+X**, then **Y**, then **Enter**

### **5. Start the bot:**

```bash
python3 tps19_main.py
```

---

## ✅ DONE!

Your bot is now trading! 🎉

**To run in background (so it keeps running when you close SSH):**

```bash
sudo apt install -y tmux
tmux new -s tps19
python3 tps19_main.py
# Press Ctrl+B, then press D (detach)
# Bot keeps running!

# To check on it later:
tmux attach -t tps19
```

---

## 📊 WHAT'S YOUR VM NAME?

Tell me your VM name and I'll give you the EXACT one-paste command with your VM name already filled in!

Look here: https://console.cloud.google.com/compute/instances

(It's probably something like `instance-1` or you named it during creation)
