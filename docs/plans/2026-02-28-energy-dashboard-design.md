# Energy Dashboard Design

**Date:** 2026-02-28
**Author:** Claude Code
**Status:** Approved

## Overview

A standalone Flask web application for comprehensive energy monitoring and cost analysis, integrating with Home Assistant sensors. Built using the SnowUI design system to provide real-time monitoring, historical analysis, and cost tracking for all energy-consuming devices in the home.

## Goals

1. **Real-time monitoring** - Live view of current power consumption across all devices and rooms
2. **Cost tracking** - Daily and monthly energy cost analysis with device-level breakdown
3. **Historical analysis** - Trend visualization over time (24h, 7d, 30d views)
4. **Device insights** - Detailed per-device statistics and usage patterns
5. **Multi-page dashboard** - Dedicated pages for different analysis needs

## Architecture

### System Overview

```
Home Assistant API (port 8123)
  ↓
  ↓ REST API calls (every 30s for realtime, 5min for history)
  ↓
Energy Dashboard Flask App (port 5002)
  ↓ In-memory cache with TTL
  ↓
Frontend (SnowUI + Chart.js)
  ↓ AJAX polling for updates
  ↓
User Browser
```

### Technology Stack

**Backend:**
- Python 3.9+
- Flask 2.3+ (web framework)
- requests (HA API client)
- python-dateutil (date/time handling)

**Frontend:**
- SnowUI design system (tokens + components)
- Chart.js 4.x (data visualization)
- Vanilla JavaScript (AJAX polling, interactivity)
- Material Design Icons (device icons)

**Infrastructure:**
- Raspberry Pi deployment (same as heizung-tracker-app)
- Port 5002
- Systemd service for auto-start
- Tailscale for remote access

## Project Structure

```
energy-dashboard/
├── app.py                    # Main Flask application
├── config.py                 # Configuration loader
├── ha_client.py              # Home Assistant API wrapper
├── requirements.txt          # Python dependencies
├── README.md                 # Setup instructions
├── static/
│   ├── css/
│   │   ├── snowui-tokens.css      # Design tokens
│   │   └── snowui-components.css  # UI components
│   └── js/
│       └── dashboard.js      # Chart.js, AJAX logic
├── templates/
│   ├── base.html            # Base template with navigation
│   ├── overview.html        # Overview page
│   ├── realtime.html        # Real-time monitoring
│   ├── costs.html           # Cost analysis
│   ├── history.html         # Historical trends
│   └── device.html          # Device details
└── docs/
    └── plans/
        └── 2026-02-28-energy-dashboard-design.md
```

## Data Architecture

### Home Assistant Integration

**API Client** (`ha_client.py`):
- Wrapper class for HA REST API interactions
- Methods:
  - `get_sensor_state(entity_id)` - Current state
  - `get_sensors_batch(entity_ids)` - Batch fetch
  - `get_sensor_history(entity_id, hours=24)` - Historical data
  - `get_all_power_sensors()` - Auto-discovery

**Caching Strategy:**
- In-memory cache with TTL
- Real-time data: 30 second cache
- Historical data: 5 minute cache
- Prevents API rate limiting
- Manual refresh option available

### Entity Categorization

**Room-based grouping** (auto-categorized from entity names):
- Kitchen: `sensor.kuche_power`, `sensor.kaffeemaschine_power`
- Bathroom: `sensor.bad_power`
- Living room: `sensor.homepod_power`
- Laundry: `sensor.meine_waschmaschine_power`
- Grid: `sensor.bitshake_aktueller_verbrauch`, `sensor.bitshake_verbrauch`, `sensor.bitshake_einspeisung`
- Monitoring: All Eve Energy plug sensors

**Configuration in `config.py`:**
```python
ROOM_CATEGORIES = {
    'kitchen': ['sensor.kuche_power', 'sensor.kaffeemaschine_power'],
    'bathroom': ['sensor.bad_power'],
    # ... etc
}
```

