# Energy Dashboard

A comprehensive Flask web application for monitoring home energy consumption through Home Assistant integration. Features real-time monitoring, cost analysis, historical trends, and device-level insights with a modern SnowUI interface.

## Features

- **Real-time Monitoring**: Live power consumption by room and device with auto-refresh
- **Cost Analysis**: Track daily, monthly, and annual energy costs with projections
- **Historical Trends**: Visualize usage patterns over 24 hours, 7 days, or 30 days
- **Device Details**: Detailed metrics and statistics for individual devices
- **SnowUI Design**: Modern, responsive interface with dark/light mode support
- **Smart Caching**: Efficient data caching with configurable TTL
- **Chart Visualizations**: Interactive Chart.js graphs and gauges

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

## Screenshots

The dashboard includes five main pages:
- Overview: Summary statistics and top consumers
- Real-time: Live monitoring with room breakdown
- Costs: Cost analysis and device cost breakdown
- History: Historical trends with insights
- Device Details: Individual device statistics and usage patterns

## Requirements

- Python 3.9 or higher
- Home Assistant instance with REST API access
- Power monitoring sensors configured in Home Assistant (W or kW)
- Long-lived access token from Home Assistant

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd energy-dashboard
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

Required packages:
- Flask >= 2.3.0
- requests >= 2.31.0
- python-dateutil >= 2.8.0

### 3. Configure Home Assistant

#### Option A: Environment Variables (Recommended)

```bash
export HA_URL="http://homeassistant.local:8123"
export HA_TOKEN="your-long-lived-access-token"
export ELECTRICITY_RATE="0.12"
export CURRENCY_SYMBOL="$"
```

#### Option B: Configuration File

Edit `config.py` directly or create a `.env` file:

```python
HA_URL = "http://homeassistant.local:8123"
HA_TOKEN = "your-long-lived-access-token"
ELECTRICITY_RATE = 0.12  # Cost per kWh
CURRENCY_SYMBOL = "$"
REFRESH_INTERVAL = 30  # Seconds
CACHE_TTL = 60  # Seconds
DEBUG = False
```

### 4. Get Home Assistant Access Token

1. Open Home Assistant
2. Click on your profile (bottom left)
3. Scroll down to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Give it a name (e.g., "Energy Dashboard")
6. Copy the token and use it in your configuration

### 5. Run the Application

```bash
python3 app.py
```

The application will start on `http://localhost:5000`

## Configuration Options

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `HA_URL` | Home Assistant URL | Required | `http://homeassistant.local:8123` |
| `HA_TOKEN` | Access token | Required | `eyJ0eXAiOiJKV1...` |
| `ELECTRICITY_RATE` | Cost per kWh | `0.12` | `0.15` |
| `CURRENCY_SYMBOL` | Currency symbol | `$` | `€`, `£`, `¥` |
| `REFRESH_INTERVAL` | Auto-refresh interval (seconds) | `30` | `60` |
| `CACHE_TTL` | Cache duration for real-time data | `60` | `120` |
| `HISTORY_CACHE_TTL` | Cache duration for historical data | `300` | `600` |
| `DEBUG` | Enable debug mode | `True` | `False` |
| `SECRET_KEY` | Flask secret key | Auto-generated | Custom string |

## Home Assistant Setup

### Required Sensors

Your Home Assistant must have power monitoring sensors that provide measurements in watts (W) or kilowatts (kW). Common integrations:

- **Energy Monitoring Devices**: Shelly Plug, TP-Link Kasa, Sonoff
- **Smart Meters**: Utility company integrations
- **Solar Systems**: Enphase, SolarEdge, Fronius
- **Whole Home Monitors**: Sense, Emporia Vue

### Sensor Format

Sensors should follow this format:
- Entity ID: `sensor.{location}_{device}_power`
- Unit: `W` or `kW`
- Example: `sensor.living_room_tv_power`

### Room Organization

The dashboard automatically organizes devices by room based on:
1. Friendly name (e.g., "Living Room TV")
2. Entity ID (e.g., `sensor.living_room_tv_power`)

Common room names detected:
- Living Room, Bedroom, Kitchen, Bathroom
- Office, Garage, Basement, Attic
- Dining Room, Laundry

## Usage

### Overview Page

- Quick summary of total power, daily energy, and costs
- Power usage gauge showing current consumption
- Top 5 energy consumers
- Quick navigation to other pages

### Real-time Monitoring

- Live total power display
- Room-by-room power breakdown (pie chart)
- Complete device list with current power readings
- Device power distribution (bar chart)
- Auto-refresh every 30 seconds (configurable)

