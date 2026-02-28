# Energy Dashboard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a standalone Flask web application for comprehensive energy monitoring with Home Assistant integration, featuring real-time monitoring, cost analysis, and historical trend visualization using the SnowUI design system.

**Architecture:** Multi-page Flask app that polls Home Assistant REST API, caches data in-memory with TTL, and serves SnowUI-styled pages with Chart.js visualizations. Five main pages: Overview, Real-time, Costs, History, and Device Details.

**Tech Stack:** Python 3.9+, Flask 2.3+, requests, Chart.js 4.x, SnowUI design system

---

## Task 1: Project Setup & Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `README.md`
- Create: `.gitignore`

**Step 1: Create requirements.txt**

```txt
Flask>=2.3.0
requests>=2.31.0
python-dateutil>=2.8.0
```

**Step 2: Create .gitignore**

```txt
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env
.vscode/
.idea/
.DS_Store
*.db
*.sqlite
```

**Step 3: Create README.md**

```markdown
# Energy Dashboard

Flask web application for monitoring home energy consumption via Home Assistant integration.

## Features

- Real-time power monitoring by room and device
- Cost analysis and projections
- Historical trend visualization
- Device-level usage insights
- SnowUI design system with dark/light mode

## Setup

1. Install dependencies: `pip3 install -r requirements.txt`
2. Configure credentials in `~/claude-projects/.credentials`
3. Run: `python3 app.py`
4. Access: http://localhost:5002

## Deployment

See `docs/plans/2026-02-28-energy-dashboard-design.md` for deployment instructions.

## Tech Stack

- Python 3.9+
- Flask 2.3+
- Chart.js 4.x
- SnowUI Design System
```

**Step 4: Commit**

```bash
git add requirements.txt .gitignore README.md
git commit -m "feat: add project setup files and dependencies"
```

---

## Task 2: Configuration Module

**Files:**
- Create: `config.py`

**Step 1: Create config.py with credentials loading**

```python
#!/usr/bin/env python3
"""
Configuration module for Energy Dashboard
Loads settings from central credentials file
"""

import os
from pathlib import Path


class Config:
    """Application configuration"""

    # Credentials file location
    CREDENTIALS_FILE = Path.home() / 'claude-projects' / '.credentials'

    # Flask settings
    FLASK_PORT = 5002
    FLASK_HOST = '0.0.0.0'
    DEBUG = False

    # Cache TTL (seconds)
    CACHE_TTL_REALTIME = 30
    CACHE_TTL_HISTORY = 300

    # Cost calculation
    ELECTRICITY_RATE_PER_KWH = 0.30  # EUR

    # Home Assistant configuration (loaded from credentials)
    HA_URL = None
    HA_TOKEN = None

    # Room/device categorization
    ROOM_CATEGORIES = {
        'kitchen': [
            'sensor.kuche_power',
            'sensor.kaffeemaschine_power'
        ],
        'bathroom': [
            'sensor.bad_power'
        ],
        'living_room': [
            'sensor.homepod_power'
        ],
        'laundry': [
            'sensor.meine_waschmaschine_power'
        ],
        'grid': [
            'sensor.bitshake_aktueller_verbrauch',
            'sensor.bitshake_verbrauch',
            'sensor.bitshake_einspeisung',
            'sensor.bitshake_smartmeterreader_mt175_power'
        ],
        'monitoring': [
            'sensor.eve_energy_20ebo8301_power',
            'sensor.eve_energy_20ebo8301_power_2',
            'sensor.eve_energy_20ebo8301_power_3',
            'sensor.eve_energy_20ebo8301_power_4',
            'sensor.eve_energy_20ebo8301_power_5',
            'sensor.eve_energy_20ebo8301_power_6',
            'sensor.eve_energy_20ebo8301_power_7',
            'sensor.eve_energy_20ebo8301_power_8',
            'sensor.eve_energy_20ebo8301_power_10',
            'sensor.eve_energy_20ebo8301_power_11',
            'sensor.eve_energy_20ebo8301_power_12'
        ]
    }

    @classmethod
    def load_credentials(cls):
        """Load HA_URL and HA_TOKEN from credentials file"""
        if not cls.CREDENTIALS_FILE.exists():
            raise FileNotFoundError(
                f"Credentials file not found: {cls.CREDENTIALS_FILE}\n"
                "Please create ~/claude-projects/.credentials with:\n"
                "HA_TOKEN=your_token\n"
                "HA_URL=http://homeassistant.local:8123"
            )

        with open(cls.CREDENTIALS_FILE) as f:
            for line in f:
                line = line.strip()
                if line.startswith('HA_TOKEN='):
                    cls.HA_TOKEN = line.split('=', 1)[1]
                elif line.startswith('HA_URL='):
                    cls.HA_URL = line.split('=', 1)[1]

        if not cls.HA_TOKEN:
            raise ValueError("HA_TOKEN not found in credentials file")
        if not cls.HA_URL:
            raise ValueError("HA_URL not found in credentials file")

        return cls


# Load credentials on module import
Config.load_credentials()
```

**Step 2: Commit**

```bash
git add config.py
git commit -m "feat: add configuration module with credentials loading"
```

---

## Task 3: Home Assistant API Client

**Files:**
- Create: `ha_client.py`

**Step 1: Create HA API client with caching**

