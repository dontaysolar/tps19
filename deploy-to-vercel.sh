#!/bin/bash
# TPS19 APEX Dashboard - Quick Deploy to Vercel
# Project ID: prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   TPS19 APEX Dashboard - Deploying to Vercel                 ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_ID="prj_PuVHxIAY2NpoqKdZ7QptUw6HIFIz"

# Check if in dashboard directory
if [ ! -f "package.json" ]; then
    echo "📁 Moving to dashboard directory..."
    cd dashboard
fi

echo "✅ Found package.json"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

echo ""
echo "🔨 Building project..."
npm run build

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "🚀 Deploying to Vercel..."
    echo "   Project ID: $PROJECT_ID"
    echo ""
    
    # Deploy to specific project
    vercel --prod --yes --project-id="$PROJECT_ID"
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "✅ DEPLOYMENT COMPLETE!"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Next steps:"
    echo "1. Check your Vercel dashboard for deployment status"
    echo "2. Visit your dashboard URL"
    echo "3. Configure environment variables if needed:"
    echo "   - NEXT_PUBLIC_API_URL"
    echo "   - NEXT_PUBLIC_WS_URL"
    echo "   - ORGANISM_API_URL"
    echo ""
else
    echo ""
    echo "❌ Build failed! Check errors above."
    echo ""
    echo "Common fixes:"
    echo "1. Delete node_modules: rm -rf node_modules"
    echo "2. Delete package-lock.json: rm package-lock.json"
    echo "3. Reinstall: npm install"
    echo "4. Try build again: npm run build"
    exit 1
fi
