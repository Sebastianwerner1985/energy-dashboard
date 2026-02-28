"""
Configuration settings for Energy Dashboard
"""
import os

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Home Assistant settings
HA_URL = os.environ.get('HA_URL', 'http://homeassistant.local:8123')
HA_TOKEN = os.environ.get('HA_TOKEN', '')

# Validate required configuration
if not HA_TOKEN:
    import sys
    print("ERROR: HA_TOKEN environment variable is required", file=sys.stderr)
    print("Set it with: export HA_TOKEN='your-token-here'", file=sys.stderr)
    print("Or create a .env file with HA_TOKEN=your-token", file=sys.stderr)
    sys.exit(1)

# Energy monitoring settings
ELECTRICITY_RATE = float(os.environ.get('ELECTRICITY_RATE', '0.12'))  # $ per kWh
CURRENCY_SYMBOL = os.environ.get('CURRENCY_SYMBOL', '$')

# Cache settings
CACHE_TTL = int(os.environ.get('CACHE_TTL', '60'))  # seconds
HISTORY_CACHE_TTL = int(os.environ.get('HISTORY_CACHE_TTL', '300'))  # seconds

# Application settings
REFRESH_INTERVAL = int(os.environ.get('REFRESH_INTERVAL', '30'))  # seconds for auto-refresh