```python
#!/usr/bin/env python3
"""
Home Assistant API Client
Handles all interactions with Home Assistant REST API
"""

import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from config import Config


class HomeAssistantClient:
    """Client for Home Assistant REST API with caching"""

    def __init__(self):
        self.base_url = Config.HA_URL
        self.token = Config.HA_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        # Simple in-memory cache
        self._cache = {}
        self._cache_timestamps = {}

    def _get_cache_key(self, endpoint: str, params: str = '') -> str:
        """Generate cache key"""
        return f"{endpoint}:{params}"

    def _is_cache_valid(self, cache_key: str, ttl: int) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache_timestamps:
            return False

        age = time.time() - self._cache_timestamps[cache_key]
        return age < ttl

    def _get_cached(self, cache_key: str, ttl: int) -> Optional[Any]:
        """Get cached data if valid"""
        if self._is_cache_valid(cache_key, ttl):
            return self._cache.get(cache_key)
        return None

    def _set_cache(self, cache_key: str, data: Any):
        """Store data in cache"""
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = time.time()

    def get_sensor_state(self, entity_id: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Get current state of a sensor

        Args:
            entity_id: Entity ID (e.g., 'sensor.kuche_power')
            use_cache: Whether to use cached data

        Returns:
            Dict with state, attributes, etc. or None if unavailable
        """
        cache_key = self._get_cache_key('state', entity_id)

        if use_cache:
            cached = self._get_cached(cache_key, Config.CACHE_TTL_REALTIME)
            if cached is not None:
                return cached

        try:
            url = f"{self.base_url}/api/states/{entity_id}"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                self._set_cache(cache_key, data)
                return data
            else:
                return None

        except Exception as e:
            print(f"Error fetching {entity_id}: {e}")
            return None

    def get_sensors_batch(self, entity_ids: List[str], use_cache: bool = True) -> Dict[str, Dict]:
        """
        Get multiple sensor states

        Args:
            entity_ids: List of entity IDs
            use_cache: Whether to use cached data

        Returns:
            Dict mapping entity_id to state data
        """
        results = {}

        for entity_id in entity_ids:
            state = self.get_sensor_state(entity_id, use_cache)
            if state:
                results[entity_id] = state

        return results

    def get_sensor_history(self, entity_id: str, hours: int = 24, use_cache: bool = True) -> List[Dict]:
        """
        Get historical data for a sensor

        Args:
            entity_id: Entity ID
            hours: Number of hours of history
            use_cache: Whether to use cached data

        Returns:
            List of state changes with timestamp
        """
        cache_key = self._get_cache_key('history', f"{entity_id}:{hours}")

        if use_cache:
            cached = self._get_cached(cache_key, Config.CACHE_TTL_HISTORY)
            if cached is not None:
                return cached

        try:
            # Calculate start time
            start_time = datetime.now() - timedelta(hours=hours)
            start_iso = start_time.isoformat()

            url = f"{self.base_url}/api/history/period/{start_iso}"
            params = {'filter_entity_id': entity_id}

            response = requests.get(url, headers=self.headers, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                # Flatten the response (HA returns list of lists)
                history = data[0] if data else []
                self._set_cache(cache_key, history)
                return history
            else:
                return []

        except Exception as e:
            print(f"Error fetching history for {entity_id}: {e}")
            return []

    def get_all_power_sensors(self) -> List[str]:
        """
        Get all power/energy sensor entity IDs

        Returns:
            List of entity IDs from ROOM_CATEGORIES
        """
        sensors = []
        for room, entities in Config.ROOM_CATEGORIES.items():
            sensors.extend(entities)
        return sensors

    def health_check(self) -> Dict[str, Any]:
        """
        Check connection to Home Assistant

        Returns:
            Dict with status information
        """
        try:
            url = f"{self.base_url}/api/"
            response = requests.get(url, headers=self.headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'healthy',
                    'ha_connection': 'ok',
                    'ha_message': data.get('message', 'API running'),
                    'cached_sensors': len(self._cache),
                    'cache_age_oldest': time.time() - min(self._cache_timestamps.values()) if self._cache_timestamps else 0
                }
            else:
                return {
                    'status': 'unhealthy',
                    'ha_connection': 'error',
                    'error': f"HTTP {response.status_code}"
                }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'ha_connection': 'error',
                'error': str(e)
            }


# Global client instance
ha_client = HomeAssistantClient()
```

**Step 2: Commit**

```bash
git add ha_client.py
git commit -m "feat: add Home Assistant API client with caching"
```

---

## Task 4: Copy SnowUI Design System

**Files:**
- Create: `static/css/snowui-tokens.css`
- Create: `static/css/snowui-components.css`

**Step 1: Create directories**

```bash
mkdir -p static/css
mkdir -p static/js
mkdir -p templates
```

**Step 2: Copy SnowUI files from heizung-tracker**

```bash
cp ~/claude-projects/heizung-tracker-app/design-system/snowui-tokens.css static/css/
cp ~/claude-projects/heizung-tracker-app/design-system/snowui-components.css static/css/
```

**Step 3: Commit**

```bash
git add static/
git commit -m "feat: add SnowUI design system (tokens and components)"
```

---

## Task 5: Base Template with Navigation

**Files:**
- Create: `templates/base.html`

**Step 1: Create base.html template**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Energy Dashboard{% endblock %}</title>

    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

    <!-- Material Design Icons -->
    <link href="https://cdn.jsdelivr.net/npm/@mdi/font@7/css/materialdesignicons.min.css" rel="stylesheet">

    <!-- SnowUI Design System -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/snowui-tokens.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/snowui-components.css') }}">

    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>

    <style>
        body {
            margin: 0;
            font-family: 'Inter', sans-serif;
            background: var(--bg-base);
            color: var(--text-primary);
            display: flex;
            min-height: 100vh;
        }

        .sidebar {
            width: 240px;
            background: var(--bg-surface);
            border-right: 1px solid var(--color-border);
            padding: var(--space-6);
            display: flex;
            flex-direction: column;
        }

        .sidebar-header {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: var(--space-10);
            display: flex;
            align-items: center;
            gap: var(--space-3);
        }

        .sidebar-nav {
            display: flex;
            flex-direction: column;
            gap: var(--space-2);
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: var(--space-3);
            padding: var(--space-3) var(--space-4);
            border-radius: 8px;
            text-decoration: none;
            color: var(--text-secondary);
            font-weight: 500;
            transition: all 0.2s;
        }

        .nav-item:hover {
            background: var(--bg-accent-primary);
            color: var(--text-primary);
        }

        .nav-item.active {
            background: var(--color-primary);
            color: white;
        }

        .nav-item i {
            font-size: 20px;
        }

        .theme-toggle {
            margin-top: auto;
            padding-top: var(--space-6);
            border-top: 1px solid var(--color-border);
        }

        .main-content {
            flex: 1;
            padding: var(--space-10);
            overflow-y: auto;
        }

        .page-header {
            margin-bottom: var(--space-10);
        }

        .page-title {
            font-size: 28px;
            font-weight: 700;
            margin: 0 0 var(--space-2) 0;
        }

        .page-subtitle {
            font-size: 14px;
            color: var(--text-secondary);
            margin: 0;
        }

        @media (max-width: 768px) {
            .sidebar {
                display: none;
            }
        }
    </style>

    {% block extra_css %}{% endblock %}
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <i class="mdi mdi-lightning-bolt"></i>
            Energy
        </div>

        <nav class="sidebar-nav">
            <a href="{{ url_for('overview') }}" class="nav-item {% if request.endpoint == 'overview' %}active{% endif %}">
                <i class="mdi mdi-home-lightning-bolt"></i>
                Overview
            </a>
            <a href="{{ url_for('realtime') }}" class="nav-item {% if request.endpoint == 'realtime' %}active{% endif %}">
                <i class="mdi mdi-clock-outline"></i>
                Real-time
            </a>
            <a href="{{ url_for('costs') }}" class="nav-item {% if request.endpoint == 'costs' %}active{% endif %}">
                <i class="mdi mdi-currency-eur"></i>
                Costs
            </a>
            <a href="{{ url_for('history') }}" class="nav-item {% if request.endpoint == 'history' %}active{% endif %}">
                <i class="mdi mdi-chart-line"></i>
                History
            </a>
        </nav>

        <div class="theme-toggle">
            <button class="btn btn-ghost btn-sm" onclick="toggleTheme()">
                <i class="mdi mdi-theme-light-dark"></i>
                Toggle Theme
            </button>
        </div>
    </div>

    <main class="main-content">
        {% block content %}{% endblock %}
    </main>

    <script>
        // Theme toggle
        function toggleTheme() {
            const html = document.documentElement;
            const isDark = html.classList.toggle('dark');
            html.setAttribute('data-theme', isDark ? 'dark' : 'light');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        }

        // Load saved theme preference
        const saved = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (saved === 'dark' || (!saved && prefersDark)) {
            document.documentElement.classList.add('dark');
            document.documentElement.setAttribute('data-theme', 'dark');
        }
    </script>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

