# Manual Deployment Guide - ECharts Migration

Since SSH key authentication is not set up, here's how to deploy manually.

## Option 1: Set up SSH key (Recommended - One-time setup)

This will make future deployments much easier:

```bash
# Copy your SSH key to the Pi (you'll need to enter Pi password once)
ssh-copy-id pi@192.168.178.100

# Test connection (should work without password now)
ssh pi@192.168.178.100 "echo 'Connection successful!'"

# Now run the deployment script
./deploy-echarts.sh
```

## Option 2: Manual File Copy with Password

Copy files to the Pi (you'll be prompted for password):

```bash
# Navigate to project directory
cd /Users/d056488/Claude-Projects/apps/energy-dashboard

# Copy templates (enter password when prompted)
scp -r templates/* pi@192.168.178.100:/home/pi/energy-dashboard/templates/

# SSH into Pi and restart service (enter password when prompted)
ssh pi@192.168.178.100

# On the Pi, run:
sudo systemctl restart energy-dashboard
sudo systemctl status energy-dashboard

# Verify it's working
curl http://localhost:5002/ | grep echarts

# Exit Pi
exit
```

## Option 3: Direct Pi Access

If you have keyboard/monitor connected to the Pi:

1. **On your Mac, create a zip of templates:**
   ```bash
   cd /Users/d056488/Claude-Projects/apps/energy-dashboard
   zip -r templates.zip templates/
   ```

2. **Transfer the zip file to Pi** (via USB drive, or download from shared location)

3. **On the Pi:**
   ```bash
   cd /home/pi/energy-dashboard

   # Backup current templates
   cp -r templates templates.backup

   # Extract new templates
   unzip ~/templates.zip -d /home/pi/energy-dashboard/

   # Restart service
   sudo systemctl restart energy-dashboard
   sudo systemctl status energy-dashboard
   ```

## Verification Steps

After deployment by any method:

1. **Check the website loads:**
   - Open: http://192.168.178.100:5002/
   - You should see the dashboard

2. **Verify ECharts is loaded:**
   ```bash
   curl -s http://192.168.178.100:5002/ | grep -o "cdn.jsdelivr.net/npm/echarts"
   ```
   Should output: `cdn.jsdelivr.net/npm/echarts`

3. **Check browser console (F12):**
   - Open browser developer tools
   - Look for any JavaScript errors
   - Should see no errors related to Chart.js or echarts

4. **Test all pages:**
   - Overview: http://192.168.178.100:5002/
   - Real-time: http://192.168.178.100:5002/realtime
   - Costs: http://192.168.178.100:5002/costs
   - History: http://192.168.178.100:5002/history
   - Click any device: http://192.168.178.100:5002/device/[device-id]

5. **Check for whitespace issues:**
   - The charts should now have minimal padding/margins
   - Power gauge should have no whitespace below it
   - Pie charts should be compact

## Troubleshooting

### If you see "Chart is not defined" errors:

The old Chart.js code is still cached. Hard refresh:
- Chrome/Edge: Ctrl+Shift+R (Cmd+Shift+R on Mac)
- Firefox: Ctrl+F5 (Cmd+Shift+R on Mac)
- Safari: Cmd+Option+R

### If charts don't appear:

Check service logs:
```bash
ssh pi@192.168.178.100
sudo journalctl -u energy-dashboard -n 50 --no-pager
```

### If service fails to start:

Check for Python errors:
```bash
ssh pi@192.168.178.100
cd /home/pi/energy-dashboard
source venv/bin/activate
python3 app.py
```

## Quick SSH Setup (Saves time for future deployments)

```bash
# Run this once:
ssh-copy-id pi@192.168.178.100

# Enter Pi password when prompted
# Default Raspberry Pi OS password is usually: raspberry

# After this, all future deployments can use:
./deploy-echarts.sh
```

## Files That Changed

All files are in the `templates/` directory:
- base.html (ECharts CDN instead of Chart.js)
- overview.html (Power gauge)
- realtime.html (Pie chart + bar chart)
- costs.html (Cost projection)
- history.html (Historical trends)
- device.html (24-hour usage)

No Python code changes were made, only HTML/JavaScript templates.
