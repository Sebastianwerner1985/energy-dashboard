# Energy Dashboard SnowUI Redesign - Design Document

**Date:** 2026-02-28
**Status:** Approved
**Approach:** Complete template rewrite with SnowUI design system

---

## Problem Statement

The Energy Dashboard was initially implemented with Bootstrap classes and a non-existent `@snowui/core` CDN link. The templates use Bootstrap components (navbar, cards, buttons) which don't align with the SnowUI design system used in other projects (heizung-tracker-app).

**Issues:**
- Non-functional SnowUI CDN reference
- Bootstrap classes throughout templates
- Top navbar instead of sidebar layout
- Inconsistent with SnowUI design patterns
- Visual appearance doesn't match SnowUI aesthetic

---

## Design Goals

1. **Full SnowUI Integration**: Use proper SnowUI CSS variables and component patterns
2. **Consistency**: Match heizung-tracker-app's design language and layout
3. **Professional Dashboard**: Sidebar layout optimized for energy monitoring
4. **Theme Support**: Dark/light mode with seamless switching
5. **Responsive**: Mobile-friendly with collapsible sidebar
6. **Chart Integration**: Chart.js styled with SnowUI tokens

---

## Approach: Complete Rewrite

**Decision:** Rebuild all templates from scratch following the heizung-tracker-app pattern.

**Rationale:**
- Clean slate avoids Bootstrap remnants
- Faster than incremental refactor
- Ensures consistency across all pages
- Templates are straightforward (5 pages + base)

**Alternatives Considered:**
- Incremental refactor: Too much work, inconsistent during transition
- CSS override: Creates technical debt, doesn't fix structure issues

---

## Architecture

### Base Template Structure

```
<html data-theme="dark|light">
  <head>
    - Google Fonts: Inter
    - /static/css/snowui-tokens.css
    - /static/css/snowui-components.css
    - /static/css/custom.css
    - Chart.js CDN
  </head>
  <body>
    <div class="app-container">
      <aside class="sidebar">
        - Logo/app name header
        - Navigation links
        - Theme toggle (bottom)
      </aside>
      <main class="main-content">
        {% block content %}
      </main>
    </div>
  </body>
</html>
```

### Layout System

**CSS Grid Layout:**
```css
.app-container {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
}
```

**Sidebar:**
- Fixed width: 260px
- Background: `var(--bg-surface)`
- Border-right: `var(--border-default)`
- Vertical navigation links
- Theme toggle at bottom

**Main Content:**
- Flexible width
- Background: `var(--bg-base)`
- Scrollable overflow
- Padding: `var(--space-6)`

---

## Component Patterns

### 1. Stat Cards (Overview Page)

**Structure:**
```html
<div class="stat-card">
  <div class="stat-icon">⚡</div>
  <div class="stat-value">1234.5</div>
  <div class="stat-label">Current Power (W)</div>
</div>
```

**Styling:**
- Background: `var(--bg-surface)`
- Shadow: `var(--shadow-medium)`
- Border-radius: `var(--radius-lg)`
- Padding: `var(--space-5)`

### 2. Main Cards (Page Containers)

**Structure:**
```html
<div class="main-card">
  <h2 class="text-lg font-semibold">Section Title</h2>
  <!-- Content -->
</div>
```

**Styling:**
- Background: `var(--bg-surface)`
- Border-radius: `var(--radius-xl)`
- Padding: `var(--space-6)`
- Shadow: `var(--shadow-medium)`

### 3. Tables

**Structure:**
```html
<div class="table-container">
  <table>
    <thead>
      <tr><th>Column</th></tr>
    </thead>
    <tbody>
      <tr><td>Data</td></tr>
    </tbody>
  </table>
</div>
```

**Styling:**
- Border: `var(--border-default)`
- Border-radius: `var(--radius-md)`
- Sticky header: `var(--bg-surface-overlay)`
- Row hover: `var(--bg-surface-overlay)`
- Tabular numbers for data columns