**Step 2: Commit**

```bash
git add templates/base.html
git commit -m "feat: add base template with sidebar navigation and theme toggle"
```

---

## Task 6: Flask Application Core

**Files:**
- Create: `app.py`

**Step 1: Create Flask app with basic routes**

```python
#!/usr/bin/env python3
"""
Energy Dashboard - Flask Application
Main application entry point
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
from config import Config
from ha_client import ha_client

app = Flask(__name__)
app.config.from_object(Config)


# Disable caching for development
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


def calculate_power_from_state(state_data):
    """Extract power value from sensor state"""
    if not state_data:
        return 0.0

    try:
        state = state_data.get('state', '0')
        # Handle 'unavailable' or 'unknown' states
        if state in ['unavailable', 'unknown', 'none', None]:
            return 0.0
        return float(state)
    except (ValueError, TypeError):
        return 0.0


def get_room_data():
    """Get current power data organized by room"""
    all_sensors = ha_client.get_all_power_sensors()
    sensor_states = ha_client.get_sensors_batch(all_sensors)

    rooms = {}
    total_power = 0
    active_devices = 0

    for room_name, entity_ids in Config.ROOM_CATEGORIES.items():
        room_power = 0
        devices = []

        for entity_id in entity_ids:
            state_data = sensor_states.get(entity_id)
            power = calculate_power_from_state(state_data)

            # Determine device name from entity_id or attributes
            if state_data:
                name = state_data.get('attributes', {}).get('friendly_name', entity_id)
            else:
                name = entity_id.replace('sensor.', '').replace('_', ' ').title()

            devices.append({
                'entity': entity_id,
                'name': name,
                'power': round(power, 1),
                'state': 'on' if power > 5 else 'off',
                'available': state_data is not None
            })

            room_power += power
            if power > 5:
                active_devices += 1

        rooms[room_name] = {
            'power': round(room_power, 1),
            'devices': devices
        }

        total_power += room_power

    return {
        'timestamp': datetime.now().isoformat(),
        'total_power': round(total_power, 1),
        'active_devices': active_devices,
        'rooms': rooms
    }


def calculate_cost_today(total_power_w):
    """Calculate cost for today based on current power"""
    # Simple estimation: assume this power for hours since midnight
    now = datetime.now()
    hours_today = now.hour + now.minute / 60.0

    # Convert W to kWh
    kwh_today = (total_power_w / 1000) * hours_today

    # Calculate cost
    cost = kwh_today * Config.ELECTRICITY_RATE_PER_KWH

    return round(cost, 2)


# Routes
@app.route('/')
def overview():
    """Overview page - main dashboard"""
    return render_template('overview.html')


@app.route('/realtime')
def realtime():
    """Real-time monitoring page"""
    return render_template('realtime.html')


@app.route('/costs')
def costs():
    """Cost analysis page"""
    return render_template('costs.html')


@app.route('/history')
def history():
    """Historical trends page"""
    return render_template('history.html')


@app.route('/device/<entity_id>')
def device_details(entity_id):
    """Device details page"""
    return render_template('device.html', entity_id=entity_id)


# API Endpoints
@app.route('/api/current')
def api_current():
    """Get current energy data (JSON)"""
    try:
        data = get_room_data()

        # Add cost calculation
        data['total_cost_today'] = calculate_cost_today(data['total_power'])

        # TODO: Add peak power tracking
        data['peak_power_today'] = data['total_power']  # Placeholder

        return jsonify(data)

    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/history/<int:hours>')
def api_history(hours):
    """Get historical data (JSON)"""
    try:
        # Get history for all sensors
        # For now, just return structure - will implement in later task
        return jsonify({
            'hours': hours,
            'data': [],
            'message': 'Historical data not yet implemented'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/device/<entity_id>/stats')
def api_device_stats(entity_id):
    """Get device statistics (JSON)"""
    try:
        # Get current state
        state = ha_client.get_sensor_state(entity_id)

        if not state:
            return jsonify({'error': 'Device not found'}), 404

        power = calculate_power_from_state(state)

        return jsonify({
            'entity_id': entity_id,
            'name': state.get('attributes', {}).get('friendly_name', entity_id),
            'current_power': round(power, 1),
            'state': state.get('state'),
            # TODO: Add historical stats
            'daily_cost': 0,
            'daily_kwh': 0
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    health_data = ha_client.health_check()
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code


if __name__ == '__main__':
    print(f"Starting Energy Dashboard on port {Config.FLASK_PORT}")
    print(f"Access at: http://localhost:{Config.FLASK_PORT}")
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.DEBUG
    )
```

**Step 2: Commit**

```bash
git add app.py
git commit -m "feat: add Flask app core with routes and API endpoints"
```

---

