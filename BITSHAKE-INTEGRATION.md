# Bitshake Whole-House Meter Integration

## Overview

The Energy Dashboard now properly integrates the Bitshake whole-house electricity meter, which measures total household consumption. This prevents double-counting and clearly shows unmonitored consumption.

## Problem Statement

**Before:**
- Bitshake entities were treated as regular devices
- Total power was sum of all devices (including bitshake)
- This caused double-counting since bitshake = all devices + untracked
- No visibility into unmonitored consumption

**User Explanation:**
> "The bitshake entities are live consumption for the whole house. They should be excluded from all others. The difference between bitshake and all other is the consumption that I can't track with Matter sockets."

## Solution

### Power Calculation Logic

```
Total Power (Bitshake)    = 256.0W  ← Whole house meter
Tracked Devices           = 223.0W  ← Sum of Matter sockets
Untracked Consumption     = 33.0W   ← Difference (12.9% of total)
```

**Untracked** represents devices not monitored by Matter sockets:
- Hardwired appliances
- Lighting circuits
- Built-in systems
- Any devices without smart plugs

### Implementation Details

#### 1. **Device Filtering**
All data processing functions now:
- Detect bitshake entities by name: `'bitshake' in entity_id.lower()`
- Separate bitshake from regular devices
- Use bitshake value as true total power
- Only count Matter socket devices in tracked totals

**Files Modified:**
- `services/data_processor.py`:
  - `get_overview_data()` - Filter bitshake from device count and top consumers
  - `get_realtime_data()` - Calculate tracked vs untracked, add "Untracked" room
  - `get_cost_data()` - Use bitshake for total, exclude from device costs

#### 2. **Realtime Page Enhancement**

**New Display (3 Cards):**
```
⚡ Total Power (W)        → 256.0W (Bitshake reading)
📦 Tracked Devices (W)    → 223.0W (Sum of Matter sockets)
❓ Untracked (W)          → 33.0W  (Highlighted in warning color)
```

**Auto-Refresh:**
- All three values update every 5 seconds
- Untracked card has warning border when > 0W
- Shows percentage of total that's unmonitored

#### 3. **Room Breakdown**

**"Untracked" as Virtual Room:**
- Appears in room list when untracked > 0W
- Shows in pie charts and room breakdowns
- Helps identify monitoring gaps

**Example Output:**
```
Rooms: 12
📍 Heizung: 22.3W
📍 Schlafzimmer: 12.0W
📍 Other: 117.7W
📍 Wohnzimmer: 6.0W
📍 Galerie: 35.8W
📍 Büro: 12.7W
📍 Garage: 3.8W
📍 Badezimmer: 3.4W
📍 Dachboden: 0.3W
📍 Küche: 4.7W
📍 Flur: 4.1W
❓ Untracked: 33.0W  ← Virtual room for unmonitored consumption
```

#### 4. **Cost Calculations**

**Uses Bitshake for Accuracy:**
- Daily cost based on bitshake total power
- Hourly cost projection uses bitshake
- Device costs only show tracked devices (not bitshake itself)

This ensures cost calculations reflect true consumption, not just tracked devices.

## Identified Bitshake Entities

The system automatically detects these entities:

```
Name: Bitshake Aktueller Verbrauch
ID:   sensor.bitshake_aktueller_verbrauch
Power: 256.0W

Name: bitShake SmartMeterReader MT175 Power
ID:   sensor.bitshake_smartmeterreader_mt175_power
Power: 256.0W
```

**Detection Logic:** Any entity with "bitshake" in entity_id or friendly_name (case-insensitive)

## Benefits

### 1. **Accurate Totals**
- Total power = actual whole-house consumption (from meter)
- No more double-counting
- Reflects real electricity usage

### 2. **Monitoring Gaps Visible**
- Untracked consumption clearly displayed
- Helps identify which devices need smart plugs
- Shows percentage of household not monitored

### 3. **Better Cost Accuracy**
- Costs based on real consumption (bitshake)
- Not just sum of tracked devices
- Matches actual electricity bill

### 4. **Cleaner Device Lists**
- Bitshake not shown as a "device"
- Device count = actual monitored devices (59 not 61)
- Top consumers list more meaningful

## Example Scenarios

### Scenario 1: All Devices Monitored
```
Total:      500W
Tracked:    500W
Untracked:  0W
→ Perfect monitoring! All consumption accounted for.
```

### Scenario 2: Some Untracked (Current)
```
Total:      256W
Tracked:    223W
Untracked:  33W (12.9%)
→ 13% of consumption unmonitored. Add smart plugs to reduce.
```

### Scenario 3: Mostly Untracked
```
Total:      800W
Tracked:    200W
Untracked:  600W (75%)
→ Need more monitoring! Most devices not tracked.
```

## Technical Details

### Data Structure Changes

**API Response (`/api/realtime`):**
```json
{
  "total_power": 256.0,        // ← From bitshake
  "tracked_power": 223.0,      // ← Sum of devices
  "untracked_power": 33.0,     // ← Difference
  "bitshake_power": 256.0,     // ← Bitshake raw value
  "devices": [...],            // ← Excludes bitshake
  "rooms": [
    {"name": "Heizung", "power": 22.3},
    ...
    {"name": "Untracked", "power": 33.0}  // ← Virtual room
  ]
}
```

### Fallback Behavior

**If no bitshake detected:**
- Uses sum of tracked devices as total
- Untracked = 0W
- Everything works as before

**If bitshake available:**
- Uses bitshake as total (more accurate)
- Calculates untracked consumption
- Shows monitoring coverage

## Testing Results

```
🔍 Testing Bitshake Integration...

1. Power Breakdown:
   Total (Bitshake):  256.0W
   Tracked (Devices): 223.0W
   Untracked:         33.0W
   ✅ Bitshake detected: 256.0W

2. Tracked Devices: 59
   ✅ Bitshake properly excluded from device list

3. Rooms: 12
   [11 real rooms + 1 Untracked virtual room]

4. Untracked Consumption: 12.9% of total
   ℹ️  This represents devices not monitored by Matter sockets

✅ Bitshake integration complete!
```

## Future Enhancements

### Potential Improvements:

1. **Monitoring Coverage Percentage**
   - Show: "87.1% of your home is monitored"
   - Encourage reaching 100%

2. **Untracked Device Identification**
   - Suggest which devices might be untracked
   - Time-based analysis to identify patterns

3. **Historical Untracked Trends**
   - Track how untracked consumption changes
   - Identify if monitoring coverage is improving

4. **Smart Plug Recommendations**
   - "Add 2 more smart plugs to reach 95% coverage"
   - ROI calculation for additional monitoring

## Summary

The bitshake integration provides:
- ✅ Accurate whole-house consumption tracking
- ✅ Clear visibility into unmonitored devices
- ✅ No double-counting
- ✅ Better cost calculations
- ✅ Monitoring coverage metrics

**Current Status:**
- Total: 256W (from bitshake meter)
- Tracked: 223W (87% coverage)
- Untracked: 33W (13% unmonitored)

This helps identify which additional devices should be monitored to improve energy tracking coverage.

---

**Last Updated:** 2026-02-28 16:30 CET
**Status:** ✅ Fully Implemented and Tested
