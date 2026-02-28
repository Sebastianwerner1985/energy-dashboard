# Quick Start Guide

Get your Energy Dashboard up and running in 5 minutes!

## Prerequisites

- Home Assistant installed and running
- Python 3.9+ installed
- Power monitoring sensors in Home Assistant

## Step 1: Install Dependencies

```bash
pip3 install -r requirements.txt
```

## Step 2: Get Home Assistant Token

1. Open Home Assistant web interface
2. Click your profile icon (bottom left)
3. Scroll to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Name it "Energy Dashboard"
6. Copy the token (you'll only see it once!)

## Step 3: Configure Environment

### Option A: Quick Setup (Environment Variables)

```bash
export HA_URL="http://homeassistant.local:8123"
export HA_TOKEN="paste-your-token-here"
export ELECTRICITY_RATE="0.12"
```

### Option B: Configuration File

1. Copy example config:
   ```bash
   cp config.example.py config.py
   ```

2. Edit `config.py`:
   ```python
   HA_URL = "http://your-homeassistant:8123"
   HA_TOKEN = "your-token-here"
   ELECTRICITY_RATE = 0.12  # Your rate per kWh
   ```

## Step 4: Run the Application

```bash
python3 app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
INFO: Starting Energy Dashboard on http://localhost:5000
```

## Step 5: Access the Dashboard

Open your browser to: `http://localhost:5000`

You should see the Overview page with your energy data!

## Troubleshooting

### "Connection Failed"
- Check Home Assistant is running
- Verify URL is correct (include port 8123)
- Ensure token is valid

### "No Data Available"
- Check you have power sensors in Home Assistant
- Verify sensors have units: W, kW, Wh, or kWh
- Try refreshing the page

### "Module not found"
- Ensure you ran: `pip3 install -r requirements.txt`
- Check you're using Python 3.9+

## Next Steps

1. Explore all five dashboard pages
2. Toggle dark/light mode (moon/sun icon)
3. Customize electricity rate in Settings
4. Check individual device details
5. Review historical trends

## Need Help?

- Check the full README.md
- Review logs: `tail -f logs/energy_dashboard.log`
- Report issues on GitHub

Enjoy monitoring your energy consumption!