### Cost Analysis

- Current hourly, daily, and monthly costs
- Monthly and annual projections
- Top 10 device cost breakdown
- Cost per device with daily/monthly/annual calculations

### Historical Trends

- View usage over 24 hours, 7 days, or 30 days
- Usage pattern analysis
- Peak, average, and minimum power statistics
- Key insights and recommendations

### Device Details

- Individual device monitoring
- 24-hour usage chart
- Current, average, and peak power
- Cost calculations (hourly, daily, monthly, annual)
- Device status and state

## Project Structure

```
energy-dashboard/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
├── .gitignore            # Git ignore rules
├── services/
│   ├── home_assistant.py  # Home Assistant API client
│   └── data_processor.py  # Data processing and caching
├── utils/
│   └── logger.py         # Logging configuration
├── templates/
│   ├── base.html         # Base template with SnowUI
│   ├── overview.html     # Overview page
│   ├── realtime.html     # Real-time monitoring
│   ├── costs.html        # Cost analysis
│   ├── history.html      # Historical trends
│   ├── device.html       # Device details
│   ├── settings.html     # Settings page
│   └── error.html        # Error page
└── static/
    ├── css/
    │   └── custom.css    # Custom styles
    └── js/
        ├── realtime.js   # Real-time utilities
        ├── costs.js      # Cost utilities
        ├── history.js    # History utilities
        └── device.js     # Device utilities
```

## API Endpoints

The application provides REST API endpoints for dynamic updates:

- `GET /api/realtime` - Get current real-time data
- `GET /api/device/<device_id>` - Get device-specific data

## Troubleshooting

### Connection Issues

**Problem**: "Connection test failed" or "Device not found"

**Solutions**:
1. Verify Home Assistant is running and accessible
2. Check the URL format (include `http://` or `https://`)
3. Ensure the access token is valid and not expired
4. Verify network connectivity between devices

### No Data Displayed

**Problem**: Dashboard shows zero values or "No data available"

**Solutions**:
1. Confirm power sensors exist in Home Assistant
2. Check sensor units are W, kW, or Wh, kWh
3. Verify sensors are updating (check Home Assistant)
4. Review logs for API errors: `tail -f logs/energy_dashboard.log`

### Historical Data Missing

**Problem**: History page shows no data

**Solutions**:
1. Check Home Assistant recorder is enabled
2. Verify database size limits not exceeded
3. Ensure sensors have sufficient history
4. Try a shorter time period (24h instead of 30d)

### High Memory Usage

**Solutions**:
1. Reduce `CACHE_TTL` values in config
2. Decrease `REFRESH_INTERVAL`
3. Limit number of monitored sensors
4. Use a reverse proxy with caching

## Development

### Running in Debug Mode

```bash
export DEBUG=True
python3 app.py
```

### Logging

Logs are stored in `logs/energy_dashboard.log` with rotation:
- Maximum size: 10 MB
- Backup count: 5 files
- Format: `timestamp - name - level - message`

### Extending Functionality

The modular architecture makes it easy to extend:

1. **Add new pages**: Create template in `templates/` and route in `app.py`
2. **Add data sources**: Extend `HomeAssistantClient` in `services/home_assistant.py`
3. **Add visualizations**: Use Chart.js in templates
4. **Customize caching**: Modify `DataProcessor` in `services/data_processor.py`

## Performance

- **Caching**: Intelligent caching reduces API calls to Home Assistant
- **Lazy Loading**: Data fetched only when needed
- **Background Refresh**: Auto-refresh runs client-side
- **Optimized Queries**: Efficient API requests with filtering

## Security

- **Token Security**: Never commit tokens to version control
- **HTTPS**: Use HTTPS for production deployments
- **Secret Key**: Set custom `SECRET_KEY` in production
- **Firewall**: Restrict access to trusted networks

## Production Deployment

### Using Gunicorn

```bash
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker (Example)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "app.py"]
```

### Reverse Proxy (Nginx Example)

```nginx
server {
    listen 80;
    server_name energy.example.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. See LICENSE file for details.

## Support

- **Documentation**: See this README
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join GitHub Discussions

## Credits

- **Flask**: Web framework
- **SnowUI**: UI design system
- **Chart.js**: Data visualization
- **Home Assistant**: Smart home platform

## Changelog

### Version 1.0.0 (2026-02-28)

- Initial release
- Five main dashboard pages
- Real-time monitoring
- Cost analysis
- Historical trends
- Device details
- Dark/light mode
- Responsive design