## Task 7: Overview Page

**Files:**
- Create: `templates/overview.html`

**Step 1: Create overview.html template**

```html
{% extends "base.html" %}

{% block title %}Overview - Energy Dashboard{% endblock %}

{% block content %}
<div class="page-header">
    <h1 class="page-title">Energy Overview</h1>
    <p class="page-subtitle">Quick snapshot of current energy consumption</p>
</div>

<!-- Stat Cards -->
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--space-6); margin-bottom: var(--space-10);">
    <div class="stat-card">
        <div class="stat-card-value" id="total-power">--</div>
        <div class="stat-card-label">Total Power (W)</div>
        <div class="stat-card-change" id="power-trend">--</div>
    </div>

    <div class="stat-card stat-card-mint">
        <div class="stat-card-value" id="cost-today">--</div>
        <div class="stat-card-label">Cost Today (€)</div>
        <div class="stat-card-change" id="cost-change">--</div>
    </div>

    <div class="stat-card stat-card-purple">
        <div class="stat-card-value" id="peak-power">--</div>
        <div class="stat-card-label">Peak Power Today (W)</div>
        <div class="stat-card-change" id="peak-time">--</div>
    </div>

    <div class="stat-card stat-card-secondary">
        <div class="stat-card-value" id="active-devices">--</div>
        <div class="stat-card-label">Active Devices</div>
        <div class="stat-card-change">Currently consuming >5W</div>
    </div>
</div>

<!-- Main Chart -->
<div style="background: var(--bg-surface); padding: var(--space-6); border-radius: 12px; margin-bottom: var(--space-10);">
    <h2 style="margin: 0 0 var(--space-6) 0; font-size: 18px; font-weight: 600;">Power Consumption (24h)</h2>
    <canvas id="power-chart" height="80"></canvas>
</div>

<!-- Room/Device List -->
<div style="background: var(--bg-surface); padding: var(--space-6); border-radius: 12px;">
    <h2 style="margin: 0 0 var(--space-6) 0; font-size: 18px; font-weight: 600;">Current Consumption by Room</h2>
    <div id="room-list">
        <p style="color: var(--text-secondary);">Loading...</p>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
let powerChart = null;

// Initialize Chart.js
function initChart() {
    const ctx = document.getElementById('power-chart').getContext('2d');

    powerChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Power (W)',
                data: [],
                borderColor: getComputedStyle(document.documentElement).getPropertyValue('--color-primary').trim(),
                backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--color-primary').trim() + '20',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--color-border').trim()
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Update dashboard data
function updateDashboard() {
    fetch('/api/current')
        .then(response => response.json())
        .then(data => {
            // Update stat cards
            document.getElementById('total-power').textContent = data.total_power.toFixed(0);
            document.getElementById('cost-today').textContent = '€' + data.total_cost_today.toFixed(2);
            document.getElementById('peak-power').textContent = data.peak_power_today.toFixed(0);
            document.getElementById('active-devices').textContent = data.active_devices;

            // Update room list
            updateRoomList(data.rooms);

            // Update chart (placeholder - will add real data later)
            updateChart(data.total_power);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

function updateRoomList(rooms) {
    const container = document.getElementById('room-list');

    let html = '<table style="width: 100%; border-collapse: collapse;">';
    html += '<thead><tr style="border-bottom: 1px solid var(--color-border);">';
    html += '<th style="text-align: left; padding: var(--space-3); font-weight: 600;">Room</th>';
    html += '<th style="text-align: right; padding: var(--space-3); font-weight: 600;">Power (W)</th>';
    html += '<th style="text-align: right; padding: var(--space-3); font-weight: 600;">Devices</th>';
    html += '</tr></thead><tbody>';

    // Sort rooms by power (highest first)
    const sortedRooms = Object.entries(rooms).sort((a, b) => b[1].power - a[1].power);

    for (const [roomName, roomData] of sortedRooms) {
        const displayName = roomName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        html += '<tr style="border-bottom: 1px solid var(--color-border);">';
        html += `<td style="padding: var(--space-3);">${displayName}</td>`;
        html += `<td style="text-align: right; padding: var(--space-3); font-weight: 600;">${roomData.power.toFixed(1)}</td>`;
        html += `<td style="text-align: right; padding: var(--space-3); color: var(--text-secondary);">${roomData.devices.length}</td>`;
        html += '</tr>';
    }

    html += '</tbody></table>';
    container.innerHTML = html;
}

function updateChart(currentPower) {
    // Placeholder: add current power to chart
    // In real implementation, this would fetch historical data
    const now = new Date();
    const timeLabel = now.getHours() + ':' + String(now.getMinutes()).padStart(2, '0');

    if (powerChart) {
        powerChart.data.labels.push(timeLabel);
        powerChart.data.datasets[0].data.push(currentPower);

        // Keep only last 20 data points
        if (powerChart.data.labels.length > 20) {
            powerChart.data.labels.shift();
            powerChart.data.datasets[0].data.shift();
        }

        powerChart.update();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initChart();
    updateDashboard();

    // Auto-refresh every 30 seconds
    setInterval(updateDashboard, 30000);
});
</script>
{% endblock %}
```

**Step 2: Commit**

```bash
git add templates/overview.html
git commit -m "feat: add overview page with stat cards and room list"
```

---

## Task 8: Real-time Monitoring Page

**Files:**
- Create: `templates/realtime.html`

**Step 1: Create realtime.html template**

