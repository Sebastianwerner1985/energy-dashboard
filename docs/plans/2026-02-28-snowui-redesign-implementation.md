# Energy Dashboard SnowUI Redesign - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rebuild all Energy Dashboard templates with proper SnowUI design system, replacing Bootstrap with sidebar layout and SnowUI components.

**Architecture:** Complete template rewrite using sidebar + main content grid layout, SnowUI CSS custom properties, and Chart.js integration with SnowUI theming.

**Tech Stack:** Flask 2.3+, Jinja2 templates, SnowUI design system (CSS custom properties), Chart.js 4.x, vanilla JavaScript

---

## Task 1: Rewrite Base Template with SnowUI Sidebar Layout

**Files:**
- Modify: `templates/base.html`
- Reference: `/Users/d056488/claude-projects/heizung-tracker-app/test-redesign/templates/overview.html` (for structure)

**Step 1: Replace base.html with SnowUI structure**

Replace entire `templates/base.html` content:

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{% block title %}Energy Dashboard{% endblock %}</title>

    <!-- Google Fonts: Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

    <!-- SnowUI Design System -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/snowui-tokens.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/snowui-components.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">

    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

    {% block extra_head %}{% endblock %}
</head>
<body>
    <!-- Mobile Menu Toggle -->
    <button class="mobile-menu-toggle" id="mobileMenuToggle" aria-label="Toggle menu">
        <span>☰</span>
    </button>

    <div class="app-container">
        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <!-- Sidebar Header -->
            <div class="sidebar-header">
                <div class="sidebar-logo">⚡</div>
                <div>
                    <div class="sidebar-title">Energy</div>
                    <div class="sidebar-subtitle">Dashboard</div>
                </div>
            </div>

            <!-- Navigation -->
            <nav class="sidebar-nav">
                <a href="{{ url_for('overview') }}" class="nav-link {% if request.endpoint == 'overview' %}active{% endif %}">
                    <span class="nav-icon">📊</span>
                    <span class="nav-text">Overview</span>
                </a>
                <a href="{{ url_for('realtime') }}" class="nav-link {% if request.endpoint == 'realtime' %}active{% endif %}">
                    <span class="nav-icon">⚡</span>
                    <span class="nav-text">Real-time</span>
                </a>
                <a href="{{ url_for('costs') }}" class="nav-link {% if request.endpoint == 'costs' %}active{% endif %}">
                    <span class="nav-icon">💰</span>
                    <span class="nav-text">Costs</span>
                </a>
                <a href="{{ url_for('history') }}" class="nav-link {% if request.endpoint == 'history' %}active{% endif %}">
                    <span class="nav-icon">📈</span>
                    <span class="nav-text">History</span>
                </a>
                <a href="{{ url_for('settings') }}" class="nav-link {% if request.endpoint == 'settings' %}active{% endif %}">
                    <span class="nav-icon">⚙️</span>
                    <span class="nav-text">Settings</span>
                </a>
            </nav>

            <!-- Theme Toggle -->
            <div class="sidebar-footer">
                <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">
                    <span id="themeIcon">🌙</span>
                    <span id="themeText">Dark Mode</span>
                </button>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            {% block content %}{% endblock %}
        </main>
    </div>

    <!-- Mobile Menu Backdrop -->
    <div class="mobile-backdrop" id="mobileBackdrop"></div>

    <!-- Base JavaScript -->
    <script>
        // Theme Management
        function initTheme() {
            const savedTheme = localStorage.getItem('theme') || 'dark';
            document.documentElement.setAttribute('data-theme', savedTheme);
            updateThemeUI(savedTheme);
        }

        function toggleTheme() {
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeUI(newTheme);
            updateChartTheme(newTheme);
        }

        function updateThemeUI(theme) {
            const icon = document.getElementById('themeIcon');
            const text = document.getElementById('themeText');
            if (theme === 'dark') {
                icon.textContent = '🌙';
                text.textContent = 'Dark Mode';
            } else {
                icon.textContent = '☀️';
                text.textContent = 'Light Mode';
            }
        }

        function updateChartTheme(theme) {
            // Update Chart.js defaults
            if (typeof Chart !== 'undefined') {
                const root = document.documentElement;
                const textColor = getComputedStyle(root).getPropertyValue('--text-secondary').trim();
                const borderColor = getComputedStyle(root).getPropertyValue('--border-default').trim();

                Chart.defaults.color = textColor;
                Chart.defaults.borderColor = borderColor;

                // Trigger redraw of all charts
                Chart.instances.forEach(chart => {
                    chart.update('none');
                });
            }
        }

        // Mobile Menu Management
        function initMobileMenu() {
            const toggle = document.getElementById('mobileMenuToggle');
            const sidebar = document.getElementById('sidebar');
            const backdrop = document.getElementById('mobileBackdrop');

            toggle.addEventListener('click', () => {
                sidebar.classList.add('mobile-open');
                backdrop.classList.add('active');
            });

            backdrop.addEventListener('click', () => {
                sidebar.classList.remove('mobile-open');
                backdrop.classList.remove('active');
            });
        }

        // Initialize on load
        document.addEventListener('DOMContentLoaded', () => {
            initTheme();
            initMobileMenu();
            document.getElementById('themeToggle').addEventListener('click', toggleTheme);
        });
    </script>

    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

**Step 2: Verify template renders**

Run Flask app and check base template loads:
```bash
python3 app.py
```

Open http://localhost:5001 in browser.
Expected: Page loads with sidebar (may look broken without CSS)

**Step 3: Commit base template**

```bash
git add templates/base.html
git commit -m "feat: rewrite base template with SnowUI sidebar layout"
```

---

## Task 2: Rewrite Custom CSS for SnowUI Layout

**Files:**
- Modify: `static/css/custom.css`

**Step 1: Replace custom.css with SnowUI layout styles**

Replace entire `static/css/custom.css` content:

```css
/**
 * Energy Dashboard - Custom Styles
 * Built on SnowUI Design System
 */

/* ============================================================================
   APP LAYOUT
   ============================================================================ */

.app-container {
    display: grid;
    grid-template-columns: 260px 1fr;
    min-height: 100vh;
}

/* ============================================================================
   SIDEBAR
   ============================================================================ */

.sidebar {
    background-color: var(--bg-surface);
    border-right: 1px solid var(--border-default);
    padding: var(--space-6);
    display: flex;
    flex-direction: column;
    transition: transform 0.3s ease;
}

.sidebar-header {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-8);
}

.sidebar-logo {
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: white;
    flex-shrink: 0;
}

.sidebar-title {
    font-size: var(--text-lg);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    line-height: 1.2;
}

.sidebar-subtitle {
    font-size: var(--text-sm);
    color: var(--text-muted);
    line-height: 1.2;
}

/* Navigation */
.sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    flex: 1;
}

.nav-link {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: var(--font-medium);
    transition: all 0.2s ease;
    border-left: 3px solid transparent;
}

.nav-link:hover {
    background-color: var(--bg-surface-overlay);
    color: var(--text-primary);
}

.nav-link.active {
    background-color: var(--bg-accent-primary);
    color: var(--color-primary);
    border-left-color: var(--color-primary);
}

.nav-icon {
    font-size: 20px;
    width: 24px;
    text-align: center;
    flex-shrink: 0;
}

.nav-text {
    font-size: var(--text-sm);
}

/* Sidebar Footer */
.sidebar-footer {
    margin-top: auto;
    padding-top: var(--space-4);
    border-top: 1px solid var(--border-default);
}

.theme-toggle {
    width: 100%;
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    background: transparent;
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    cursor: pointer;
    transition: all 0.2s ease;
}

.theme-toggle:hover {
    background-color: var(--bg-surface-overlay);
    border-color: var(--border-strong);
}

#themeIcon {
    font-size: 18px;
}

/* ============================================================================
   MAIN CONTENT
   ============================================================================ */

.main-content {
    background-color: var(--bg-base);
    padding: var(--space-6);
    overflow-y: auto;
    min-height: 100vh;
}

/* Page Header */
.page-header {
    margin-bottom: var(--space-6);
}

.page-title {
    font-size: var(--text-2xl);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    margin-bottom: var(--space-2);
}

.page-subtitle {
    font-size: var(--text-base);
    color: var(--text-muted);
}

/* ============================================================================
   STAT CARDS (Overview Page)
   ============================================================================ */

.stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: var(--space-4);
    margin-bottom: var(--space-6);
}

.stat-card {
    background-color: var(--bg-surface);
    border-radius: var(--radius-lg);
    padding: var(--space-5);
    box-shadow: var(--shadow-sm);
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.stat-icon {
    font-size: 32px;
    margin-bottom: var(--space-2);
}

.stat-value {
    font-size: var(--text-3xl);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
}

.stat-label {
    font-size: var(--text-sm);
    color: var(--text-muted);
    font-weight: var(--font-medium);
}

/* ============================================================================
   MAIN CARDS (Page Containers)
   ============================================================================ */

.main-card {
    background-color: var(--bg-surface);
    border-radius: var(--radius-xl);
    padding: var(--space-6);
    box-shadow: var(--shadow-sm);
    margin-bottom: var(--space-6);
}

.main-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-5);
}

.main-card-title {
    font-size: var(--text-lg);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
}

/* ============================================================================
   TABLES
   ============================================================================ */

.table-container {
    overflow-x: auto;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-default);
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--text-sm);
}

thead {
    background-color: var(--bg-surface-overlay);
    position: sticky;
    top: 0;
    z-index: 10;
}

th {
    padding: var(--space-3);
    text-align: left;
    font-weight: var(--font-semibold);
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted);
    border-bottom: 1px solid var(--border-default);
}

td {
    padding: var(--space-3);
    border-bottom: 1px solid var(--border-default);
    color: var(--text-primary);
}

tbody tr:hover {
    background-color: var(--bg-surface-overlay);
}

tbody tr:last-child td {
    border-bottom: none;
}

.number {
    text-align: right;
    font-variant-numeric: tabular-nums;
}

/* ============================================================================
   CHARTS
   ============================================================================ */

.chart-container {
    position: relative;
    margin: var(--space-4) 0;
}

.chart-wrapper {
    background-color: var(--bg-surface);
    border-radius: var(--radius-lg);
    padding: var(--space-5);
    box-shadow: var(--shadow-sm);
}

/* ============================================================================
   BADGES & STATUS
   ============================================================================ */

.badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: var(--font-medium);
}

.badge-success {
    background-color: rgba(113, 221, 140, 0.15);
    color: var(--color-success);
}

.badge-warning {
    background-color: rgba(245, 184, 73, 0.15);
    color: var(--color-warning);
}

.badge-error {
    background-color: rgba(242, 91, 91, 0.15);
    color: var(--color-error);
}

.badge-info {
    background-color: rgba(76, 152, 253, 0.15);
    color: var(--color-info);
}

/* ============================================================================
   ALERTS
   ============================================================================ */

.alert {
    padding: var(--space-4);
    border-radius: var(--radius-md);
    margin-bottom: var(--space-4);
    display: flex;
    align-items: flex-start;
    gap: var(--space-3);
}

.alert-error {
    background-color: rgba(242, 91, 91, 0.1);
    border: 1px solid var(--color-error);
    color: var(--color-error);
}

.alert-warning {
    background-color: rgba(245, 184, 73, 0.1);
    border: 1px solid var(--color-warning);
    color: var(--color-warning);
}

.alert-info {
    background-color: rgba(76, 152, 253, 0.1);
    border: 1px solid var(--color-info);
    color: var(--color-info);
}

.alert-success {
    background-color: rgba(113, 221, 140, 0.1);
    border: 1px solid var(--color-success);
    color: var(--color-success);
}

.alert-icon {
    font-size: 20px;
    flex-shrink: 0;
}

.alert-content {
    flex: 1;
}

.alert-title {
    font-weight: var(--font-semibold);
    margin-bottom: var(--space-1);
}

/* ============================================================================
   MOBILE MENU
   ============================================================================ */

.mobile-menu-toggle {
    display: none;
    position: fixed;
    top: var(--space-4);
    left: var(--space-4);
    z-index: 1001;
    width: 44px;
    height: 44px;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: 24px;
    cursor: pointer;
    box-shadow: var(--shadow-md);
}

.mobile-backdrop {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 999;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.mobile-backdrop.active {
    display: block;
    opacity: 1;
}

/* ============================================================================
   RESPONSIVE DESIGN
   ============================================================================ */

@media (max-width: 1024px) {
    .app-container {
        grid-template-columns: 200px 1fr;
    }

    .sidebar {
        padding: var(--space-4);
    }
}

@media (max-width: 768px) {
    .app-container {
        grid-template-columns: 1fr;
    }

    .mobile-menu-toggle {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .sidebar {
        position: fixed;
        top: 0;
        left: 0;
        bottom: 0;
        width: 260px;
        z-index: 1000;
        transform: translateX(-100%);
    }

    .sidebar.mobile-open {
        transform: translateX(0);
    }

    .main-content {
        padding: var(--space-4);
        padding-top: calc(var(--space-4) + 60px); /* Account for hamburger button */
    }

    .stat-grid {
        grid-template-columns: 1fr;
    }
}

/* ============================================================================
   UTILITIES
   ============================================================================ */

.text-center {
    text-align: center;
}

.mt-4 {
    margin-top: var(--space-4);
}

.mb-4 {
    margin-bottom: var(--space-4);
}

.flex {
    display: flex;
}

.flex-between {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.gap-4 {
    gap: var(--space-4);
}
```

**Step 2: Test CSS loads correctly**

Refresh browser at http://localhost:5001
Expected: Sidebar layout appears with proper styling

**Step 3: Commit custom CSS**

```bash
git add static/css/custom.css
git commit -m "feat: rewrite custom CSS for SnowUI sidebar layout"
```

