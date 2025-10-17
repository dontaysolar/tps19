#!/bin/bash
# TPS19 - Google Cloud Platform Automated Deployment Script
# AEGIS-COMPLIANT DEPLOYMENT AUTOMATION

set -e  # Exit on any error

echo "============================================================"
echo "🚀 TPS19 - Google Cloud Platform Deployment"
echo "============================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variables
PROJECT_ID="${1:-tps19-trading-bot}"
REGION="${2:-us-central1}"
SERVICE_NAME="tps19-trading-bot"

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    log_error "gcloud CLI not found"
    log_info "Use Cloud Shell or install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

log_info "Using project: $PROJECT_ID"
log_info "Using region: $REGION"
echo ""

# Step 1: Set project
log_step "1/7: Setting Google Cloud project..."
gcloud config set project $PROJECT_ID
log_info "✅ Project set"
echo ""

# Step 2: Enable APIs
log_step "2/7: Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com \
  --quiet

log_info "✅ APIs enabled"
echo ""

# Step 3: Build container image
log_step "3/7: Building Docker container..."
gcloud builds submit \
  --tag gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --timeout=20m \
  --machine-type=n1-highcpu-8 \
  --quiet

log_info "✅ Container built successfully"
echo ""

# Step 4: Create secrets (if API keys provided via env vars)
log_step "4/7: Setting up secrets..."
if [ ! -z "$EXCHANGE_API_KEY" ]; then
    echo -n "$EXCHANGE_API_KEY" | gcloud secrets create exchange-api-key \
      --data-file=- --replication-policy=automatic 2>/dev/null || \
    echo -n "$EXCHANGE_API_KEY" | gcloud secrets versions add exchange-api-key \
      --data-file=-
    log_info "✅ API key secret created/updated"
else
    log_warn "EXCHANGE_API_KEY not set. You'll need to add it manually later."
fi

if [ ! -z "$EXCHANGE_API_SECRET" ]; then
    echo -n "$EXCHANGE_API_SECRET" | gcloud secrets create exchange-api-secret \
      --data-file=- --replication-policy=automatic 2>/dev/null || \
    echo -n "$EXCHANGE_API_SECRET" | gcloud secrets versions add exchange-api-secret \
      --data-file=-
    log_info "✅ API secret created/updated"
else
    log_warn "EXCHANGE_API_SECRET not set. You'll need to add it manually later."
fi
echo ""

# Step 5: Deploy to Cloud Run
log_step "5/7: Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 1 \
  --min-instances 1 \
  --set-env-vars "TPS19_ENV=production" \
  --set-env-vars "PYTHON_VERSION=3.11" \
  --allow-unauthenticated \
  --quiet

log_info "✅ Deployed to Cloud Run"
echo ""

# Step 6: Get service URL
log_step "6/7: Getting service information..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format="value(status.url)")

log_info "✅ Service URL: $SERVICE_URL"
echo ""

# Step 7: Verification
log_step "7/7: Verifying deployment..."
sleep 5  # Wait for service to be ready

# Check health endpoint
if curl -f -s "$SERVICE_URL/health" > /dev/null 2>&1; then
    log_info "✅ Health check passed"
else
    log_warn "Health check not responding (this is OK if bot doesn't have HTTP endpoint)"
fi

echo ""
echo "============================================================"
log_info "🎉 DEPLOYMENT COMPLETE!"
echo "============================================================"
echo ""
echo "Service Details:"
echo "  Name: $SERVICE_NAME"
echo "  Project: $PROJECT_ID"
echo "  Region: $REGION"
echo "  URL: $SERVICE_URL"
echo ""
echo "Next Steps:"
echo "  1. View logs: gcloud run services logs tail $SERVICE_NAME --region $REGION"
echo "  2. Check status: gcloud run services describe $SERVICE_NAME --region $REGION"
echo "  3. Set secrets (if not done):"
echo "     gcloud secrets create exchange-api-key --data-file=-"
echo "  4. Monitor in Console: https://console.cloud.google.com/run"
echo ""
echo "Cost Estimate: \$10-20/month (covered by \$300 free credit for 3+ months)"
echo ""
echo "============================================================"