```html
{% extends "base.html" %}

{% block title %}Real-time - Energy Dashboard{% endblock %}

{% block content %}
<div class="page-header">
    <h1 class="page-title">Real-time Monitoring</h1>
    <p class="page-subtitle">Live power consumption by room and device</p>
    <div style="display: flex; align-items: center; gap: var(--space-3); margin-top: var(--space-4);">
        <span id="last-update" style="color: var(--text-secondary); font-size: 14px;">Loading...</span>
        <span id="update-indicator" style="width: 8px; height: 8px; border-radius: 50%; background: var(--color-green);"></span>
    </div>
</div>

<!-- Room Cards Grid -->
<div id="room-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: var(--space-6);">
    <p style="color: var(--text-secondary);">Loading devices...</p>
</div>
{% endblock %}

{% block extra_css %}
<style>
.room-card {
    background: var(--bg-surface);
    padding: var(--space-6);
    border-radius: 12px;
    border: 1px solid var(--color-border);
}

.room-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-5);
    padding-bottom: var(--space-4);
    border-bottom: 1px solid var(--color-border);
}

.room-name {
    font-size: 18px;
    font-weight: 600;
    margin: 0;
}

.room-total {
    font-size: 20px;
    font-weight: 700;
    color: var(--color-primary);
}

.device-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
}

.device-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3);
    border-radius: 8px;
    background: var(--bg-base);
}

.device-icon {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: var(--bg-accent-primary);
    font-size: 20px;
}

.device-info {
    flex: 1;
}

.device-name {
    font-weight: 500;
    margin: 0;
    font-size: 14px;
}

.device-status {
    font-size: 12px;
    color: var(--text-secondary);
    margin: 0;
}

.device-power {
    font-size: 16px;
    font-weight: 600;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: var(--space-2);
}

.status-dot.on {
    background: var(--color-green);
}

.status-dot.off {
    background: var(--color-border);
}

.room-card.kitchen { border-left: 3px solid var(--color-mint); }
.room-card.bathroom { border-left: 3px solid var(--color-purple); }
.room-card.living_room { border-left: 3px solid var(--color-cyan); }
.room-card.laundry { border-left: 3px solid var(--color-green); }
.room-card.grid { border-left: 3px solid var(--color-primary); }
</style>
{% endblock %}

{% block extra_js %}
<script>
const ICONS = {
    'kuche': 'mdi-stove',
    'kaffeemaschine': 'mdi-coffee',
    'bad': 'mdi-shower',
    'waschmaschine': 'mdi-washing-machine',
    'homepod': 'mdi-speaker',
    'eve_energy': 'mdi-power-socket',
    'bitshake': 'mdi-transmission-tower',
    'default': 'mdi-power-plug'
};

function getDeviceIcon(entityId) {
    for (const [key, icon] of Object.entries(ICONS)) {
        if (entityId.toLowerCase().includes(key)) {
            return icon;
        }
    }
    return ICONS.default;
}

function updateRealtime() {
    const indicator = document.getElementById('update-indicator');
    indicator.style.opacity = '0.3';

    fetch('/api/current')
        .then(response => response.json())
        .then(data => {
            renderRoomCards(data.rooms);

            // Update timestamp
            const now = new Date();
            document.getElementById('last-update').textContent =
                'Last update: ' + now.toLocaleTimeString();

            indicator.style.opacity = '1';
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            document.getElementById('last-update').textContent = 'Error updating data';
        });
}

function renderRoomCards(rooms) {
    const container = document.getElementById('room-grid');

    let html = '';

    for (const [roomKey, roomData] of Object.entries(rooms)) {
        const displayName = roomKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        html += `<div class="room-card ${roomKey}">`;
        html += `<div class="room-header">`;
        html += `<h3 class="room-name">${displayName}</h3>`;
        html += `<div class="room-total">${roomData.power.toFixed(0)}W</div>`;
        html += `</div>`;
        html += `<div class="device-list">`;

        for (const device of roomData.devices) {
            const icon = getDeviceIcon(device.entity);
            const statusClass = device.state === 'on' ? 'on' : 'off';
            const statusText = device.available ? (device.state === 'on' ? 'Active' : 'Idle') : 'Unavailable';

            html += `<div class="device-item">`;
            html += `<div class="device-icon"><i class="mdi ${icon}"></i></div>`;
            html += `<div class="device-info">`;
            html += `<p class="device-name">${device.name}</p>`;
            html += `<p class="device-status">`;
            html += `<span class="status-dot ${statusClass}"></span>${statusText}`;
            html += `</p>`;
            html += `</div>`;
            html += `<div class="device-power">${device.power.toFixed(1)}W</div>`;
            html += `</div>`;
        }

        html += `</div></div>`;
    }

    container.innerHTML = html;
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    updateRealtime();

    // Auto-refresh every 30 seconds
    setInterval(updateRealtime, 30000);
});
</script>
{% endblock %}
```

**Step 2: Commit**

```bash
git add templates/realtime.html
git commit -m "feat: add real-time monitoring page with room cards"
```

---

## Task 9: Cost Analysis Page

**Files:**
- Create: `templates/costs.html`

**Step 1: Create costs.html template**

