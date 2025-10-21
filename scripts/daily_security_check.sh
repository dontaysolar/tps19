#!/bin/bash
#================================================================
# AEGIS v2.0 - Daily Security Check
# Run this script daily to verify security posture
#================================================================

set -e  # Exit on error

echo "🔍 AEGIS Daily Security Check"
echo "=============================="
echo "Date: $(date)"
echo ""

WORKSPACE="/workspace"
ERRORS=0

#================================================================
# Check 1: Verify .env is not in git
#================================================================
echo "[1/7] Checking if .env is tracked in git..."
cd "$WORKSPACE"
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo "❌ CRITICAL: .env is tracked in git!"
    echo "   Action: Remove with 'git rm --cached .env'"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ .env is not tracked"
fi

#================================================================
# Check 2: Verify .gitignore exists
#================================================================
echo ""
echo "[2/7] Checking if .gitignore exists..."
if [ -f "$WORKSPACE/.gitignore" ]; then
    if grep -q "^\.env$" "$WORKSPACE/.gitignore"; then
        echo "✅ .gitignore exists and includes .env"
    else
        echo "⚠️  .gitignore exists but missing .env entry"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "❌ .gitignore does not exist!"
    ERRORS=$((ERRORS + 1))
fi

#================================================================
# Check 3: Search for hardcoded credentials
#================================================================
echo ""
echo "[3/7] Scanning for hardcoded credentials..."

# Check for old Telegram token
if grep -r "7289126201" --include="*.py" "$WORKSPACE" 2>/dev/null | grep -v ".example" | grep -v "AEGIS_"; then
    echo "❌ Found hardcoded Telegram token!"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ No hardcoded tokens found"
fi

# Check for suspicious patterns
if grep -rE "(api|secret|password|token).*=.*['\"][a-zA-Z0-9]{20,}['\"]" --include="*.py" "$WORKSPACE" 2>/dev/null | grep -v ".example" | grep -v "os.getenv" | grep -v "AEGIS_" | head -5; then
    echo "⚠️  Found potential hardcoded secrets (review above)"
fi

#================================================================
# Check 4: Validate environment variables
#================================================================
echo ""
echo "[4/7] Validating environment variables..."
if [ -f "$WORKSPACE/utils/env_validator.py" ]; then
    python3 "$WORKSPACE/utils/env_validator.py"
    if [ $? -ne 0 ]; then
        echo "❌ Environment validation failed"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "⚠️  env_validator.py not found, skipping"
fi

#================================================================
# Check 5: Check file permissions
#================================================================
echo ""
echo "[5/7] Checking sensitive file permissions..."
if [ -f "$WORKSPACE/.env" ]; then
    PERMS=$(stat -c "%a" "$WORKSPACE/.env" 2>/dev/null || stat -f "%A" "$WORKSPACE/.env" 2>/dev/null)
    if [ "$PERMS" != "600" ] && [ "$PERMS" != "400" ]; then
        echo "⚠️  .env permissions are $PERMS (should be 600 or 400)"
        echo "   Fix with: chmod 600 $WORKSPACE/.env"
    else
        echo "✅ .env has secure permissions ($PERMS)"
    fi
else
    echo "⚠️  .env file not found"
fi

#================================================================
# Check 6: Look for exposed database files
#================================================================
echo ""
echo "[6/7] Checking for exposed database files..."
DB_COUNT=$(find "$WORKSPACE" -name "*.db" -not -path "*/.*" | wc -l)
if [ "$DB_COUNT" -gt 0 ]; then
    if git ls-files "$WORKSPACE/*.db" 2>/dev/null | grep -q ".db"; then
        echo "⚠️  Found $DB_COUNT database files, some may be in git"
    else
        echo "✅ Found $DB_COUNT database files, none in git"
    fi
else
    echo "✅ No database files found"
fi

#================================================================
# Check 7: Verify no API keys in logs
#================================================================
echo ""
echo "[7/7] Checking logs for leaked credentials..."
if [ -d "$WORKSPACE/logs" ]; then
    if grep -r "api.*key\|secret\|token" --include="*.log" "$WORKSPACE/logs" 2>/dev/null | grep -v "API key" | head -3; then
        echo "⚠️  Found potential credentials in logs (review above)"
    else
        echo "✅ No obvious credentials in logs"
    fi
else
    echo "ℹ️  No logs directory found"
fi

#================================================================
# Summary
#================================================================
echo ""
echo "=============================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ All security checks PASSED!"
    echo "=============================="
    exit 0
else
    echo "❌ Found $ERRORS security issues"
    echo "   Review and fix before trading!"
    echo "=============================="
    exit 1
fi