### 4. Buttons

Use SnowUI predefined classes:
- `.btn-primary`: Primary actions
- `.btn-secondary`: Secondary actions
- `.btn-ghost`: Tertiary actions

### 5. Navigation Links

**Active State:**
- Background: `var(--bg-accent-primary)`
- Text: `var(--color-primary)`
- Border-left accent

**Hover State:**
- Background: `var(--bg-surface-overlay)`

---

## Page Layouts

### Overview Page
- Grid: 4 stat cards (2x2)
- Gauge chart: Current power usage
- Quick navigation cards to other pages

### Real-time Monitoring
- Pie chart: Room power breakdown
- Horizontal bar chart: Device power distribution
- Auto-refresh indicator
- Live data badge

### Cost Analysis
- Line chart: Monthly cost projection
- Table: Top 10 device costs
- Total cost summary card

### Historical Trends
- Time period selector (24h, 7d, 30d)
- Multi-line chart: Usage trends
- Insights list: Pattern analysis

### Device Details
- Device header with icon and name
- Line chart: 24h usage pattern
- Statistics grid: Total usage, avg power, cost

### Settings
- Form sections:
  - Home Assistant connection
  - Energy configuration (rate, currency)
  - Cache settings (TTL)
- Save button (primary)
- Test connection button (secondary)

### Error Page
- Error alert card (`.alert-error`)
- Error icon and message
- Action buttons: "Check Settings", "Go Home"
- Maintains sidebar for consistency

---

## Chart.js Integration

### Theme Configuration

**Default Colors (applied via JavaScript):**
```javascript
Chart.defaults.color = getComputedStyle(document.documentElement)
  .getPropertyValue('--text-secondary');

Chart.defaults.borderColor = getComputedStyle(document.documentElement)
  .getPropertyValue('--border-default');
```

### Chart Color Palette

Use SnowUI chart colors:
1. `var(--color-primary)` - #4c98fd (blue)
2. `var(--color-cyan)` - #a0bce8
3. `var(--color-mint)` - #6be6d3
4. `var(--color-purple)` - #b899eb
5. `var(--color-green)` - #71dd8c

### Chart Types by Page

| Page | Chart Type | Purpose |
|------|------------|---------|
| Overview | Gauge/Doughnut | Current power usage |
| Real-time | Pie + Horizontal Bar | Room & device breakdown |
| Costs | Line + Bar | Projections & device costs |
| History | Multi-line | Usage trends over time |
| Device | Line | 24h usage pattern |

### Responsive Configuration

- Maintain aspect ratio
- Legend position: bottom (mobile), right (desktop)
- Font sizes scale with viewport
- Tooltips use `var(--bg-surface)` with shadow

### Theme Switching

- JavaScript listens for theme changes
- Updates Chart.js default colors
- Charts redraw with new theme colors
- Smooth transition without flicker

---

## Responsive Design

### Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| ≤768px | Sidebar collapses to hamburger menu overlay |
| 769-1024px | Sidebar width: 200px |
| ≥1025px | Sidebar width: 260px (full) |

### Mobile Menu

**Collapsed State:**
- Hamburger icon (☰) top-left
- Full-width main content

**Expanded State:**
- Overlay sidebar slides from left
- Dark backdrop over main content
- Close button (✕) in sidebar
- Click outside to dismiss

### Mobile Adaptations

**Stat Cards:**
- Stack vertically (single column)
- Full width

**Charts:**
- Full width container
- Legends move to bottom
- Smaller font sizes

**Tables:**
- Horizontal scroll
- Sticky first column
- Compact padding

**Forms:**
- Full width inputs
- Stacked form groups

---

## Error Handling & States

### Error Messages

**Template:** `error.html`

**Components:**
- Error alert card (`.alert-error`)
- Error icon (❌) + message
- Error details (if available)
- Action buttons: "Check Settings", "Go Home"