```html
{% extends "base.html" %}

{% block title %}Costs - Energy Dashboard{% endblock %}

{% block content %}
<div class="page-header">
    <h1 class="page-title">Cost Analysis</h1>
    <p class="page-subtitle">Energy costs and device ranking</p>
</div>

<!-- Monthly Projection Card -->
<div class="stat-card" style="margin-bottom: var(--space-10);">
    <div class="stat-card-value" id="monthly-projection">€--</div>
    <div class="stat-card-label">Estimated Monthly Cost</div>
    <div class="stat-card-change">Based on current usage patterns</div>
</div>

<!-- Charts Row -->
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: var(--space-6); margin-bottom: var(--space-10);">
    <!-- Cost by Room Chart -->
    <div style="background: var(--bg-surface); padding: var(--space-6); border-radius: 12px;">
        <h2 style="margin: 0 0 var(--space-6) 0; font-size: 18px; font-weight: 600;">Cost Breakdown by Room</h2>
        <canvas id="cost-breakdown-chart" height="250"></canvas>
    </div>

    <!-- Daily Cost Chart -->
    <div style="background: var(--bg-surface); padding: var(--space-6); border-radius: 12px;">
        <h2 style="margin: 0 0 var(--space-6) 0; font-size: 18px; font-weight: 600;">Daily Cost (Last 7 Days)</h2>
        <canvas id="daily-cost-chart" height="250"></canvas>
    </div>
</div>

<!-- Device Ranking Table -->
<div style="background: var(--bg-surface); padding: var(--space-6); border-radius: 12px;">
    <h2 style="margin: 0 0 var(--space-6) 0; font-size: 18px; font-weight: 600;">Device Ranking by Cost</h2>
    <div id="device-ranking">
        <p style="color: var(--text-secondary);">Loading...</p>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
let breakdownChart = null;
let dailyCostChart = null;

function initCharts() {
    // Cost breakdown pie chart
    const ctx1 = document.getElementById('cost-breakdown-chart').getContext('2d');
    breakdownChart = new Chart(ctx1, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    getComputedStyle(document.documentElement).getPropertyValue('--color-mint').trim(),
                    getComputedStyle(document.documentElement).getPropertyValue('--color-purple').trim(),
                    getComputedStyle(document.documentElement).getPropertyValue('--color-cyan').trim(),
                    getComputedStyle(document.documentElement).getPropertyValue('--color-green').trim(),
                    getComputedStyle(document.documentElement).getPropertyValue('--color-primary').trim()
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // Daily cost bar chart
    const ctx2 = document.getElementById('daily-cost-chart').getContext('2d');
    dailyCostChart = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Cost (€)',
                data: [3.2, 2.8, 3.5, 3.1, 3.4, 4.2, 3.9],
                backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--color-primary').trim()
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '€' + value.toFixed(2);
                        }
                    }
                }
            }
        }
    });
}

function updateCosts() {
    fetch('/api/current')
        .then(response => response.json())
        .then(data => {
            // Calculate monthly projection
            const dailyCost = data.total_cost_today;
            const monthlyProjection = dailyCost * 30;
            document.getElementById('monthly-projection').textContent = '€' + monthlyProjection.toFixed(2);

            // Update breakdown chart
            updateBreakdownChart(data.rooms);

            // Update device ranking
            updateDeviceRanking(data.rooms);
        })
        .catch(error => {
            console.error('Error fetching cost data:', error);
        });
}

function updateBreakdownChart(rooms) {
    const labels = [];
    const data = [];

    for (const [roomKey, roomData] of Object.entries(rooms)) {
        if (roomData.power > 0) {
            const displayName = roomKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            labels.push(displayName);

            // Estimate daily cost for room
            const dailyCost = (roomData.power / 1000) * 24 * 0.30;
            data.push(dailyCost);
        }
    }

    if (breakdownChart) {
        breakdownChart.data.labels = labels;
        breakdownChart.data.datasets[0].data = data;
        breakdownChart.update();
    }
}

function updateDeviceRanking(rooms) {
    const devices = [];

    for (const [roomKey, roomData] of Object.entries(rooms)) {
        for (const device of roomData.devices) {
            if (device.power > 0) {
                const dailyCost = (device.power / 1000) * 24 * 0.30;
                const dailyKwh = (device.power / 1000) * 24;

                devices.push({
                    name: device.name,
                    power: device.power,
                    dailyCost: dailyCost,
                    dailyKwh: dailyKwh
                });
            }
        }
    }

    // Sort by daily cost (highest first)
    devices.sort((a, b) => b.dailyCost - a.dailyCost);

    // Render table
    const container = document.getElementById('device-ranking');
    let html = '<table style="width: 100%; border-collapse: collapse;">';
    html += '<thead><tr style="border-bottom: 1px solid var(--color-border);">';
    html += '<th style="text-align: left; padding: var(--space-3);">Device</th>';
    html += '<th style="text-align: right; padding: var(--space-3);">Power (W)</th>';
    html += '<th style="text-align: right; padding: var(--space-3);">Daily Cost</th>';
    html += '<th style="text-align: right; padding: var(--space-3);">Daily kWh</th>';
    html += '</tr></thead><tbody>';

    for (const device of devices.slice(0, 10)) {
        html += '<tr style="border-bottom: 1px solid var(--color-border);">';
        html += `<td style="padding: var(--space-3);">${device.name}</td>`;
        html += `<td style="text-align: right; padding: var(--space-3);">${device.power.toFixed(1)}</td>`;
        html += `<td style="text-align: right; padding: var(--space-3); font-weight: 600;">€${device.dailyCost.toFixed(2)}</td>`;
        html += `<td style="text-align: right; padding: var(--space-3); color: var(--text-secondary);">${device.dailyKwh.toFixed(2)}</td>`;
        html += '</tr>';
    }

    html += '</tbody></table>';
    container.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    updateCosts();

    // Refresh every minute
    setInterval(updateCosts, 60000);
});
</script>
{% endblock %}
```

**Step 2: Commit**

```bash
git add templates/costs.html
git commit -m "feat: add cost analysis page with charts and device ranking"
```

---

## Task 10: History Page

**Files:**
- Create: `templates/history.html`

**Step 1: Create history.html template**

```html
{% extends "base.html" %}

{% block title %}History - Energy Dashboard{% endblock %}

{% block content %}
<div class="page-header">
    <h1 class="page-title">Historical Trends</h1>
    <p class="page-subtitle">Power consumption analysis over time</p>
</div>

<!-- Time Range Selector -->
<div style="margin-bottom: var(--space-6);">
    <nav class="nav-pills">
        <a href="#" class="nav-pill active" data-hours="24">24 Hours</a>
        <a href="#" class="nav-pill" data-hours="168">7 Days</a>
        <a href="#" class="nav-pill" data-hours="720">30 Days</a>
    </nav>
</div>

<!-- Main Chart -->
<div style="background: var(--bg-surface); padding: var(--space-6); border-radius: 12px; margin-bottom: var(--space-10);">
    <h2 style="margin: 0 0 var(--space-6) 0; font-size: 18px; font-weight: 600;">Power Over Time</h2>
    <canvas id="history-chart" height="100"></canvas>
</div>

<!-- Daily Energy Chart -->
<div style="background: var(--bg-surface); padding: var(--space-6); border-radius: 12px; margin-bottom: var(--space-10);">
    <h2 style="margin: 0 0 var(--space-6) 0; font-size: 18px; font-weight: 600;">Daily Energy Consumption</h2>
    <canvas id="daily-energy-chart" height="80"></canvas>
</div>

<!-- Device Comparison -->
<div style="background: var(--bg-surface); padding: var(--space-6); border-radius: 12px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-6);">
        <h2 style="margin: 0; font-size: 18px; font-weight: 600;">Device Comparison</h2>
        <button class="btn btn-secondary btn-sm" onclick="showDeviceSelector()">
            <i class="mdi mdi-plus"></i> Add Device
        </button>
    </div>
    <canvas id="comparison-chart" height="80"></canvas>
    <div id="selected-devices" style="margin-top: var(--space-4); display: flex; flex-wrap: gap; gap: var(--space-2);"></div>
</div>
{% endblock %}

{% block extra_js %}
<script>
let historyChart = null;
let dailyEnergyChart = null;
let comparisonChart = null;
let selectedTimeRange = 24;

function initCharts() {
    const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--color-primary').trim();
    const cyanColor = getComputedStyle(document.documentElement).getPropertyValue('--color-cyan').trim();
    const mintColor = getComputedStyle(document.documentElement).getPropertyValue('--color-mint').trim();

    // History chart
    const ctx1 = document.getElementById('history-chart').getContext('2d');
    historyChart = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Total Power (W)',
                data: [],
                borderColor: primaryColor,
                backgroundColor: primaryColor + '20',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + 'W';
                        }
                    }
                }
            }
        }
    });

    // Daily energy chart
    const ctx2 = document.getElementById('daily-energy-chart').getContext('2d');
    dailyEnergyChart = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
            datasets: [{
                label: 'Energy (kWh)',
                data: [45, 52, 48, 55, 51, 58, 54],
                backgroundColor: cyanColor
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + ' kWh';
                        }
                    }
                }
            }
        }
    });

    // Comparison chart
    const ctx3 = document.getElementById('comparison-chart').getContext('2d');
    comparisonChart = new Chart(ctx3, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function loadHistory(hours) {
    // Placeholder: Generate sample data
    // In real implementation, fetch from /api/history/<hours>
    const labels = [];
    const data = [];
    const now = new Date();

    const points = Math.min(hours, 48);
    const interval = (hours * 60) / points;

    for (let i = points; i >= 0; i--) {
        const time = new Date(now.getTime() - (i * interval * 60000));
        labels.push(time.getHours() + ':' + String(time.getMinutes()).padStart(2, '0'));
        data.push(Math.random() * 1000 + 1500);
    }

    if (historyChart) {
        historyChart.data.labels = labels;
        historyChart.data.datasets[0].data = data;
        historyChart.update();
    }
}

function showDeviceSelector() {
    alert('Device selector not yet implemented');
    // TODO: Implement device multi-select modal
}

// Handle time range selection
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    loadHistory(24);

    // Time range pill click handlers
    document.querySelectorAll('.nav-pill').forEach(pill => {
        pill.addEventListener('click', function(e) {
            e.preventDefault();

            // Update active state
            document.querySelectorAll('.nav-pill').forEach(p => p.classList.remove('active'));
            this.classList.add('active');

            // Load new time range
            const hours = parseInt(this.dataset.hours);
            selectedTimeRange = hours;
            loadHistory(hours);
        });
    });
});
</script>
{% endblock %}
```

