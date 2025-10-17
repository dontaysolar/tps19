#!/bin/bash
# Create a deployment package that can be transferred to VM

echo "📦 Creating deployment package..."

cd /workspace

# Create tarball with all necessary files
tar -czf tps19_deploy.tar.gz \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='*.db' \
  --exclude='*.log' \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='.env' \
  --exclude='*.tar.gz' \
  .

echo "✅ Package created: tps19_deploy.tar.gz"
echo "📊 Size: $(du -h tps19_deploy.tar.gz | cut -f1)"
echo ""
echo "🚀 To use on VM:"
echo "   1. Upload tps19_deploy.tar.gz to your VM"
echo "   2. Run: tar -xzf tps19_deploy.tar.gz && cd tps19"
