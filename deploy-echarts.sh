#!/bin/bash

# Energy Dashboard - ECharts Migration Deployment Script
# Run this to deploy the ECharts changes to Raspberry Pi

set -e

PI_HOST="bstiwrnr@192.168.178.100"
DEPLOY_DIR="/home/bstiwrnr/energy-dashboard"

echo "========================================="
echo "Energy Dashboard ECharts Migration"
echo "========================================="
echo ""

# Check if we can connect to Pi
echo "Testing connection to Raspberry Pi..."
if ! ssh -o ConnectTimeout=5 "$PI_HOST" "exit" 2>/dev/null; then
    echo "❌ Cannot connect to Raspberry Pi at $PI_HOST"
    echo "Please check:"
    echo "  1. SSH key is set up (ssh-copy-id $PI_HOST)"
    echo "  2. Raspberry Pi is powered on and connected"
    echo "  3. IP address is correct"
    exit 1
fi
echo "✅ Connected to Raspberry Pi"
echo ""

# Deploy templates
echo "Deploying updated templates..."
rsync -av --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    templates/ "$PI_HOST:$DEPLOY_DIR/templates/"

if [ $? -eq 0 ]; then
    echo "✅ Templates deployed successfully"
else
    echo "❌ Failed to deploy templates"
    exit 1
fi
echo ""

# Restart service
echo "Restarting energy-dashboard service..."
ssh "$PI_HOST" "sudo systemctl restart energy-dashboard"

if [ $? -eq 0 ]; then
    echo "✅ Service restarted successfully"
else
    echo "❌ Failed to restart service"
    exit 1
fi
echo ""

# Wait for service to start
echo "Waiting for service to start..."
sleep 3

# Check service status
echo "Checking service status..."
if ssh "$PI_HOST" "sudo systemctl is-active --quiet energy-dashboard"; then
    echo "✅ Service is running"
else
    echo "❌ Service is not running"
    echo ""
    echo "Service logs:"
    ssh "$PI_HOST" "sudo journalctl -u energy-dashboard -n 20 --no-pager"
    exit 1
fi
echo ""

# Verify ECharts is loaded
echo "Verifying ECharts is loaded..."
if curl -s http://192.168.178.100:5002/ | grep -q "echarts.init"; then
    echo "✅ ECharts is loaded and active"
else
    echo "❌ ECharts not found in page source"
    echo "   Chart.js might still be loaded instead"
    exit 1
fi
echo ""

echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Open http://192.168.178.100:5002/ in your browser"
echo "2. Test all pages:"
echo "   - Overview: Check power gauge has no whitespace below"
echo "   - Real-time: Check pie chart and bar chart spacing"
echo "   - Costs: Check 30-day projection chart"
echo "   - History: Check chart updates when switching periods"
echo "   - Device: Check 24-hour usage pattern"
echo "3. Open browser console (F12) to check for errors"
echo ""
echo "If you see any issues:"
echo "   ssh $PI_HOST"
echo "   sudo journalctl -u energy-dashboard -f"
echo ""
