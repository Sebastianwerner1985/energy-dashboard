# Energy Dashboard - Deployment Guide

## Overview

Energy Dashboard is a Flask web application that visualizes Home Assistant energy data with a modern SnowUI design system. This guide covers deployment on Raspberry Pi, Home Assistant systems, or any Linux server.

## System Requirements

- Python 3.9 or higher
- Home Assistant instance with REST API enabled
- Network access to Home Assistant instance
- 512MB RAM minimum (1GB+ recommended)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/energy-dashboard.git
cd energy-dashboard
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```env
# Required: Home Assistant Configuration
HA_URL=http://homeassistant.local:8123
HA_TOKEN=your_long_lived_access_token_here

# Optional: Energy Cost Settings
ELECTRICITY_RATE=0.12
CURRENCY_SYMBOL=$

# Optional: Cache Settings
CACHE_TTL=60
HISTORY_CACHE_TTL=300

# Optional: Auto-refresh Interval
REFRESH_INTERVAL=30

# Optional: Flask Settings
SECRET_KEY=your-secret-key-change-in-production
DEBUG=False
```

#### Getting Your Home Assistant Token

1. Log into Home Assistant web interface
2. Click your profile (bottom left)
3. Scroll to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Give it a name (e.g., "Energy Dashboard")
6. Copy the token immediately (you won't see it again!)
7. Paste into `.env` file as `HA_TOKEN=...`

### 5. Run Application

```bash
# Development mode
python app.py

# Production mode (with gunicorn)
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

Access at: `http://localhost:5001`

## Deployment Options

### Option 1: Raspberry Pi (Recommended)

#### Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv git
```

#### Set Up Application

```bash
# Clone repository
cd /home/pi
git clone https://github.com/yourusername/energy-dashboard.git
cd energy-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
nano .env  # Add your HA_URL and HA_TOKEN
```

#### Create Systemd Service

Create `/etc/systemd/system/energy-dashboard.service`:

```ini
[Unit]
Description=Energy Dashboard Web Application
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/energy-dashboard
Environment="PATH=/home/pi/energy-dashboard/venv/bin"
EnvironmentFile=/home/pi/energy-dashboard/.env
ExecStart=/home/pi/energy-dashboard/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable energy-dashboard
sudo systemctl start energy-dashboard
sudo systemctl status energy-dashboard
```

### Option 2: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  energy-dashboard:
    build: .
    ports:
      - "5001:5001"
    environment:
      - HA_URL=${HA_URL}
      - HA_TOKEN=${HA_TOKEN}
      - ELECTRICITY_RATE=${ELECTRICITY_RATE:-0.12}
      - CACHE_TTL=${CACHE_TTL:-60}
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

Run with:

```bash
docker-compose up -d
```

### Option 3: Home Assistant Add-on

Create `config.json`:

```json
{
  "name": "Energy Dashboard",
  "version": "1.0.0",
  "slug": "energy-dashboard",
  "description": "Modern energy monitoring dashboard",
  "arch": ["armhf", "armv7", "aarch64", "amd64", "i386"],
  "startup": "application",
  "boot": "auto",
  "ports": {
    "5001/tcp": 5001
  },
  "options": {
    "electricity_rate": 0.12,
    "currency_symbol": "$"
  },
  "schema": {
    "electricity_rate": "float",
    "currency_symbol": "str"
  }
}
```

## Security Best Practices

### 1. Never Commit Credentials

The `.gitignore` is configured to exclude:
- `.env` files
- `config.py` (if you create one)
- `logs/` directory

Always verify before committing:

```bash
git status
# Ensure .env and config.py are NOT listed
```

### 2. Use Environment Variables

Never hardcode credentials in code. Always use:

```python
import os
HA_TOKEN = os.environ.get('HA_TOKEN', '')
```

### 3. Restrict File Permissions

```bash
# Protect .env file
chmod 600 .env

# Protect logs directory
chmod 700 logs/
```

### 4. Use HTTPS in Production

Set up reverse proxy with nginx:

```nginx
server {
    listen 443 ssl;
    server_name energy.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Port Already in Use

If port 5001 is occupied:

```bash
# Find process using port
lsof -i :5001

# Kill process
kill -9 <PID>

# Or change port in app.py
app.run(host='0.0.0.0', port=5002)
```

### 401 Unauthorized Error

**Problem**: "401 Client Error: Unauthorized for url: http://homeassistant.local:8123/api/states"

**Solutions**:
1. Verify HA_TOKEN is set correctly in `.env`
2. Check token hasn't expired in Home Assistant
3. Ensure token has proper permissions
4. Verify HA_URL is correct and accessible

```bash
# Test Home Assistant connection
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://homeassistant.local:8123/api/states
```

### No Data Showing

**Problem**: Dashboard loads but shows no data

**Solutions**:
1. Check Home Assistant has power/energy sensors
2. Verify sensors are named correctly (contain "power" or "energy")
3. Check Home Assistant logs for API errors
4. Review application logs: `tail -f logs/app.log`

### Mobile Menu Not Working

**Problem**: Hamburger menu doesn't open on mobile

**Fixed in**: Commit 22374bd - Changed JavaScript to use 'mobile-open' class

**Verify fix**:
```bash
# Check JavaScript uses correct class
grep "mobile-open" templates/base.html
```

## Monitoring

### View Application Logs

```bash
# Real-time logs
tail -f logs/app.log

# Recent errors
grep ERROR logs/app.log | tail -20

# Systemd service logs
sudo journalctl -u energy-dashboard -f
```

### Health Check Endpoint

Add to `app.py`:

```python
@app.route('/health')
def health():
    return {'status': 'healthy'}, 200
```

Test: `curl http://localhost:5001/health`

## Performance Tuning

### Cache Settings

Adjust cache TTL based on needs:

```env
# Fast updates (every 30 seconds)
CACHE_TTL=30

# Battery/resource saving (every 5 minutes)
CACHE_TTL=300
```

### Gunicorn Workers

Calculate optimal workers:

```bash
# Formula: (2 x CPU cores) + 1
nproc  # Shows CPU count

# Example for 4 cores:
gunicorn -w 9 -b 0.0.0.0:5001 app:app
```

## Updating

```bash
# Pull latest changes
cd /home/pi/energy-dashboard
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart energy-dashboard
```

## Development for LLMs

### Project Structure

```
energy-dashboard/
├── app.py                 # Flask application entry point
├── requirements.txt       # Python dependencies
├── config.py             # Configuration (gitignored, uses env vars)
├── .env                  # Environment variables (gitignored)
├── services/
│   ├── ha_client.py      # Home Assistant REST API client
│   └── data_processor.py # Data aggregation and caching
├── templates/
│   ├── base.html         # Base template with SnowUI sidebar
│   ├── overview.html     # Dashboard overview page
│   ├── realtime.html     # Real-time monitoring page
│   ├── costs.html        # Cost analysis page
│   ├── history.html      # Historical trends page
│   └── settings.html     # Settings page
├── static/
│   └── css/
│       ├── snowui-tokens.css      # Design system tokens
│       ├── snowui-components.css  # Component styles
│       └── custom.css             # Application-specific styles
└── docs/
    ├── plans/                     # Design and implementation plans
    └── DEPLOYMENT.md              # This file
```

### Key Design Decisions

1. **SnowUI Design System**: Modern, accessible design with dark/light mode
2. **Caching Strategy**: 60-second cache for real-time data, 5-minute for historical
3. **No Database**: Reads directly from Home Assistant API
4. **Responsive Layout**: CSS Grid with mobile hamburger menu
5. **Chart.js**: Client-side charting for interactivity

### Common Modifications

#### Add New Dashboard Page

1. Create route in `app.py`:
   ```python
   @app.route('/newpage')
   def newpage():
       data = processor.get_custom_data()
       return render_template('newpage.html', data=data)
   ```

2. Add method to `data_processor.py`:
   ```python
   def get_custom_data(self):
       cached = self._get_cached('custom')
       if cached:
           return cached
       # ... fetch and process data
       self._set_cache('custom', data)
       return data
   ```

3. Create template `templates/newpage.html` extending `base.html`

4. Add navigation link in `templates/base.html`

#### Customize Cost Calculation

Edit `/Users/d056488/claude-projects/energy-dashboard/services/data_processor.py:156`:

```python
# Current fixed rate
rate = 0.12  # $ per kWh

# Change to time-based rates
hour = datetime.now().hour
if 0 <= hour < 7:
    rate = 0.08  # Off-peak
elif 17 <= hour < 21:
    rate = 0.18  # Peak
else:
    rate = 0.12  # Standard
```

#### Add New Sensor Types

Edit `services/ha_client.py` to filter by different attributes:

```python
def get_temperature_sensors(self):
    states = self._get('/api/states')
    return [s for s in states if
            'temperature' in s.get('attributes', {}).get('device_class', '')]
```

### Testing Checklist

- [ ] Theme toggle switches correctly
- [ ] Mobile menu opens and closes
- [ ] All 5 dashboard pages load
- [ ] Real-time data updates every 30 seconds
- [ ] Charts render correctly
- [ ] Cost calculations accurate
- [ ] History periods (24h, 7d, 30d) work
- [ ] Responsive on mobile/tablet/desktop
- [ ] Dark mode works in all pages
- [ ] No console errors

## Support

For issues or questions:
1. Check logs: `tail -f logs/app.log`
2. Review this deployment guide
3. Check Home Assistant API status
4. Verify network connectivity to HA instance

## License

MIT License - See LICENSE file for details