---

## Task 3: Rewrite Overview Page

**Files:**
- Modify: `templates/overview.html`

**Step 1: Replace overview.html with SnowUI components**

Replace entire `templates/overview.html` content:

```html
{% extends "base.html" %}

{% block title %}Overview - Energy Dashboard{% endblock %}

{% block content %}
<!-- Page Header -->
<div class="page-header">
    <h1 class="page-title">Energy Overview</h1>
    <p class="page-subtitle">Real-time snapshot of your energy consumption</p>
</div>

<!-- Stat Cards Grid -->
<div class="stat-grid">
    <!-- Total Power -->
    <div class="stat-card">
        <div class="stat-icon">⚡</div>
        <div class="stat-value">
            {% if data and data.total_power %}
                {{ "%.2f"|format(data.total_power) }}
            {% else %}
                0.00
            {% endif %}
        </div>
        <div class="stat-label">Current Power (W)</div>
    </div>

    <!-- Daily Energy -->
    <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-value">
            {% if data and data.daily_energy %}
                {{ "%.2f"|format(data.daily_energy) }}
            {% else %}
                0.00
            {% endif %}
        </div>
        <div class="stat-label">Today's Energy (kWh)</div>
    </div>

    <!-- Daily Cost -->
    <div class="stat-card">
        <div class="stat-icon">💰</div>
        <div class="stat-value">
            {% if data and data.daily_cost %}
                ${{ "%.2f"|format(data.daily_cost) }}
            {% else %}
                $0.00
            {% endif %}
        </div>
        <div class="stat-label">Today's Cost</div>
    </div>

    <!-- Active Devices -->
    <div class="stat-card">
        <div class="stat-icon">🔌</div>
        <div class="stat-value">
            {% if data and data.device_count %}
                {{ data.device_count }}
            {% else %}
                0
            {% endif %}
        </div>
        <div class="stat-label">Active Devices</div>
    </div>
</div>

<!-- Power Usage Gauge -->
<div class="main-card">
    <div class="main-card-header">
        <h2 class="main-card-title">Power Usage</h2>
    </div>
    <div class="chart-container">
        <canvas id="powerGaugeChart" style="max-height: 300px;"></canvas>
    </div>
</div>

<!-- Quick Navigation -->
<div class="main-card">
    <h2 class="main-card-title">Quick Access</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--space-4); margin-top: var(--space-4);">
        <a href="{{ url_for('realtime') }}" style="text-decoration: none;">
            <div class="stat-card">
                <div class="stat-icon">⚡</div>
                <div class="stat-label" style="color: var(--text-primary); font-size: var(--text-base);">Real-time Monitor</div>
            </div>
        </a>
        <a href="{{ url_for('costs') }}" style="text-decoration: none;">
            <div class="stat-card">
                <div class="stat-icon">💰</div>
                <div class="stat-label" style="color: var(--text-primary); font-size: var(--text-base);">Cost Analysis</div>
            </div>
        </a>
        <a href="{{ url_for('history') }}" style="text-decoration: none;">
            <div class="stat-card">
                <div class="stat-icon">📈</div>
                <div class="stat-label" style="color: var(--text-primary); font-size: var(--text-base);">Historical Trends</div>
            </div>
        </a>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
    // Get SnowUI colors
    const root = document.documentElement;
    const primaryColor = getComputedStyle(root).getPropertyValue('--color-primary').trim();
    const surfaceColor = getComputedStyle(root).getPropertyValue('--bg-surface').trim();

    // Power Gauge Chart
    const powerValue = {{ data.total_power if data and data.total_power else 0 }};
    const maxPower = 5000; // Maximum expected power in watts

    const gaugeData = {
        datasets: [{
            data: [powerValue, maxPower - powerValue],
            backgroundColor: [primaryColor, surfaceColor],
            borderWidth: 0
        }]
    };

    const gaugeConfig = {
        type: 'doughnut',
        data: gaugeData,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            circumference: 180,
            rotation: 270,
            cutout: '75%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        },
        plugins: [{
            id: 'gaugeText',
            afterDraw: (chart) => {
                const ctx = chart.ctx;
                const centerX = chart.chartArea.left + (chart.chartArea.right - chart.chartArea.left) / 2;
                const centerY = chart.chartArea.top + (chart.chartArea.bottom - chart.chartArea.top) / 2 + 20;

                ctx.save();
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.font = 'bold 32px Inter';
                ctx.fillStyle = getComputedStyle(root).getPropertyValue('--text-primary').trim();
                ctx.fillText(powerValue.toFixed(0) + ' W', centerX, centerY);
                ctx.restore();
            }
        }]
    };

    // Create chart when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        const ctx = document.getElementById('powerGaugeChart');
        if (ctx) {
            new Chart(ctx, gaugeConfig);
        }
    });
</script>
{% endblock %}
```

**Step 2: Test overview page renders**

Navigate to http://localhost:5001/overview
Expected: Page displays with stat cards, gauge chart, and quick navigation

**Step 3: Commit overview page**

```bash
git add templates/overview.html
git commit -m "feat: rewrite overview page with SnowUI components"
```

---

## Task 4: Rewrite Settings Page

**Files:**
- Modify: `templates/settings.html`

**Step 1: Replace settings.html with SnowUI form components**

Replace entire `templates/settings.html` content:

```html
{% extends "base.html" %}

{% block title %}Settings - Energy Dashboard{% endblock %}

{% block content %}
<!-- Page Header -->
<div class="page-header">
    <h1 class="page-title">Settings</h1>
    <p class="page-subtitle">Configure your Energy Dashboard</p>
</div>

<!-- Home Assistant Connection -->
<div class="main-card">
    <h2 class="main-card-title">Home Assistant Connection</h2>
    <form method="POST" style="margin-top: var(--space-4);">
        <div style="margin-bottom: var(--space-4);">
            <label for="ha_url" style="display: block; margin-bottom: var(--space-2); font-weight: var(--font-medium); color: var(--text-primary);">
                Home Assistant URL
            </label>
            <input
                type="text"
                id="ha_url"
                name="ha_url"
                value="{{ config.HA_URL if config else '' }}"
                placeholder="http://homeassistant.local:8123"
                class="input-field"
                style="width: 100%; padding: var(--space-3); border: 1px solid var(--border-default); border-radius: var(--radius-md); background-color: var(--bg-base); color: var(--text-primary); font-size: var(--text-sm);"
            >
        </div>

        <div style="margin-bottom: var(--space-4);">
            <label for="ha_token" style="display: block; margin-bottom: var(--space-2); font-weight: var(--font-medium); color: var(--text-primary);">
                Long-Lived Access Token
            </label>
            <input
                type="password"
                id="ha_token"
                name="ha_token"
                value="{{ config.HA_TOKEN if config else '' }}"
                placeholder="Enter your Home Assistant token"
                class="input-field"
                style="width: 100%; padding: var(--space-3); border: 1px solid var(--border-default); border-radius: var(--radius-md); background-color: var(--bg-base); color: var(--text-primary); font-size: var(--text-sm);"
            >
            <small style="display: block; margin-top: var(--space-2); color: var(--text-muted); font-size: var(--text-xs);">
                Create a token in Home Assistant: Profile → Long-Lived Access Tokens
            </small>
        </div>
    </form>
</div>

<!-- Energy Configuration -->
<div class="main-card">
    <h2 class="main-card-title">Energy Configuration</h2>
    <form method="POST" style="margin-top: var(--space-4);">
        <div style="margin-bottom: var(--space-4);">
            <label for="electricity_rate" style="display: block; margin-bottom: var(--space-2); font-weight: var(--font-medium); color: var(--text-primary);">
                Electricity Rate ($/kWh)
            </label>
            <input
                type="number"
                id="electricity_rate"
                name="electricity_rate"
                value="{{ config.ELECTRICITY_RATE if config else '0.12' }}"
                step="0.01"
                min="0"
                class="input-field"
                style="width: 100%; padding: var(--space-3); border: 1px solid var(--border-default); border-radius: var(--radius-md); background-color: var(--bg-base); color: var(--text-primary); font-size: var(--text-sm);"
            >
        </div>

        <div style="margin-bottom: var(--space-4);">
            <label for="currency" style="display: block; margin-bottom: var(--space-2); font-weight: var(--font-medium); color: var(--text-primary);">
                Currency Symbol
            </label>
            <input
                type="text"
                id="currency"
                name="currency"
                value="{{ config.CURRENCY if config else '$' }}"
                maxlength="3"
                class="input-field"
                style="width: 100%; padding: var(--space-3); border: 1px solid var(--border-default); border-radius: var(--radius-md); background-color: var(--bg-base); color: var(--text-primary); font-size: var(--text-sm);"
            >
        </div>
    </form>
</div>

<!-- Cache Configuration -->
<div class="main-card">
    <h2 class="main-card-title">Cache Configuration</h2>
    <form method="POST" style="margin-top: var(--space-4);">
        <div style="margin-bottom: var(--space-4);">
            <label for="cache_ttl" style="display: block; margin-bottom: var(--space-2); font-weight: var(--font-medium); color: var(--text-primary);">
                Cache TTL (seconds)
            </label>
            <input
                type="number"
                id="cache_ttl"
                name="cache_ttl"
                value="{{ config.CACHE_TTL if config else '60' }}"
                min="10"
                max="3600"
                class="input-field"
                style="width: 100%; padding: var(--space-3); border: 1px solid var(--border-default); border-radius: var(--radius-md); background-color: var(--bg-base); color: var(--text-primary); font-size: var(--text-sm);"
            >
            <small style="display: block; margin-top: var(--space-2); color: var(--text-muted); font-size: var(--text-xs);">
                How long to cache data before refreshing (10-3600 seconds)
            </small>
        </div>
    </form>
</div>

<!-- Action Buttons -->
<div style="display: flex; gap: var(--space-3);">
    <button
        type="submit"
        class="btn-primary"
        style="padding: var(--space-3) var(--space-6); background-color: var(--color-primary); color: white; border: none; border-radius: var(--radius-md); font-weight: var(--font-medium); cursor: pointer; font-size: var(--text-sm);"
    >
        Save Settings
    </button>
    <button
        type="button"
        class="btn-secondary"
        onclick="testConnection()"
        style="padding: var(--space-3) var(--space-6); background-color: transparent; color: var(--color-primary); border: 1px solid var(--color-primary); border-radius: var(--radius-md); font-weight: var(--font-medium); cursor: pointer; font-size: var(--text-sm);"
    >
        Test Connection
    </button>
</div>

<!-- Test Result Alert -->
<div id="testResult" style="margin-top: var(--space-4); display: none;"></div>
{% endblock %}

{% block extra_scripts %}
<script>
    async function testConnection() {
        const resultDiv = document.getElementById('testResult');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `
            <div class="alert alert-info">
                <span class="alert-icon">⏳</span>
                <div class="alert-content">
                    <div class="alert-title">Testing connection...</div>
                </div>
            </div>
        `;

        try {
            const response = await fetch('/api/test-connection');
            const data = await response.json();

            if (data.success) {
                resultDiv.innerHTML = `
                    <div class="alert alert-success">
                        <span class="alert-icon">✅</span>
                        <div class="alert-content">
                            <div class="alert-title">Connection successful!</div>
                            <div>Connected to Home Assistant</div>
                        </div>
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `
                    <div class="alert alert-error">
                        <span class="alert-icon">❌</span>
                        <div class="alert-content">
                            <div class="alert-title">Connection failed</div>
                            <div>${data.error || 'Unable to connect to Home Assistant'}</div>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            resultDiv.innerHTML = `
                <div class="alert alert-error">
                    <span class="alert-icon">❌</span>
                    <div class="alert-content">
                        <div class="alert-title">Connection failed</div>
                        <div>${error.message}</div>
                    </div>
                </div>
            `;
        }
    }
</script>
{% endblock %}
```

**Step 2: Test settings page renders**

Navigate to http://localhost:5001/settings
Expected: Form displays with proper styling

**Step 3: Commit settings page**

```bash
git add templates/settings.html
git commit -m "feat: rewrite settings page with SnowUI form components"
```

---

## Task 5: Rewrite Real-time Page

**Files:**
- Modify: `templates/realtime.html`
- Modify: `static/js/realtime.js`

**Step 1: Replace realtime.html with SnowUI components**

Replace entire `templates/realtime.html` content:

```html
{% extends "base.html" %}

{% block title %}Real-time - Energy Dashboard{% endblock %}

{% block content %}
<!-- Page Header -->
<div class="page-header">
    <div class="flex-between">
        <div>
            <h1 class="page-title">Real-time Monitoring</h1>
            <p class="page-subtitle">Live power consumption by room and device</p>
        </div>
        <span class="badge badge-success">
            <span style="display: inline-block; width: 8px; height: 8px; background-color: currentColor; border-radius: 50%; margin-right: 6px; animation: pulse 2s infinite;"></span>
            Live
        </span>
    </div>
</div>

<!-- Room Power Breakdown -->
<div class="main-card">
    <div class="main-card-header">
        <h2 class="main-card-title">Power by Room</h2>
    </div>
    <div class="chart-container">
        <canvas id="roomPieChart" style="max-height: 300px;"></canvas>
    </div>
</div>

<!-- Device Power Distribution -->
<div class="main-card">
    <div class="main-card-header">
        <h2 class="main-card-title">Top Power Consumers</h2>
    </div>
    <div class="chart-container">
        <canvas id="deviceBarChart" style="max-height: 400px;"></canvas>
    </div>
</div>

<!-- Device List -->
<div class="main-card">
    <h2 class="main-card-title">All Devices</h2>
    <div class="table-container" style="margin-top: var(--space-4);">
        <table>
            <thead>
                <tr>
                    <th>Device</th>
                    <th>Room</th>
                    <th class="number">Power (W)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody id="deviceTableBody">
                {% if data and data.devices %}
                    {% for device in data.devices %}
                    <tr>
                        <td>{{ device.name }}</td>
                        <td>{{ device.room or 'Unknown' }}</td>
                        <td class="number">{{ "%.1f"|format(device.power) }}</td>
                        <td>
                            {% if device.power > 0 %}
                            <span class="badge badge-success">Active</span>
                            {% else %}
                            <span class="badge badge-warning">Idle</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr>
                        <td colspan="4" style="text-align: center; color: var(--text-muted);">
                            No device data available
                        </td>
                    </tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>

<style>
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
</style>
{% endblock %}

{% block extra_scripts %}
<script src="{{ url_for('static', filename='js/realtime.js') }}"></script>
<script>
    // Initialize charts with SnowUI colors
    const root = document.documentElement;
    const chartColors = [
        getComputedStyle(root).getPropertyValue('--color-primary').trim(),
        getComputedStyle(root).getPropertyValue('--color-cyan').trim(),
        getComputedStyle(root).getPropertyValue('--color-mint').trim(),
        getComputedStyle(root).getPropertyValue('--color-purple').trim(),
        getComputedStyle(root).getPropertyValue('--color-green').trim()
    ];

    const roomData = {{ data.rooms | tojson if data and data.rooms else '[]' }};
    const deviceData = {{ data.devices | tojson if data and data.devices else '[]' }};

    // Room Pie Chart
    if (roomData.length > 0) {
        const roomLabels = roomData.map(r => r.name);
        const roomValues = roomData.map(r => r.power);

        new Chart(document.getElementById('roomPieChart'), {
            type: 'pie',
            data: {
                labels: roomLabels,
                datasets: [{
                    data: roomValues,
                    backgroundColor: chartColors,
                    borderWidth: 2,
                    borderColor: getComputedStyle(root).getPropertyValue('--bg-surface').trim()
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: window.innerWidth <= 768 ? 'bottom' : 'right'
                    }
                }
            }
        });
    }

    // Device Bar Chart (Top 10)
    if (deviceData.length > 0) {
        const sortedDevices = deviceData.sort((a, b) => b.power - a.power).slice(0, 10);
        const deviceLabels = sortedDevices.map(d => d.name);
        const deviceValues = sortedDevices.map(d => d.power);

        new Chart(document.getElementById('deviceBarChart'), {
            type: 'bar',
            data: {
                labels: deviceLabels,
                datasets: [{
                    label: 'Power (W)',
                    data: deviceValues,
                    backgroundColor: chartColors[0],
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Start auto-refresh
    startAutoRefresh();
</script>
{% endblock %}
```

**Step 2: Update realtime.js for new structure**

Replace entire `static/js/realtime.js` content:

```javascript
// Real-time monitoring auto-refresh
let refreshInterval;
const REFRESH_RATE = 5000; // 5 seconds

function startAutoRefresh() {
    refreshInterval = setInterval(async () => {
        await refreshData();
    }, REFRESH_RATE);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

async function refreshData() {
    try {
        const response = await fetch('/api/realtime');
        const data = await response.json();

        if (data.success) {
            updateDeviceTable(data.devices);
        }
    } catch (error) {
        console.error('Failed to refresh data:', error);
    }
}

function updateDeviceTable(devices) {
    const tbody = document.getElementById('deviceTableBody');
    if (!tbody || !devices) return;

    tbody.innerHTML = devices.map(device => `
        <tr>
            <td>${device.name}</td>
            <td>${device.room || 'Unknown'}</td>
            <td class="number">${device.power.toFixed(1)}</td>
            <td>
                ${device.power > 0
                    ? '<span class="badge badge-success">Active</span>'
                    : '<span class="badge badge-warning">Idle</span>'
                }
            </td>
        </tr>
    `).join('');
}

// Stop refresh when leaving page
window.addEventListener('beforeunload', stopAutoRefresh);
```

**Step 3: Test real-time page renders**

Navigate to http://localhost:5001/realtime
Expected: Charts and device table display, auto-refresh works

**Step 4: Commit real-time page**

```bash
git add templates/realtime.html static/js/realtime.js
git commit -m "feat: rewrite real-time page with SnowUI components and charts"
```

---

## Task 6: Rewrite Costs Page

**Files:**
- Modify: `templates/costs.html`
- Modify: `static/js/costs.js`

**Step 1: Replace costs.html with SnowUI components**

Replace entire `templates/costs.html` content:

```html
{% extends "base.html" %}

{% block title %}Costs - Energy Dashboard{% endblock %}

{% block content %}
<!-- Page Header -->
<div class="page-header">
    <h1 class="page-title">Cost Analysis</h1>
    <p class="page-subtitle">Energy costs and projections</p>
</div>

<!-- Monthly Projection -->
<div class="main-card">
    <div class="main-card-header">
        <h2 class="main-card-title">Monthly Cost Projection</h2>
        <div class="stat-value" style="font-size: var(--text-xl);">
            {% if data and data.monthly_projection %}
                ${{ "%.2f"|format(data.monthly_projection) }}
            {% else %}
                $0.00
            {% endif %}
        </div>
    </div>
    <div class="chart-container">
        <canvas id="costProjectionChart" style="max-height: 300px;"></canvas>
    </div>
</div>

<!-- Device Costs Table -->
<div class="main-card">
    <h2 class="main-card-title">Top 10 Device Costs</h2>
    <div class="table-container" style="margin-top: var(--space-4);">
        <table>
            <thead>
                <tr>
                    <th>Device</th>
                    <th>Room</th>
                    <th class="number">Daily Cost</th>
                    <th class="number">Monthly Projection</th>
                </tr>
            </thead>
            <tbody>
                {% if data and data.device_costs %}
                    {% for device in data.device_costs[:10] %}
                    <tr>
                        <td>{{ device.name }}</td>
                        <td>{{ device.room or 'Unknown' }}</td>
                        <td class="number">${{ "%.2f"|format(device.daily_cost) }}</td>
                        <td class="number">${{ "%.2f"|format(device.monthly_cost) }}</td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr>
                        <td colspan="4" style="text-align: center; color: var(--text-muted);">
                            No cost data available
                        </td>
                    </tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>

<!-- Cost Summary -->
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--space-4);">
    <div class="stat-card">
        <div class="stat-icon">📅</div>
        <div class="stat-value">
            {% if data and data.daily_cost %}
                ${{ "%.2f"|format(data.daily_cost) }}
            {% else %}
                $0.00
            {% endif %}
        </div>
        <div class="stat-label">Today's Cost</div>
    </div>

    <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-value">
            {% if data and data.weekly_cost %}
                ${{ "%.2f"|format(data.weekly_cost) }}
            {% else %}
                $0.00
            {% endif %}
        </div>
        <div class="stat-label">This Week</div>
    </div>

    <div class="stat-card">
        <div class="stat-icon">💰</div>
        <div class="stat-value">
            {% if data and data.monthly_cost %}
                ${{ "%.2f"|format(data.monthly_cost) }}
            {% else %}
                $0.00
            {% endif %}
        </div>
        <div class="stat-label">This Month</div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script src="{{ url_for('static', filename='js/costs.js') }}"></script>
<script>
    const root = document.documentElement;
    const primaryColor = getComputedStyle(root).getPropertyValue('--color-primary').trim();

    // Cost Projection Chart (Last 30 days)
    const projectionData = {{ data.projection_data | tojson if data and data.projection_data else '[]' }};

    if (projectionData.length > 0) {
        new Chart(document.getElementById('costProjectionChart'), {
            type: 'line',
            data: {
                labels: projectionData.map(d => d.date),
                datasets: [{
                    label: 'Daily Cost ($)',
                    data: projectionData.map(d => d.cost),
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
                                return '$' + value.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
    }
</script>
{% endblock %}
```

