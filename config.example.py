"""
Example configuration for Energy Dashboard
Copy this file to config.py and update with your settings
"""
import os

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Home Assistant settings
# Get your long-lived access token from Home Assistant Profile
HA_URL = os.environ.get('HA_URL', 'http://homeassistant.local:8123')
HA_TOKEN = os.environ.get('HA_TOKEN', 'your-home-assistant-token-here')

# Energy monitoring settings
# Your electricity rate in currency per kWh
ELECTRICITY_RATE = float(os.environ.get('ELECTRICITY_RATE', '0.12'))
CURRENCY_SYMBOL = os.environ.get('CURRENCY_SYMBOL', '$')

# Cache settings (in seconds)
# How long to cache real-time data
CACHE_TTL = int(os.environ.get('CACHE_TTL', '60'))
# How long to cache historical data
HISTORY_CACHE_TTL = int(os.environ.get('HISTORY_CACHE_TTL', '300'))

# Application settings
# How often to auto-refresh real-time page (in seconds)
REFRESH_INTERVAL = int(os.environ.get('REFRESH_INTERVAL', '30'))

# Example for different regions:
# UK: ELECTRICITY_RATE = 0.28, CURRENCY_SYMBOL = '£'
# EU: ELECTRICITY_RATE = 0.25, CURRENCY_SYMBOL = '€'
# US: ELECTRICITY_RATE = 0.12, CURRENCY_SYMBOL = '$'