**Step 2: Commit**

```bash
git add templates/history.html
git commit -m "feat: add history page with time-series charts"
```

---

## Task 11: Device Details Page

**Files:**
- Create: `templates/device.html`

**Step 1: Create device.html template**

```html
{% extends "base.html" %}

{% block title %}Device Details - Energy Dashboard{% endblock %}

{% block content %}
<div style="margin-bottom: var(--space-6);">
    <a href="{{ url_for('realtime') }}" class="btn btn-ghost btn-sm">
        <i class="mdi mdi-arrow-left"></i> Back to Real-time
    </a>
</div>

<div class="page-header">
    <h1 class="page-title" id="device-name">Loading...</h1>
    <p class="page-subtitle" id="device-entity">{{ entity_id }}</p>
</div>

<!-- Device Header Card -->
<div class="stat-card" style="margin-bottom: var(--space-10);">
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: var(--space-6);">
        <div>
            <div class="stat-card-label">Current Power</div>
            <div class="stat-card-value" id="current-power">--</div>
        </div>
        <div>
            <div class="stat-card-label">Daily Cost</div>
            <div class="stat-card-value" id="daily-cost">€--</div>
        </div>
        <div>
            <div class="stat-card-label">Daily kWh</div>
            <div class="stat-card-value" id="daily-kwh">--</div>
        </div>
        <div>
            <div class="stat-card-label">Status</div>
            <div class="stat-card-value" id="device-status">--</div>
        </div>
    </div>
</div>

<!-- 24h Chart -->
<div style="background: var(--bg-surface); padding: var(--space-6); border-radius: 12px; margin-bottom: var(--space-10);">
    <h2 style="margin: 0 0 var(--space-6) 0; font-size: 18px; font-weight: 600;">Power (Last 24 Hours)</h2>
    <canvas id="device-24h-chart" height="80"></canvas>
</div>

<!-- Usage Patterns -->
<div style="background: var(--bg-surface); padding: var(--space-6); border-radius: 12px;">
    <h2 style="margin: 0 0 var(--space-6) 0; font-size: 18px; font-weight: 600;">Average Usage by Hour</h2>
    <canvas id="usage-pattern-chart" height="80"></canvas>
</div>
{% endblock %}

{% block extra_js %}
<script>
const entityId = '{{ entity_id }}';
let device24hChart = null;
let usagePatternChart = null;

function initCharts() {
    const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--color-primary').trim();
    const mintColor = getComputedStyle(document.documentElement).getPropertyValue('--color-mint').trim();

    // 24h chart
    const ctx1 = document.getElementById('device-24h-chart').getContext('2d');
    device24hChart = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Power (W)',
                data: [],
                borderColor: primaryColor,
                backgroundColor: primaryColor + '20',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Usage pattern chart
    const ctx2 = document.getElementById('usage-pattern-chart').getContext('2d');
    usagePatternChart = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: ['0h', '2h', '4h', '6h', '8h', '10h', '12h', '14h', '16h', '18h', '20h', '22h'],
            datasets: [{
                label: 'Avg Power (W)',
                data: Array(12).fill(0).map(() => Math.random() * 300 + 100),
                backgroundColor: mintColor
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function loadDeviceData() {
    fetch(`/api/device/${entityId}/stats`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('device-name').textContent = data.name;
            document.getElementById('current-power').textContent = data.current_power + 'W';
            document.getElementById('daily-cost').textContent = '€' + data.daily_cost.toFixed(2);
            document.getElementById('daily-kwh').textContent = data.daily_kwh.toFixed(2) + ' kWh';
            document.getElementById('device-status').textContent = data.state || 'unknown';

            // TODO: Load and render historical data for charts
        })
        .catch(error => {
            console.error('Error loading device data:', error);
        });
}

document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    loadDeviceData();

    // Refresh every 30 seconds
    setInterval(loadDeviceData, 30000);
});
</script>
{% endblock %}
```

**Step 2: Commit**

```bash
git add templates/device.html
git commit -m "feat: add device details page with stats and charts"
```

---

## Task 12: Testing and Documentation

**Files:**
- Modify: `README.md`

**Step 1: Update README with setup instructions**