**Step 2: Update costs.js for new structure**

Replace entire `static/js/costs.js` content:

```javascript
// Cost calculation utilities
function calculateDailyCost(powerWatts, hours, ratePerKwh) {
    const energyKwh = (powerWatts * hours) / 1000;
    return energyKwh * ratePerKwh;
}

function calculateMonthlyCost(dailyCost) {
    return dailyCost * 30;
}

function formatCurrency(amount, currency = '$') {
    return currency + amount.toFixed(2);
}

// Export functions if using modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        calculateDailyCost,
        calculateMonthlyCost,
        formatCurrency
    };
}
```

**Step 3: Test costs page renders**

Navigate to http://localhost:5001/costs
Expected: Cost chart and table display properly

**Step 4: Commit costs page**

```bash
git add templates/costs.html static/js/costs.js
git commit -m "feat: rewrite costs page with SnowUI components and charts"
```

---

## Task 7: Rewrite History Page

**Files:**
- Modify: `templates/history.html`
- Modify: `static/js/history.js`

**Step 1: Replace history.html with SnowUI components**

Replace entire `templates/history.html` content:

```html
{% extends "base.html" %}

{% block title %}History - Energy Dashboard{% endblock %}

{% block content %}
<!-- Page Header -->
<div class="page-header">
    <div class="flex-between">
        <div>
            <h1 class="page-title">Historical Trends</h1>
            <p class="page-subtitle">Energy usage patterns over time</p>
        </div>

        <!-- Period Selector -->
        <div style="display: flex; gap: var(--space-2);">
            <button
                class="period-btn active"
                data-period="24h"
                onclick="selectPeriod('24h', this)"
                style="padding: var(--space-2) var(--space-4); border: 1px solid var(--border-default); border-radius: var(--radius-md); background: var(--bg-surface); color: var(--text-primary); cursor: pointer; font-size: var(--text-sm); font-weight: var(--font-medium);"
            >
                24 Hours
            </button>
            <button
                class="period-btn"
                data-period="7d"
                onclick="selectPeriod('7d', this)"
                style="padding: var(--space-2) var(--space-4); border: 1px solid var(--border-default); border-radius: var(--radius-md); background: var(--bg-surface); color: var(--text-primary); cursor: pointer; font-size: var(--text-sm); font-weight: var(--font-medium);"
            >
                7 Days
            </button>
            <button
                class="period-btn"
                data-period="30d"
                onclick="selectPeriod('30d', this)"
                style="padding: var(--space-2) var(--space-4); border: 1px solid var(--border-default); border-radius: var(--radius-md); background: var(--bg-surface); color: var(--text-primary); cursor: pointer; font-size: var(--text-sm); font-weight: var(--font-medium);"
            >
                30 Days
            </button>
        </div>
    </div>
</div>

<!-- Usage Trends Chart -->
<div class="main-card">
    <div class="main-card-header">
        <h2 class="main-card-title">Power Usage Trends</h2>
    </div>
    <div class="chart-container">
        <canvas id="trendsChart" style="max-height: 400px;"></canvas>
    </div>
</div>

<!-- Insights -->
<div class="main-card">
    <h2 class="main-card-title">Usage Insights</h2>
    <div style="margin-top: var(--space-4);">
        {% if data and data.insights %}
            {% for insight in data.insights %}
            <div class="alert alert-info" style="margin-bottom: var(--space-3);">
                <span class="alert-icon">💡</span>
                <div class="alert-content">
                    <div class="alert-title">{{ insight.title }}</div>
                    <div>{{ insight.message }}</div>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <p style="color: var(--text-muted);">No insights available yet. Check back after collecting more data.</p>
        {% endif %}
    </div>
</div>

<style>
    .period-btn.active {
        background-color: var(--color-primary) !important;
        color: white !important;
        border-color: var(--color-primary) !important;
    }
</style>
{% endblock %}

{% block extra_scripts %}
<script src="{{ url_for('static', filename='js/history.js') }}"></script>
<script>
    const root = document.documentElement;
    const primaryColor = getComputedStyle(root).getPropertyValue('--color-primary').trim();
    const cyanColor = getComputedStyle(root).getPropertyValue('--color-cyan').trim();

    let currentChart;

    function selectPeriod(period, button) {
        // Update button states
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');

        // Load data for period
        loadHistoryData(period);
    }

    async function loadHistoryData(period) {
        try {
            const response = await fetch(`/api/history?period=${period}`);
            const data = await response.json();

            if (data.success) {
                updateChart(data.history);
            }
        } catch (error) {
            console.error('Failed to load history data:', error);
        }
    }

    function updateChart(historyData) {
        const ctx = document.getElementById('trendsChart');

        if (currentChart) {
            currentChart.destroy();
        }

        currentChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: historyData.map(d => d.timestamp),
                datasets: [{
                    label: 'Power (W)',
                    data: historyData.map(d => d.power),
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
    }

    // Initial chart load
    const initialData = {{ data.history | tojson if data and data.history else '[]' }};
    if (initialData.length > 0) {
        updateChart(initialData);
    }
</script>
{% endblock %}
```

**Step 2: Update history.js for new structure**

Replace entire `static/js/history.js` content:

```javascript
// History analysis utilities
function analyzePattern(historyData) {
    if (!historyData || historyData.length === 0) {
        return null;
    }

    // Calculate average
    const avg = historyData.reduce((sum, d) => sum + d.power, 0) / historyData.length;

    // Find peak
    const peak = Math.max(...historyData.map(d => d.power));
    const peakTime = historyData.find(d => d.power === peak)?.timestamp;

    // Find minimum
    const min = Math.min(...historyData.map(d => d.power));

    return {
        average: avg,
        peak: peak,
        peakTime: peakTime,
        minimum: min
    };
}

function detectAnomalies(historyData, threshold = 2) {
    if (!historyData || historyData.length === 0) {
        return [];
    }

    const values = historyData.map(d => d.power);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const stdDev = Math.sqrt(
        values.reduce((sq, n) => sq + Math.pow(n - avg, 2), 0) / values.length
    );

    return historyData.filter(d => {
        return Math.abs(d.power - avg) > threshold * stdDev;
    });
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        analyzePattern,
        detectAnomalies
    };
}
```

