# SnowUI Design System Redesign

## Overview

This document details the complete redesign of the Energy Dashboard using the **SnowUI Design System**, transforming it from a basic Bootstrap interface to a modern, professional dashboard with sophisticated styling and enhanced user experience.

## Design Goals

1. **Professional Appearance**: Modern sidebar layout with polished visual design
2. **Dark/Light Mode**: Full theme support with instant switching
3. **Responsive Design**: Mobile-first approach with collapsible navigation
4. **Consistent Components**: Reusable UI components across all pages
5. **Chart Integration**: Seamless Chart.js styling with SnowUI tokens
6. **Performance**: Efficient CSS with minimal overhead

## Architecture

### CSS Structure

The SnowUI system consists of three CSS files:

```
static/css/
├── snowui-tokens.css       # Design tokens (colors, spacing, typography)
├── snowui-components.css   # Component library (cards, buttons, tables)
└── custom.css              # App-specific overrides and layouts
```

### Load Order

Critical load order in `base.html`:

```html
<!-- SnowUI Design System -->
<link rel="stylesheet" href="/static/css/snowui-tokens.css">
<link rel="stylesheet" href="/static/css/snowui-components.css">
<link rel="stylesheet" href="/static/css/custom.css">
```

## Design Tokens (`snowui-tokens.css`)

### Color System