### Data Model

**API Response Structure:**
```python
{
    'timestamp': '2026-02-28T14:30:00',
    'total_power': 2450.5,          # W
    'total_cost_today': 3.45,       # EUR
    'peak_power_today': 3200.0,     # W
    'active_devices': 12,           # count
    'rooms': {
        'kitchen': {
            'power': 850.2,
            'devices': [
                {
                    'entity': 'sensor.kuche_power',
                    'name': 'Küche',
                    'power': 450.0,
                    'state': 'on',
                    'icon': 'mdi:stove'
                }
            ]
        }
    },
    'grid': {
        'consumption': 2450.5,
        'feed_in': 0,
        'net': 2450.5
    }
}
```

### Cost Calculation

**Formula:**
```python
cost_eur = (power_watts / 1000) * hours * rate_per_kwh
```

**Settings:**
- Electricity rate: €0.30/kWh (configurable in `config.py`)
- Daily cost: Sum from midnight to now
- Monthly projection: Current day average × 30 days

## Frontend Design

### Page Structure

#### 1. Overview Page (`/`)

**Purpose:** Quick snapshot of overall energy status

**Components:**
- **Stat Cards Grid** (4 cards):
  1. Total Power - Current consumption with trend (↑/↓)
  2. Cost Today - Running cost with % vs yesterday
  3. Peak Power Today - Max consumption with time
  4. Active Devices - Count of devices >5W

- **Main Chart:** 24h line chart of total consumption
- **Device List:** Table showing all rooms, sorted by current power

**Layout:** Grid with stat cards at top, chart middle, table bottom

#### 2. Real-time Page (`/realtime`)

**Purpose:** Live monitoring of all devices by room

**Components:**
- **Room Cards** (grid layout):
  - Room header with total power
  - Device list with icons, names, current power
  - Status indicators (green dot if active, gray if idle)
  - SnowUI accent background colors (rotate mint/purple/cyan)

- **Grid Card** (special):
  - Current consumption (green)
  - Feed-in/solar (orange)
  - Net consumption (blue)

**Auto-refresh:** Every 30 seconds via AJAX

#### 3. Cost Analysis Page (`/costs`)

**Purpose:** Understand energy costs and identify expensive devices

**Components:**
- **Daily Cost Chart:** Bar chart, last 30 days
- **Cost by Room:** Doughnut chart showing % breakdown
- **Device Ranking Table:** Sortable by daily cost/kWh
- **Monthly Projection Card:** Estimated monthly cost

**Layout:** Charts at top, table middle, projection bottom

#### 4. History Page (`/history`)

**Purpose:** Analyze consumption trends over time

**Components:**
- **Time Range Selector:** Nav-pills (24h | 7d | 30d | Custom)
- **Power Over Time Chart:** Line chart for selected period
- **Daily Energy Chart:** Bar chart showing kWh per day
- **Comparison Chart:** Multi-line chart for selected devices
- **Device Selector:** Multi-select dropdown

**Layout:** Time selector at top, main chart, comparison chart with selector

#### 5. Device Details Page (`/device/<entity_id>`)

**Purpose:** Deep dive into single device usage

**Components:**
- **Device Header Card:** Name, current state, power, icon
- **Quick Stats Cards:** Daily cost, daily kWh, avg power, peak power
- **24h Detail Chart:** Power over last 24 hours
- **Usage Patterns Chart:** Average consumption by hour of day
- **Cost History Table:** Daily costs for last 30 days

**Layout:** Header top, stats grid, charts middle, table bottom

### Base Template

**Navigation Sidebar:**
- Home (overview) - `mdi:home-lightning-bolt`
- Real-time - `mdi:clock-outline`
- Costs - `mdi:currency-eur`
- History - `mdi:chart-line`
- Devices - `mdi:devices`

**Features:**
- SnowUI design system styling
- Dark/light mode toggle
- Responsive layout (mobile/tablet/desktop)
- Active page highlighting

### Chart.js Integration