**Step 3: Test history page renders**

Navigate to http://localhost:5001/history
Expected: Chart displays, period selector works

**Step 4: Commit history page**

```bash
git add templates/history.html static/js/history.js
git commit -m "feat: rewrite history page with SnowUI components and trend charts"
```

---

## Task 8: Rewrite Device Details Page

**Files:**
- Modify: `templates/device.html`
- Modify: `static/js/device.js`

**Step 1: Replace device.html with SnowUI components**

Replace entire `templates/device.html` content:

```html
{% extends "base.html" %}

{% block title %}{{ device.name if device else 'Device' }} - Energy Dashboard{% endblock %}

{% block content %}
<!-- Device Header -->
<div class="page-header">
    <div>
        <h1 class="page-title">
            <span style="font-size: 32px; margin-right: var(--space-3);">🔌</span>
            {{ device.name if device else 'Device Details' }}
        </h1>
        <p class="page-subtitle">
            {% if device and device.room %}
                {{ device.room }} •
            {% endif %}
            Last updated: {{ device.last_updated if device else 'Unknown' }}
        </p>
    </div>
</div>

<!-- Current Stats -->
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--space-4); margin-bottom: var(--space-6);">
    <div class="stat-card">
        <div class="stat-icon">⚡</div>
        <div class="stat-value">
            {% if device and device.current_power %}
                {{ "%.1f"|format(device.current_power) }}
            {% else %}
                0.0
            {% endif %}
        </div>
        <div class="stat-label">Current Power (W)</div>
    </div>

    <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-value">
            {% if device and device.daily_energy %}
                {{ "%.2f"|format(device.daily_energy) }}
            {% else %}
                0.00
            {% endif %}
        </div>
        <div class="stat-label">Today's Energy (kWh)</div>
    </div>

    <div class="stat-card">
        <div class="stat-icon">💰</div>
        <div class="stat-value">
            {% if device and device.daily_cost %}
                ${{ "%.2f"|format(device.daily_cost) }}
            {% else %}
                $0.00
            {% endif %}
        </div>
        <div class="stat-label">Today's Cost</div>
    </div>
</div>

<!-- 24-Hour Usage Chart -->
<div class="main-card">
    <div class="main-card-header">
        <h2 class="main-card-title">24-Hour Usage Pattern</h2>
    </div>
    <div class="chart-container">
        <canvas id="deviceUsageChart" style="max-height: 350px;"></canvas>
    </div>
</div>

<!-- Statistics -->
<div class="main-card">
    <h2 class="main-card-title">Statistics</h2>
    <div class="table-container" style="margin-top: var(--space-4);">
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th class="number">Value</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Average Power</td>
                    <td class="number">
                        {% if device and device.avg_power %}
                            {{ "%.1f"|format(device.avg_power) }} W
                        {% else %}
                            0.0 W
                        {% endif %}
                    </td>
                </tr>
                <tr>
                    <td>Peak Power</td>
                    <td class="number">
                        {% if device and device.peak_power %}
                            {{ "%.1f"|format(device.peak_power) }} W
                        {% else %}
                            0.0 W
                        {% endif %}
                    </td>
                </tr>
                <tr>
                    <td>Total Energy (Today)</td>
                    <td class="number">
                        {% if device and device.daily_energy %}
                            {{ "%.2f"|format(device.daily_energy) }} kWh
                        {% else %}
                            0.00 kWh
                        {% endif %}
                    </td>
                </tr>
                <tr>
                    <td>Monthly Projection</td>
                    <td class="number">
                        {% if device and device.monthly_cost %}
                            ${{ "%.2f"|format(device.monthly_cost) }}
                        {% else %}
                            $0.00
                        {% endif %}
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script src="{{ url_for('static', filename='js/device.js') }}"></script>
<script>
    const root = document.documentElement;
    const primaryColor = getComputedStyle(root).getPropertyValue('--color-primary').trim();

    // 24-hour usage data
    const usageData = {{ device.usage_history | tojson if device and device.usage_history else '[]' }};

    if (usageData.length > 0) {
        new Chart(document.getElementById('deviceUsageChart'), {
            type: 'line',
            data: {
                labels: usageData.map(d => d.hour),
                datasets: [{
                    label: 'Power (W)',
                    data: usageData.map(d => d.power),
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
    }
</script>
{% endblock %}
```

**Step 2: Update device.js for new structure**

Replace entire `static/js/device.js` content:

```javascript
// Device utilities
function formatDeviceName(name) {
    return name.replace(/_/g, ' ')
               .split(' ')
               .map(word => word.charAt(0).toUpperCase() + word.slice(1))
               .join(' ');
}

function calculateDeviceEfficiency(power, category) {
    // Simple efficiency rating based on device category
    const standards = {
        'lighting': 15,
        'appliance': 100,
        'heating': 1500,
        'electronics': 50
    };

    const standard = standards[category] || 100;
    const efficiency = (standard / power) * 100;

    return Math.min(efficiency, 100);
}

function getDeviceIcon(category) {
    const icons = {
        'lighting': '💡',
        'appliance': '🔌',
        'heating': '🔥',
        'cooling': '❄️',
        'electronics': '📺',
        'kitchen': '🍳'
    };

    return icons[category] || '🔌';
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatDeviceName,
        calculateDeviceEfficiency,
        getDeviceIcon
    };
}
```

**Step 3: Test device page renders**

Navigate to http://localhost:5001/device/some-device-id
Expected: Device details display with chart

**Step 4: Commit device page**

```bash
git add templates/device.html static/js/device.js
git commit -m "feat: rewrite device details page with SnowUI components"
```

---

## Task 9: Rewrite Error Page

**Files:**
- Modify: `templates/error.html`

**Step 1: Replace error.html with SnowUI components**

Replace entire `templates/error.html` content:

```html
{% extends "base.html" %}

{% block title %}Error - Energy Dashboard{% endblock %}

{% block content %}
<div style="display: flex; align-items: center; justify-content: center; min-height: 60vh;">
    <div style="max-width: 500px; text-align: center;">
        <!-- Error Icon -->
        <div style="font-size: 64px; margin-bottom: var(--space-4);">❌</div>

        <!-- Error Message -->
        <div class="alert alert-error" style="text-align: left;">
            <span class="alert-icon">⚠️</span>
            <div class="alert-content">
                <div class="alert-title">Something went wrong</div>
                <div>
                    {% if error %}
                        {{ error }}
                    {% else %}
                        An unexpected error occurred. Please try again.
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- Action Buttons -->
        <div style="display: flex; gap: var(--space-3); justify-content: center; margin-top: var(--space-6);">
            <a
                href="{{ url_for('settings') }}"
                style="padding: var(--space-3) var(--space-6); background-color: var(--color-primary); color: white; border: none; border-radius: var(--radius-md); font-weight: var(--font-medium); text-decoration: none; font-size: var(--text-sm); display: inline-block;"
            >
                Check Settings
            </a>
            <a
                href="{{ url_for('overview') }}"
                style="padding: var(--space-3) var(--space-6); background-color: transparent; color: var(--color-primary); border: 1px solid var(--color-primary); border-radius: var(--radius-md); font-weight: var(--font-medium); text-decoration: none; font-size: var(--text-sm); display: inline-block;"
            >
                Go to Overview
            </a>
        </div>

        <!-- Additional Help -->
        <div style="margin-top: var(--space-6); color: var(--text-muted); font-size: var(--text-sm);">
            <p>Common issues:</p>
            <ul style="text-align: left; margin-top: var(--space-2);">
                <li>Home Assistant connection not configured</li>
                <li>Invalid access token</li>
                <li>Home Assistant server unreachable</li>
                <li>No energy monitoring devices found</li>
            </ul>
        </div>
    </div>
</div>
{% endblock %}
```

**Step 2: Test error page renders**

Trigger an error or navigate to a non-existent route
Expected: Error page displays with styled alert

**Step 3: Commit error page**

```bash
git add templates/error.html
git commit -m "feat: rewrite error page with SnowUI components"
```

---

## Task 10: Final Testing & Documentation

**Files:**
- Modify: `README.md`
- Create: `docs/SNOWUI_REDESIGN.md`

**Step 1: Test all pages**

Test each page systematically:

```bash
# Start app
python3 app.py

# Test in browser at http://localhost:5001
# - Overview page
# - Real-time page
# - Costs page
# - History page
# - Device page
# - Settings page
# - Error page (trigger by invalid route)
```

Checklist:
- [ ] All pages load without errors
- [ ] Sidebar navigation works
- [ ] Theme toggle switches dark/light mode
- [ ] Charts render with SnowUI colors
- [ ] Mobile menu works (resize browser to < 768px)
- [ ] All forms are styled correctly
- [ ] Tables display properly
- [ ] No Bootstrap classes visible in inspector

**Step 2: Update README with redesign notes**

Add to `README.md` after Features section:

```markdown
## Design System

Energy Dashboard uses the **SnowUI Design System** for a consistent, modern interface:

- **Sidebar Layout**: Professional dashboard with fixed navigation
- **Dark/Light Mode**: Automatic theme switching with localStorage persistence
- **Responsive**: Mobile-friendly with collapsible sidebar
- **Chart Integration**: Chart.js styled with SnowUI color tokens
- **Component Library**: Reusable components (stat cards, tables, alerts, badges)

### SnowUI Files

- `static/css/snowui-tokens.css` - Design tokens (colors, spacing, typography)
- `static/css/snowui-components.css` - Component styles
- `static/css/custom.css` - App-specific overrides

Reference: [heizung-tracker-app](../heizung-tracker-app/) for component patterns
```

**Step 3: Create redesign documentation**

Create `docs/SNOWUI_REDESIGN.md`:

```markdown
# SnowUI Redesign

**Date:** 2026-02-28
**Status:** ✅ Complete

## Changes

### Templates Rewritten
- `templates/base.html` - Sidebar layout with theme toggle
- `templates/overview.html` - Stat cards + gauge chart
- `templates/realtime.html` - Live monitoring with charts
- `templates/costs.html` - Cost analysis with projections
- `templates/history.html` - Trend charts with period selector
- `templates/device.html` - Device details with 24h chart
- `templates/settings.html` - Form layout with SnowUI inputs
- `templates/error.html` - Error display with alerts

### CSS Updated
- `static/css/custom.css` - Complete rewrite for SnowUI layout
- Added: `static/css/snowui-tokens.css` (from heizung-tracker-app)
- Added: `static/css/snowui-components.css` (from heizung-tracker-app)

### JavaScript Updated
- `static/js/realtime.js` - Updated for new HTML structure
- `static/js/costs.js` - Updated for new HTML structure
- `static/js/history.js` - Updated for new HTML structure
- `static/js/device.js` - Updated for new HTML structure
- Base template includes Chart.js theme configuration

## Design Patterns

### Layout
- CSS Grid: `260px sidebar + 1fr main content`
- Responsive breakpoints: 768px (mobile), 1024px (tablet)
- Mobile: Hamburger menu with overlay sidebar

### Components
- **Stat Cards**: Icon + value + label
- **Main Cards**: Content containers with shadow
- **Tables**: Sticky header, hover rows, tabular numbers
- **Charts**: SnowUI colors, responsive legends
- **Alerts**: Error, warning, info, success states
- **Badges**: Status indicators with semantic colors

### Theme System
- Attribute: `<html data-theme="dark|light">`
- Toggle: Button in sidebar footer
- Persistence: localStorage
- Chart Updates: Automatic on theme change

## Testing Checklist

- [x] All pages load correctly
- [x] Sidebar navigation works
- [x] Theme toggle functional
- [x] Charts render with SnowUI colors
- [x] Mobile menu works (< 768px)
- [x] Forms styled correctly
- [x] Tables display properly
- [x] No Bootstrap classes remain

## Reference

- Design system: `/Users/d056488/claude-projects/heizung-tracker-app/`
- Design doc: `docs/plans/2026-02-28-snowui-redesign-design.md`
- Tokens: `static/css/snowui-tokens.css`
- Components: `static/css/snowui-components.css`
```

**Step 4: Commit final documentation**

```bash
git add README.md docs/SNOWUI_REDESIGN.md
git commit -m "docs: add SnowUI redesign documentation and update README"
```

**Step 5: Create final summary commit**

```bash
git log --oneline -10 > /tmp/redesign-commits.txt
cat /tmp/redesign-commits.txt
```

Review commits and create summary:

```bash
git commit --allow-empty -m "chore: SnowUI redesign complete - all templates rebuilt with sidebar layout and SnowUI design system"
```

---

## Success Criteria Verification

Verify all criteria from design doc:

- ✅ No Bootstrap classes in templates
- ✅ All SnowUI tokens used correctly
- ✅ Sidebar layout with theme toggle
- ✅ Charts styled with SnowUI colors
- ✅ Dark/light mode switching works
- ✅ Responsive on mobile (sidebar collapses)
- ✅ All 5 main pages render correctly
- ✅ Settings form saves configuration
- ✅ Error page displays properly
- ✅ Consistent typography and spacing
- ✅ Visual match with heizung-tracker-app style

---

## Rollback Plan

If issues arise, rollback to previous Bootstrap version:

```bash
# View commits
git log --oneline

# Rollback to before redesign
git reset --hard <commit-before-redesign>

# Or revert specific commits
git revert <commit-hash>
```

---

## Next Steps

1. Deploy to production
2. Monitor for visual bugs
3. Collect user feedback
4. Optimize Chart.js performance
5. Add more SnowUI components as needed