**Styling:**
- Color: `var(--color-error)`
- Background: `rgba(var(--color-error-rgb), 0.1)` or `var(--bg-accent-error)`
- Border: `var(--color-error)`

### Empty States

**No data available:**
- Info alert (`.alert-info`)
- Message: "No data available. Check your Home Assistant connection."
- Link to Settings

**Loading:**
- Centered spinner with SnowUI colors
- Loading text below spinner
- Subtle animation

### Connection Issues

**Alert Banner:**
- Top of page, dismissible
- Warning color: `var(--color-warning)`
- Message: "Connection to Home Assistant failed. Retrying..."
- Retry action button

---

## Theme Switching

### Implementation

**HTML Attribute:**
```html
<html data-theme="dark">
```

**JavaScript Toggle:**
```javascript
function toggleTheme() {
  const html = document.documentElement;
  const currentTheme = html.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  updateChartTheme(newTheme);
}
```

**Persistence:**
- Save to `localStorage` on toggle
- Load on page init
- Default: dark mode

**Visual Indicator:**
- Button icon: 🌙 (dark mode), ☀️ (light mode)
- Button location: Bottom of sidebar
- Smooth transition: 0.3s ease

---

## File Changes

### Templates to Rewrite

1. `templates/base.html` - Complete restructure
2. `templates/overview.html` - Stat cards + gauge
3. `templates/realtime.html` - Charts + device list
4. `templates/costs.html` - Cost charts + table
5. `templates/history.html` - Trend charts + selector
6. `templates/device.html` - Device details + chart
7. `templates/settings.html` - Form layout
8. `templates/error.html` - Error display

### CSS Files

**Keep:**
- `static/css/snowui-tokens.css` ✅ (already copied)
- `static/css/snowui-components.css` ✅ (already copied)

**Rewrite:**
- `static/css/custom.css` - App-specific styles and overrides

### JavaScript Files

**Update:**
- `static/js/realtime.js` - Update for new HTML structure
- `static/js/costs.js` - Update for new HTML structure
- `static/js/history.js` - Update for new HTML structure
- `static/js/device.js` - Update for new HTML structure

**Add:**
- Chart.js theme configuration in `base.html` inline script

### Python/Flask

**No changes required:**
- Routes remain the same
- Data structure unchanged
- Only template rendering affected

---

## Implementation Order

1. **Base Template** - Foundation for all pages
2. **Custom CSS** - App-specific styles and layout
3. **Overview Page** - Simplest page, good starting point
4. **Settings Page** - No charts, test forms
5. **Real-time Page** - Test charts + auto-refresh
6. **Costs Page** - Test tables + charts
7. **History Page** - Test time selectors
8. **Device Page** - Test dynamic routing
9. **Error Page** - Test error handling
10. **JavaScript Updates** - Fix chart interactions
11. **Mobile Testing** - Verify responsive behavior
12. **Theme Testing** - Verify dark/light switching

---

## Success Criteria

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

## Testing Plan

### Visual Testing
- [ ] Compare each page with heizung-tracker-app reference
- [ ] Verify colors match SnowUI tokens
- [ ] Check spacing consistency
- [ ] Test dark/light theme toggle

### Functional Testing
- [ ] All navigation links work
- [ ] Charts render correctly
- [ ] Auto-refresh works on real-time page
- [ ] Forms submit and validate
- [ ] Error states display properly

### Responsive Testing
- [ ] Test on mobile (≤768px)
- [ ] Test on tablet (769-1024px)
- [ ] Test on desktop (≥1025px)
- [ ] Verify hamburger menu works
- [ ] Check chart responsiveness

### Browser Testing
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari

---

## Notes

- Reference heizung-tracker-app templates for component patterns
- Use existing Flask routes (no backend changes)
- Maintain Chart.js version 4.x compatibility
- Keep Home Assistant integration unchanged
- Preserve existing data processing logic

---

## Next Steps

Create implementation plan using `writing-plans` skill to break this design into actionable tasks.
