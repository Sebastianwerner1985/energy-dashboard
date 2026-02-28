# Energy Dashboard - LLM Development Guide

This document provides comprehensive context for AI assistants (LLMs) working on the Energy Dashboard project.

## Project Overview

Energy Dashboard is a Flask web application that integrates with Home Assistant to provide real-time energy monitoring, cost analysis, and historical trends visualization. It uses the SnowUI design system for a modern, responsive interface.

## Key Context for LLMs

### 1. Project History

**Development Timeline**:
- Created using subagent-driven development workflow
- Initial implementation with 13 tasks (Bootstrap design)
- Complete SnowUI redesign with 10 tasks (current version)
- Comprehensive code review and fixes applied
- All critical and important issues resolved

**Major Changes**:
1. **Bootstrap → SnowUI Migration**: Complete UI redesign from Bootstrap to custom SnowUI design system
2. **Security Fixes**: Removed hardcoded credentials, added environment variable validation
3. **Bug Fixes**: Fixed mobile menu, daily energy calculation, history API indexing
4. **CSS Improvements**: Added missing design tokens (--space-8, --text-3xl)

### 2. Architecture Decisions

**Why Flask?**: Simple, lightweight framework perfect for single-purpose dashboards

**Why No Database?**:
- Home Assistant already stores all data
- Direct API integration reduces complexity
- Caching layer provides performance

**Why SnowUI?**:
- Modern, accessible design system
- Dark/light mode support built-in
- Consistent with other dashboard projects
- CSS custom properties for easy theming

**Port Choice**:
- Uses port 5001 instead of 5000
- Reason: macOS AirPlay Receiver occupies port 5000 by default
- Configured in app.py line 186

### 3. Code Organization

```
Key Files and Their Purpose:

app.py (186 lines)
├── Flask routes for 5 pages (overview, realtime, costs, history, settings)
├── API endpoints for AJAX updates
└── Error handling and logging setup

services/ha_client.py
├── Home Assistant REST API client
├── Methods: get_states, get_power_sensors, get_energy_sensors, get_history
└── Token-based authentication

services/data_processor.py (455 lines)
├── Data aggregation and caching logic
├── Key methods:
│   ├── get_overview_data() - Dashboard summary
│   ├── get_realtime_data() - Current power usage
│   ├── get_cost_data() - Cost calculations
│   ├── get_history_data() - Historical trends
│   └── get_device_data() - Device-specific metrics
└── Caching with TTL (60s for realtime, 300s for history)

templates/base.html (169 lines)
├── SnowUI sidebar layout
├── Theme toggle (dark/light mode)
├── Mobile hamburger menu
└── Navigation structure

static/css/
├── snowui-tokens.css (238 lines) - Design tokens
│   ├── Colors (primary, semantic, chart)
│   ├── Spacing (--space-0 to --space-20, --space-8)
│   ├── Typography (--text-xs to --text-3xl)
│   ├── Shadows, transitions, radius
│   └── Dark mode overrides
├── snowui-components.css - Reusable components
└── custom.css (504 lines) - App-specific styles
    ├── Sidebar layout (260px fixed)
    ├── Main content (CSS Grid)
    ├── Stat cards, tables, charts
    └── Mobile responsive (breakpoint: 768px)
```

### 4. Critical Implementation Details

#### Daily Energy Calculation (IMPORTANT!)

The `_calculate_daily_energy()` method calculates TODAY'S consumption (midnight to now):

```python
# services/data_processor.py:371-430
def _calculate_daily_energy(self, sensors):
    # Get midnight today as start time
    midnight = datetime(now.year, now.month, now.day, 0, 0, 0)

    # For each sensor:
    # 1. Get history from midnight to now
    # 2. Find first valid reading after midnight
    # 3. Get current reading
    # 4. Calculate difference: current - midnight
    # 5. Convert Wh to kWh if needed
    # 6. Sum all sensors
```