**Light Theme**:
- Primary: Blue (#3b82f6)
- Surface: White (#ffffff) / Light Gray (#f9fafb)
- Text: Dark Gray (#111827)

**Dark Theme**:
- Primary: Blue (#3b82f6)
- Surface: Dark Gray (#1f2937) / Darker Gray (#111827)
- Text: Light Gray (#f9fafb)

### Token Categories

1. **Colors**: Primary, surface, text, borders
2. **Spacing**: Scale from 0.5rem to 4rem (8px-64px)
3. **Typography**: Font sizes (sm/base/lg/xl/2xl/3xl)
4. **Borders**: Radius scale (sm/md/lg/full)
5. **Shadows**: Elevation levels (sm/md/lg)

### Theme Switching

Automatic theme switching via `data-theme` attribute:

```javascript
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}
```

## Component Library (`snowui-components.css`)

### Stat Card Component

Modern card with icon, value, and label:

```html
<div class="stat-card">
    <div class="stat-icon">⚡</div>
    <div class="stat-value">1,234 kWh</div>
    <div class="stat-label">Total Usage</div>
</div>
```

**Features**:
- Icon with circular background
- Large value display
- Descriptive label
- Hover elevation effect
- Theme-aware colors

### Button System

Four button variants:

```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-outline">Outline</button>
<button class="btn btn-ghost">Ghost</button>
```

**Features**:
- Consistent padding and spacing
- Hover and active states
- Disabled state styling
- Theme-adaptive colors

### Table Component

Enhanced table with striping and hover:

```html
<table class="table">
    <thead>
        <tr>
            <th>Column 1</th>
            <th>Column 2</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Data 1</td>
            <td>Data 2</td>
        </tr>
    </tbody>
</table>
```

**Features**:
- Striped rows
- Hover highlighting
- Proper spacing
- Responsive scrolling

### Alert Component

Four alert types:

```html
<div class="alert alert-info">Information message</div>
<div class="alert alert-success">Success message</div>
<div class="alert alert-warning">Warning message</div>
<div class="alert alert-error">Error message</div>
```

### Badge Component

Status indicators:

```html
<span class="badge">Default</span>
<span class="badge badge-success">Active</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-error">Error</span>
```

## Custom Layout (`custom.css`)

### Sidebar Layout

Fixed sidebar navigation with responsive behavior:

**Desktop** (≥768px):
- Sidebar: 240px fixed width
- Main content: Adjusts with left margin
- Theme toggle in sidebar footer

**Mobile** (<768px):
- Sidebar: Off-canvas (hidden by default)
- Hamburger menu button appears
- Overlay when sidebar open

### Sidebar Structure

```html
<aside class="sidebar">
    <div class="sidebar-header">
        <div class="sidebar-logo">⚡</div>
        <div class="sidebar-title">Energy</div>
        <div class="sidebar-subtitle">Dashboard</div>
    </div>
    <nav class="sidebar-nav">
        <a href="/overview" class="nav-item active">
            <span class="nav-icon">📊</span>
            <span class="nav-text">Overview</span>
        </a>
    </nav>
    <div class="sidebar-footer">
        <button class="theme-toggle-btn">☀️</button>
    </div>
</aside>
```

### Main Content Area

```html
<main class="main-content">
    <div class="content-wrapper">
        <!-- Page content -->
    </div>
</main>
```

**Features**:
- Max width: 1200px for readability
- Centered with auto margins
- Padding: 2rem (responsive)

## Page-Specific Implementations

### 1. Base Template (`base.html`)

**Changes**:
- Complete HTML structure rewrite
- SnowUI CSS imports
- Sidebar navigation layout
- Theme toggle JavaScript
- Mobile menu toggle JavaScript
- Active navigation highlighting

**Key Features**:
- Theme persistence via localStorage
- Responsive sidebar
- Page title in header bar
- Google Fonts (Inter)

### 2. Overview Page (`overview.html`)

**Layout**:
- 4 stat cards in responsive grid
- Gauge chart with SnowUI colors
- Top consumers table
- Quick navigation cards

**Components Used**:
- `stat-card`
- `card`
- `table`
- `btn-primary`

### 3. Real-time Page (`realtime.html`)

**Layout**:
- Hero stat card (total power)
- Auto-refresh badge
- Two-column chart grid
- Device table

**Components Used**:
- `stat-card`
- `badge badge-success`
- `card`
- `table`

**JavaScript Integration**:
- Chart.js with SnowUI colors
- Auto-refresh timer
- Theme-aware chart updates

### 4. Costs Page (`costs.html`)

**Layout**:
- Cost stat cards grid
- Projection cards
- Cost chart
- Device costs table

**Components Used**:
- `stat-card`
- `card`
- `table`

### 5. History Page (`history.html`)

**Layout**:
- Period selector buttons
- Stats grid
- Trend chart
- Insights alert boxes

**Components Used**:
- `btn-group`
- `stat-card`
- `card`
- `alert alert-info`

**JavaScript**:
- Period switching
- Chart updates
- Theme-aware colors

### 6. Device Details Page (`device.html`)

**Layout**:
- Device header with back button
- Stats grid
- 24-hour usage chart

**Components Used**:
- `btn-secondary`
- `stat-card`
- `card`

### 7. Settings Page (`settings.html`)

**Layout**:
- Form sections with headings
- Input groups with labels
- Action buttons

**Components Used**:
- `card`
- `form-group`
- `form-input`
- `btn-primary`
- `btn-secondary`

**Features**:
- Connection test functionality
- Form validation
- Success/error alerts

### 8. Error Page (`error.html`)

**Layout**:
- Centered error container
- Error icon and code
- Error message
- Back button

**Components Used**:
- `error-container`
- `btn-primary`

## Chart.js Integration

### Theme-Aware Chart Colors

Charts automatically adapt to current theme:

```javascript
function getChartColors() {
    const theme = document.documentElement.getAttribute('data-theme');
    if (theme === 'dark') {
        return {
            primary: '#3b82f6',
            text: '#f9fafb',
            grid: 'rgba(255, 255, 255, 0.1)'
        };
    } else {
        return {
            primary: '#3b82f6',
            text: '#111827',
            grid: 'rgba(0, 0, 0, 0.1)'
        };
    }
}
```

### Color Palette

8-color palette for data visualization:
- Blue (#3b82f6)
- Green (#10b981)
- Yellow (#f59e0b)
- Red (#ef4444)
- Purple (#8b5cf6)
- Pink (#ec4899)
- Indigo (#6366f1)
- Teal (#14b8a6)

## Responsive Breakpoints

### Mobile (<768px)
- Single column layouts
- Sidebar off-canvas
- Full-width cards
- Reduced padding

### Tablet (768px-1024px)
- Two-column grids
- Sidebar visible
- Medium padding

### Desktop (≥1024px)
- Multi-column grids
- Full sidebar
- Maximum padding

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

**Requirements**:
- CSS Custom Properties (CSS Variables)
- CSS Grid
- Flexbox
- LocalStorage API

## Performance Optimizations

1. **Minimal CSS**: ~15KB total (uncompressed)
2. **No CSS Framework**: No Bootstrap or Tailwind overhead
3. **Efficient Selectors**: Class-based styling
4. **Theme Switching**: Instant via CSS variables
5. **Chart Caching**: Chart instances reused

## Accessibility

- Semantic HTML elements
- ARIA labels on interactive elements
- Keyboard navigation support
- Sufficient color contrast ratios
- Focus indicators on interactive elements

## Migration from Bootstrap

### Before (Bootstrap)
```html
<div class="container">
    <div class="row">
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Total Power</h5>
                    <p class="card-text">1,234 W</p>
                </div>
            </div>
        </div>
    </div>
</div>
```

### After (SnowUI)
```html
<div class="content-wrapper">
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-value">1,234 W</div>
            <div class="stat-label">Total Power</div>
        </div>
    </div>
</div>
```

## Component Reference

### Layout Components
- `.sidebar` - Fixed sidebar navigation
- `.main-content` - Main content area
- `.content-wrapper` - Content container
- `.top-bar` - Header bar with mobile menu
- `.mobile-overlay` - Mobile sidebar overlay

### Display Components
- `.stat-card` - Metric display card
- `.card` - Content card
- `.table` - Data table
- `.alert` - Alert message
- `.badge` - Status badge

### Form Components
- `.form-group` - Form field wrapper
- `.form-label` - Field label
- `.form-input` - Text input
- `.form-select` - Dropdown select
- `.form-checkbox` - Checkbox

### Button Components
- `.btn` - Base button
- `.btn-primary` - Primary action
- `.btn-secondary` - Secondary action
- `.btn-outline` - Outline variant
- `.btn-ghost` - Ghost variant

### Grid Components
- `.stats-grid` - Stat cards grid
- `.chart-grid` - Charts grid
- `.two-col` - Two-column layout

## Testing Checklist

### Visual Testing
- [ ] Sidebar renders correctly
- [ ] Theme toggle switches colors
- [ ] Mobile menu works
- [ ] All pages render without errors
- [ ] Charts display with correct colors
- [ ] Tables are responsive
- [ ] Forms are properly styled

### Functional Testing
- [ ] Navigation between pages
- [ ] Theme persistence across page loads
- [ ] Mobile sidebar toggle
- [ ] Auto-refresh works
- [ ] Form submissions
- [ ] Error page displays

### Browser Testing
- [ ] Chrome desktop
- [ ] Firefox desktop
- [ ] Safari desktop
- [ ] Mobile Safari
- [ ] Chrome Mobile

## Future Enhancements

1. **Animation System**: Smooth transitions and micro-interactions
2. **Loading States**: Skeleton screens and spinners
3. **Toast Notifications**: Non-blocking notifications
4. **Modal Dialogs**: Confirm actions and display details
5. **Data Export**: Export data in CSV/JSON formats
6. **Chart Customization**: User-configurable chart types
7. **Widget System**: Draggable dashboard widgets

## Resources

- **Reference App**: `heizung-tracker-app` (sibling directory)
- **Chart.js Docs**: https://www.chartjs.org/
- **CSS Variables**: https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties
- **Flexbox**: https://css-tricks.com/snippets/css/a-guide-to-flexbox/
- **CSS Grid**: https://css-tricks.com/snippets/css/complete-guide-grid/

## Credits

- **Design System**: Based on SnowUI patterns from heizung-tracker-app
- **Icons**: Unicode emoji characters
- **Fonts**: Google Fonts (Inter)
- **Charts**: Chart.js library

## Version History

### v1.0.0 (2026-02-28)
- Initial SnowUI implementation
- Complete redesign of all pages
- Dark/light theme support
- Responsive sidebar layout
- Chart.js integration
- Mobile-friendly design

---

**Redesign Date**: February 28, 2026
**Pages Updated**: 8 (base, overview, realtime, costs, history, device, settings, error)
**CSS Files**: 3 (tokens, components, custom)
**Total CSS**: ~15KB
**Design System**: SnowUI