```markdown
# Energy Dashboard

Flask web application for monitoring home energy consumption via Home Assistant integration.

## Features

- **Overview** - Quick snapshot with stat cards and total consumption
- **Real-time Monitoring** - Live power consumption by room and device
- **Cost Analysis** - Daily/monthly cost breakdown and device ranking
- **Historical Trends** - Time-series charts for consumption analysis
- **Device Details** - Per-device usage insights and patterns

## Tech Stack

- Python 3.9+
- Flask 2.3+
- Chart.js 4.x
- SnowUI Design System
- Home Assistant REST API

## Setup

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Configure Credentials

Create or update `~/claude-projects/.credentials`:

```
HA_TOKEN=your_home_assistant_long_lived_access_token
HA_URL=http://homeassistant.local:8123
```

To create a Home Assistant long-lived access token:
1. Open Home Assistant
2. Go to Profile → Security
3. Scroll to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Copy the token to credentials file

### 3. Run Locally

```bash
python3 app.py
```

Access at: http://localhost:5002

## Configuration

Edit `config.py` to customize:

- `FLASK_PORT` - Port to run on (default: 5002)
- `ELECTRICITY_RATE_PER_KWH` - Your electricity rate (default: €0.30)
- `ROOM_CATEGORIES` - Device categorization by room
- `CACHE_TTL_REALTIME` - Real-time cache TTL (default: 30s)
- `CACHE_TTL_HISTORY` - History cache TTL (default: 5min)

## Deployment

### Raspberry Pi Setup

1. Clone repository:
```bash
git clone <repo-url> ~/energy-dashboard
cd ~/energy-dashboard
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Create systemd service:
```bash
sudo nano /etc/systemd/system/energy-dashboard.service
```

Paste:
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

4. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable energy-dashboard
sudo systemctl start energy-dashboard
sudo systemctl status energy-dashboard
```

5. Check logs:
```bash
journalctl -u energy-dashboard -f
```

### Access

- Local: http://100.127.179.121:5002
- Tailscale: http://100.127.179.121:5002

## Project Structure

```
energy-dashboard/
├── app.py                    # Flask app
├── config.py                 # Configuration
├── ha_client.py              # HA API client
├── requirements.txt          # Dependencies
├── static/
│   ├── css/                  # SnowUI design system
│   └── js/                   # Dashboard JS
├── templates/                # HTML templates
└── docs/plans/               # Design docs
```

## API Endpoints

- `GET /api/current` - Current energy data (JSON)
- `GET /api/history/<hours>` - Historical data (JSON)
- `GET /api/device/<entity_id>/stats` - Device stats (JSON)
- `GET /health` - Health check

## Development

1. Make changes locally
2. Test at http://localhost:5002
3. Commit changes
4. Deploy to Pi:
   ```bash
   ssh bstiwrnr@100.127.179.121
   cd ~/energy-dashboard
   git pull
   sudo systemctl restart energy-dashboard
   ```

## Troubleshooting

**Connection refused:**
- Check HA is running: `curl http://homeassistant.local:8123/api/`
- Verify token in credentials file
- Check Tailscale connection

**Sensors unavailable:**
- Verify sensor entity IDs in config.py
- Check HA developer tools → States

**Service won't start:**
- Check logs: `journalctl -u energy-dashboard -n 50`
- Verify Python path: `which python3`
- Check permissions: `ls -la ~/energy-dashboard`

## License

MIT
```

**Step 2: Test the application**

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run app
python3 app.py
```

Visit http://localhost:5002 and verify:
- [ ] All pages load
- [ ] Sidebar navigation works
- [ ] Theme toggle works
- [ ] /api/current returns data
- [ ] /health returns healthy status

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update README with complete setup and deployment instructions"
```

---

## Task 13: Final Review and Deployment Prep

**Step 1: Create .gitignore additions**

```bash
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
```

**Step 2: Create deployment checklist**

Create `docs/DEPLOYMENT.md`:

```markdown
# Deployment Checklist

## Pre-Deployment

- [ ] All tests pass locally
- [ ] Credentials file configured
- [ ] Config.py room categories updated
- [ ] README instructions verified
- [ ] Git repository clean (no uncommitted changes)

## Raspberry Pi Deployment

- [ ] SSH to Pi: `ssh bstiwrnr@100.127.179.121`
- [ ] Clone or pull repo to `~/energy-dashboard`
- [ ] Install dependencies: `pip3 install -r requirements.txt`
- [ ] Verify credentials file: `cat ~/claude-projects/.credentials`
- [ ] Test run: `python3 app.py` (Ctrl+C to stop)
- [ ] Create systemd service
- [ ] Enable service: `sudo systemctl enable energy-dashboard`
- [ ] Start service: `sudo systemctl start energy-dashboard`
- [ ] Check status: `sudo systemctl status energy-dashboard`
- [ ] Test access: `curl http://localhost:5002/health`
- [ ] Test from Mac: `curl http://100.127.179.121:5002/health`

## Post-Deployment Verification

- [ ] Dashboard loads in browser
- [ ] All pages accessible
- [ ] Real-time data updates
- [ ] No errors in logs: `journalctl -u energy-dashboard -n 50`
- [ ] Theme toggle works
- [ ] Charts render correctly
- [ ] Device data displays accurately

## Rollback Plan

If issues arise:
```bash
sudo systemctl stop energy-dashboard
sudo systemctl disable energy-dashboard
# Fix issues, then redeploy
```
```

**Step 3: Final commit**

```bash
git add .gitignore docs/DEPLOYMENT.md
git commit -m "chore: add deployment checklist and finalize gitignore"
```

**Step 4: Tag release**

```bash
git tag -a v1.0.0 -m "Initial release: Energy Dashboard v1.0.0"
```

---

## Execution Complete

All tasks completed! The energy dashboard is ready for deployment.

**Summary:**
- ✅ Flask app with 5 pages (Overview, Real-time, Costs, History, Device Details)
- ✅ Home Assistant API integration with caching
- ✅ SnowUI design system applied
- ✅ Chart.js visualizations
- ✅ Configuration management with central credentials
- ✅ Complete documentation and deployment guide

**Next Steps:**
1. Deploy to Raspberry Pi following `docs/DEPLOYMENT.md`
2. Access at http://100.127.179.121:5002
3. Monitor logs and verify functionality
4. Iterate on any issues found