**Why this matters**: Energy sensors are cumulative counters. To get today's consumption, we must subtract the midnight value from the current value.

**Common mistake**: Returning the current sensor value directly (which is all-time total).

#### Mobile Menu Fix (CRITICAL!)

**Issue**: JavaScript used `'active'` class but CSS expected `'mobile-open'` class.

**Fix applied** (commit 22374bd):
```javascript
// templates/base.html:150-156
function toggleMobileMenu() {
    sidebar.classList.toggle('mobile-open');  // Changed from 'active'
    mobileBackdrop.classList.toggle('active');
}
```

**CSS**: `.sidebar.mobile-open` defined in custom.css:488-496

#### History API Indexing (IMPORTANT!)

**Issue**: Double indexing caused errors when history was empty.

**Fixed in**: services/data_processor.py:397

```python
# OLD (WRONG):
if history and len(history[0]) > 0:
    states = history[0][0]  # Double indexing!

# NEW (CORRECT):
if history and len(history) > 0:
    states = history  # Already the states list
```

**Why**: `ha_client.get_history()` already returns `data[0]`, so don't index again.

### 5. Security Requirements

**NEVER commit**:
- `.env` file (contains HA_TOKEN)
- `config.py` (if it contains credentials)
- `logs/` directory (may contain sensitive data)

**ALWAYS**:
- Use environment variables for credentials
- Validate required environment variables on startup
- Check `.gitignore` before committing
- Use `chmod 600 .env` to protect file

**Token Management**:
```python
# config.py:10-20
HA_TOKEN = os.environ.get('HA_TOKEN', '')

if not HA_TOKEN:
    print("ERROR: HA_TOKEN environment variable is required")
    sys.exit(1)
```

### 6. Design System Usage

**SnowUI Tokens** (snowui-tokens.css):

```css
/* Spacing: 0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 20 */
--space-4: 16px
--space-8: 32px  /* Added in commit 22374bd */

/* Typography: xs, sm, base, lg, xl, 2xl, 3xl */
--text-sm: 14px
--text-3xl: 32px  /* Added in commit 22374bd */

/* Colors */
--color-primary: #4c98fd
--bg-base: #ffffff (light), #000000 (dark)
--text-primary: #000000 (light), #ffffff (dark)
```

**Layout Pattern**:
```css
.app-container {
    display: grid;
    grid-template-columns: 260px 1fr;  /* Sidebar + content */
    height: 100vh;
}

@media (max-width: 768px) {
    grid-template-columns: 1fr;  /* Stack on mobile */
    .sidebar { transform: translateX(-260px); }
    .sidebar.mobile-open { transform: translateX(0); }
}
```

**Stat Card Structure**:
```html
<div class="stat-card">
    <div class="stat-label">Label</div>
    <div class="stat-value">Value</div>
    <div class="stat-unit">Unit</div>
</div>
```

### 7. Common Modifications

#### Adding a New Dashboard Page

1. **Create route** (app.py):
```python
@app.route('/newpage')
def newpage():
    data = processor.get_newpage_data()
    return render_template('newpage.html', data=data)
```

2. **Add data method** (services/data_processor.py):
```python
def get_newpage_data(self):
    cached = self._get_cached('newpage')
    if cached:
        return cached

    # Fetch and process data
    data = {'key': 'value'}

    self._set_cache('newpage', data)
    return data
```

3. **Create template** (templates/newpage.html):
```html
{% extends "base.html" %}
{% block title %}New Page{% endblock %}
{% block content %}
<!-- Your content -->
{% endblock %}
```

4. **Add navigation** (templates/base.html):
```html
<a href="{{ url_for('newpage') }}" class="nav-link">
    <span class="nav-icon">🆕</span>
    <span class="nav-text">New Page</span>
</a>
```

#### Customizing Cost Calculation

Edit `services/data_processor.py:156` for time-based rates:

```python
def get_cost_data(self):
    # Time-of-use rates
    hour = datetime.now().hour
    if 0 <= hour < 7:
        rate = 0.08  # Off-peak
    elif 17 <= hour < 21:
        rate = 0.18  # Peak
    else:
        rate = 0.12  # Standard
```

#### Adding New Sensor Types

Extend `services/ha_client.py`:

```python
def get_temperature_sensors(self):
    states = self._get('/api/states')
    return [s for s in states
            if 'temperature' in s.get('attributes', {}).get('device_class', '')]
```

### 8. Testing Checklist

Before committing or deploying:

- [ ] Theme toggle switches dark/light modes correctly
- [ ] Mobile menu opens/closes on hamburger click
- [ ] All 5 pages load without errors
- [ ] Real-time data updates every 30 seconds
- [ ] Charts render correctly in both themes
- [ ] Cost calculations are accurate
- [ ] History period selector (24h, 7d, 30d) works
- [ ] Mobile responsive (test at 768px, 1024px)
- [ ] No console errors in browser DevTools
- [ ] No Python exceptions in logs
- [ ] .env and config.py are NOT staged for commit

### 9. Debugging Tips

**Check Flask server logs**:
```bash
tail -f logs/app.log
```

**Test Home Assistant connection**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://homeassistant.local:8123/api/states
```

**Verify environment variables**:
```bash
python3 -c "import os; print(os.environ.get('HA_TOKEN', 'NOT SET'))"
```

**Find port conflicts**:
```bash
lsof -i :5001
```

**Check git status before commit**:
```bash
git status
# Ensure .env, config.py, logs/ are NOT listed
```

### 10. Known Issues and Solutions

#### Issue: "Today's energy is all-time energy"
**Status**: FIXED (commit included daily energy calculation fix)
**Solution**: Implemented midnight-to-now difference calculation

#### Issue: Mobile menu won't open
**Status**: FIXED (commit 22374bd)
**Solution**: Changed JavaScript to use 'mobile-open' class

#### Issue: 401 Unauthorized
**Cause**: Missing or invalid HA_TOKEN
**Solution**: Verify token in .env, check it hasn't expired

#### Issue: Port 5000 in use
**Cause**: macOS AirPlay Receiver
**Solution**: App already uses port 5001

### 11. Development Workflow

**When extending this project**:

1. **Read this file first** - Understand context and decisions
2. **Check code review reports** - See what was already fixed
3. **Follow SnowUI patterns** - Use existing components
4. **Test thoroughly** - Use the checklist above
5. **Document changes** - Update this file if needed

**When fixing bugs**:

1. Check if already fixed in recent commits
2. Review error logs for root cause
3. Test fix in both light and dark modes
4. Verify fix on mobile and desktop
5. Update documentation if behavior changed

### 12. Deployment Context

**Recommended Deployment**:
- Raspberry Pi 4 with 2GB+ RAM
- Systemd service for auto-start
- Nginx reverse proxy for HTTPS
- See docs/DEPLOYMENT.md for full guide

**Environment Setup**:
```bash
# On Raspberry Pi
cd /home/pi
git clone <repo-url> energy-dashboard
cd energy-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add HA_URL and HA_TOKEN

# Test
python app.py

# Production (see DEPLOYMENT.md for systemd service)
```

## Summary for LLMs

When working on this project:

1. **Understand the architecture**: Flask + Home Assistant API + SnowUI design system
2. **Respect security**: Never commit credentials, always use environment variables
3. **Follow design patterns**: Use SnowUI tokens, maintain sidebar layout, support dark mode
4. **Test thoroughly**: Use the checklist, test mobile, verify both themes
5. **Document changes**: Update relevant docs when modifying behavior
6. **Reference existing code**: Look at similar features before implementing new ones
7. **Check commit history**: Many issues were already fixed, learn from them

This project was built with careful attention to security, design consistency, and code quality. Maintain these standards when extending it.