**Color Scheme (from SnowUI tokens):**
- Primary: `--color-primary` (#4c98fd)
- Accents: `--color-cyan`, `--color-mint`, `--color-purple`, `--color-green`
- Dark mode: Auto-adapts via CSS variables

**Chart Types:**
- Line: Consumption over time, comparisons
- Bar: Daily costs, hourly averages
- Doughnut: Cost breakdown by room

**Interaction:**
- Tooltips on hover
- Legend toggle to show/hide datasets
- Responsive sizing

## Technical Implementation

### Flask Routes

```python
# Page routes
@app.route('/')                              # Overview
@app.route('/realtime')                      # Real-time monitoring
@app.route('/costs')                         # Cost analysis
@app.route('/history')                       # Historical trends
@app.route('/device/<entity_id>')            # Device details

# API endpoints (JSON)
@app.route('/api/current')                   # Current data
@app.route('/api/history/<hours>')           # Historical data
@app.route('/api/device/<entity_id>/stats')  # Device stats
@app.route('/health')                        # Health check
```

### Auto-refresh Strategy

**Real-time page:**
- JavaScript polls `/api/current` every 30 seconds
- Updates DOM without full page reload
- Visual indicator during update (pulse animation)

**Other pages:**
- Manual refresh button
- Optional auto-refresh toggle (off by default)

### Error Handling

**HA API failures:**
- Show last cached data with "stale data" warning
- Retry logic with exponential backoff
- User-friendly error messages

**Missing sensors:**
- Display "unavailable" badge
- Exclude from totals calculation
- Log warnings for investigation

**Configuration errors:**
- Validate credentials file on startup
- Clear error page if token missing/invalid
- Provide setup instructions

### Performance Optimization

**Backend:**
- Connection pooling for HA API
- LRU memory cache
- Lazy loading (fetch data only when needed)

**Frontend:**
- Minified CSS/JS in production
- Chart lazy rendering (render only visible)
- Debounce on time range changes

## Configuration Management

### Credentials File

**Location:** `~/claude-projects/.credentials`

**Format:**
```
HA_TOKEN=your_home_assistant_long_lived_token_here
HA_URL=http://homeassistant.local:8123
```

### Config.py Structure

```python
import os

# Load credentials
CREDENTIALS_FILE = os.path.expanduser('~/claude-projects/.credentials')

def load_credentials():
    with open(CREDENTIALS_FILE) as f:
        for line in f:
            if line.startswith('HA_TOKEN='):
                return line.split('=', 1)[1].strip()
    raise ValueError("HA_TOKEN not found in credentials file")

# Settings
HA_URL = 'http://homeassistant.local:8123'
HA_TOKEN = load_credentials()
FLASK_PORT = 5002
DEBUG = False
CACHE_TTL_REALTIME = 30
CACHE_TTL_HISTORY = 300
ELECTRICITY_RATE_PER_KWH = 0.30

# Room categories (see Data Architecture section)
ROOM_CATEGORIES = {...}
```

## Deployment

### Raspberry Pi Setup

**Host:** Same Raspberry Pi as heizung-tracker
**IP:** 100.127.179.121 (Tailscale)
**Port:** 5002
**User:** bstiwrnr
**Directory:** `/home/bstiwrnr/energy-dashboard`

### Systemd Service

**File:** `/etc/systemd/system/energy-dashboard.service`

```ini
[Unit]
Description=Energy Dashboard Flask Application
After=network.target

[Service]
Type=simple
User=bstiwrnr
WorkingDirectory=/home/bstiwrnr/energy-dashboard
ExecStart=/usr/bin/python3 /home/bstiwrnr/energy-dashboard/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Commands:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable energy-dashboard
sudo systemctl start energy-dashboard
sudo systemctl status energy-dashboard
```

### Access URLs

- Local network: `http://100.127.179.121:5002`
- Tailscale (remote): `http://100.127.179.121:5002`

### Development Workflow

**Local development (Mac):**
1. Clone repo: `git clone <repo-url> ~/claude-projects/energy-dashboard`
2. Install dependencies: `pip3 install -r requirements.txt`
3. Run locally: `python3 app.py`
4. Access: `http://localhost:5002`

**Deploy to production:**
1. Commit and push to git
2. SSH to Pi: `ssh bstiwrnr@100.127.179.121`
3. Pull latest: `cd ~/energy-dashboard && git pull`
4. Restart service: `sudo systemctl restart energy-dashboard`
5. Check logs: `journalctl -u energy-dashboard -f`

### Git Workflow

- **Main branch:** Production-ready code
- **Feature branches:** New features/fixes
- **Commit design doc first**, then implementation
- Tag releases: `v1.0.0`, `v1.1.0`, etc.

## Monitoring & Maintenance

### Logging

**Systemd journal:**
```bash
journalctl -u energy-dashboard -f        # Follow logs
journalctl -u energy-dashboard -n 100    # Last 100 lines
```

**Flask logs:**
- Printed to stdout/stderr
- Captured by systemd
- Include timestamps and log levels

### Health Checks

**Endpoint:** `/health`

**Response:**
```json
{
    "status": "healthy",
    "ha_connection": "ok",
    "cached_sensors": 25,
    "last_update": "2026-02-28T14:30:00"
}
```

**Monitoring:**
```bash
curl http://100.127.179.121:5002/health
systemctl status energy-dashboard
```

### Updates

1. Stop service: `sudo systemctl stop energy-dashboard`
2. Pull changes: `git pull`
3. Install new deps: `pip3 install -r requirements.txt`
4. Start service: `sudo systemctl start energy-dashboard`

## Testing Strategy

### Manual Testing Checklist

**Functionality:**
- [ ] All pages load correctly
- [ ] Navigation works between pages
- [ ] Data accuracy matches HA dashboard
- [ ] Charts render correctly
- [ ] Real-time auto-refresh works
- [ ] Device details page works for all entities
- [ ] Time range selector updates charts

**Error scenarios:**
- [ ] HA unavailable (show error gracefully)
- [ ] Sensor unavailable (show badge, exclude from totals)
- [ ] Missing credentials (show setup instructions)
- [ ] Network timeout (show retry message)

**UI/UX:**
- [ ] Dark/light mode toggle works
- [ ] Responsive on mobile/tablet/desktop
- [ ] Charts are readable
- [ ] Stat cards update correctly
- [ ] Loading indicators show during updates

**No automated tests initially** - Focus on manual testing for v1

## Dependencies

### Python (`requirements.txt`)

```
Flask>=2.3.0
requests>=2.31.0
python-dateutil>=2.8.0
```

### Frontend (CDN)

```html
<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>

<!-- Google Fonts (Inter) -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

<!-- Material Design Icons -->
<link href="https://cdn.jsdelivr.net/npm/@mdi/font@7/css/materialdesignicons.min.css" rel="stylesheet">
```

## Future Enhancements (Not in v1)

- Historical data storage in SQLite for faster queries
- Export data as CSV
- Custom alerts (e.g., "power exceeded 3000W")
- Integration with other smart home systems
- Mobile app wrapper
- User authentication for remote access
- Automated tests

## Success Criteria

1. Dashboard accessible at `http://100.127.179.121:5002`
2. All 5 pages functional with correct data
3. Real-time updates work without manual refresh
4. Charts display correctly in light/dark mode
5. Runs reliably as systemd service
6. Accessible via Tailscale from remote locations
7. SnowUI design system consistently applied
8. No HA API rate limiting issues

## References

- Home Assistant REST API: https://developers.home-assistant.io/docs/api/rest/
- SnowUI Design System: `~/claude-projects/heizung-tracker-app/design-system/`
- Chart.js Documentation: https://www.chartjs.org/docs/
- Heizung Tracker App: `~/claude-projects/heizung-tracker-app/` (reference implementation)
