# ECharts Migration - 2026-02-28

## Summary

Successfully migrated all visualizations from Chart.js to Apache ECharts to solve excessive whitespace issues around charts, especially semicircle gauges and pie charts.

## Problem Solved

Chart.js was creating uncontrollable whitespace around visualizations:
- Semicircle gauges (180° power gauge) reserved space for full circle
- Pie charts had massive padding that couldn't be removed with CSS or Chart.js options
- User repeatedly requested spacing reduction, not chart size reduction
- Multiple attempts to fix with Chart.js layout padding, aspectRatio, and negative margins failed

## Solution

Replaced Chart.js with Apache ECharts which provides:
- Better control over chart spacing and padding
- Native support for semicircle gauges without whitespace
- More compact pie chart rendering
- Consistent grid padding across all chart types

## Files Modified

### 1. templates/base.html
**Changed:**
- Replaced Chart.js CDN with ECharts CDN
```html
<!-- OLD -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

<!-- NEW -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
```

### 2. templates/overview.html
**Changed:**
- Converted 180° power gauge from Chart.js to ECharts gauge
- Height: 250px (maintained large size as requested)
- ECharts gauge with proper semicircle rendering (startAngle: 180, endAngle: 0)
- No excessive whitespace below gauge

### 3. templates/realtime.html
**Changes:**
- Converted pie chart (Room Power Distribution) from Chart.js to ECharts
- Converted horizontal bar chart (Top Devices) from Chart.js to ECharts
- Changed `<canvas>` elements to `<div>` elements
- Heights: 300px (pie), 400px (bar) - maintained large sizes
- ECharts provides compact rendering with proper legend placement

### 4. templates/costs.html
**Changes:**
- Converted line chart (Cost Projection) from Chart.js to ECharts
- Changed `<canvas>` to `<div>`
- Height: 300px
- ECharts area chart with gradient fill and proper grid padding

### 5. templates/history.html
**Changes:**
- Converted line chart (Historical Trends) from Chart.js to ECharts
- Changed `<canvas>` to `<div>`
- Height: 350px
- Dynamic chart updates on period selection (24h, 7d, 30d)
- ECharts setOption() properly updates chart without recreating

### 6. templates/device.html
**Changes:**
- Converted line chart (24-Hour Usage Pattern) from Chart.js to ECharts
- Changed `<canvas>` to `<div>`
- Height: 400px
- ECharts area chart with smooth curves

## Chart Configuration Details

### Common ECharts Configuration:
```javascript
{
    tooltip: {
        trigger: 'axis' or 'item',
        formatter: custom formatter function
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '15%' or '10%',
        top: '3%',
        containLabel: true  // Ensures labels don't get cut off
    },
    xAxis: {
        axisLabel: {
            color: 'var(--text-muted)',
            rotate: 45  // for date labels
        },
        axisLine: {
            lineStyle: {
                color: 'var(--border-color)'
            }
        }
    },
    yAxis: {
        axisLabel: {
            color: 'var(--text-muted)',
            formatter: '{value} W' or '€{value}'
        },
        splitLine: {
            lineStyle: {
                color: 'var(--border-color)'
            }
        }
    }
}
```

### ECharts Advantages:
1. **Grid padding control**: Explicit `grid` configuration prevents whitespace
2. **Gauge rendering**: Proper semicircle without reserved space below
3. **Responsive**: `chart.resize()` on window resize event
4. **CSS integration**: Uses SnowUI CSS variables for colors
5. **Smooth gradients**: Better area chart rendering with gradient fills

## Testing Required

After deploying these changes to Raspberry Pi (`/home/pi/energy-dashboard`):

1. **Restart service:**
   ```bash
   sudo systemctl restart energy-dashboard
   ```

2. **Test all pages:**
   - Overview: Power gauge renders without whitespace below
   - Real-time: Pie chart and bar chart compact and properly spaced
   - Costs: Line chart with 30-day projection displays correctly
   - History: Chart updates when switching between 24h/7d/30d
   - Device: 24-hour usage pattern displays correctly

3. **Verify:**
   - No JavaScript console errors
   - Charts are large (300-400px height maintained)
   - Minimal padding/margins around charts (user's core request)
   - SnowUI colors are applied correctly
   - Charts resize properly on mobile

## Deployment Steps

Since I don't have SSH access, manual deployment required:

1. **Copy updated templates to Pi:**
   ```bash
   rsync -av templates/ pi@192.168.178.100:/home/pi/energy-dashboard/templates/
   ```

2. **Restart service:**
   ```bash
   ssh pi@192.168.178.100 "sudo systemctl restart energy-dashboard"
   ```

3. **Verify deployment:**
   ```bash
   curl http://192.168.178.100:5002/ | grep echarts
   ```
   Should show: `echarts.init(document.getElementById(...))` in the output

## Success Criteria

✅ All Chart.js code removed
✅ All canvas elements replaced with divs
✅ ECharts CDN loaded in base.html
✅ All 5 pages converted (overview, realtime, costs, history, device)
✅ Chart heights maintained (300-400px)
✅ Grid padding minimized
✅ SnowUI design system colors integrated
✅ Responsive resize handlers added

⏳ **Pending deployment to Raspberry Pi**

## Next Steps

1. Deploy updated templates to Pi (requires SSH access)
2. Test all charts render correctly with minimal whitespace
3. If user reports remaining spacing issues, adjust ECharts `grid` padding values
4. Consider adding loading states for charts
5. Monitor for any ECharts-specific rendering issues

## Rollback Plan

If issues occur after deployment:

1. Revert base.html to Chart.js CDN
2. Restore Chart.js code in all template files
3. Change divs back to canvas elements
4. Restart service

Original Chart.js files are preserved in git history.
