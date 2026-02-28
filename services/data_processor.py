"""
Data Processing and Caching Service
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dateutil import parser
import time
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and cache energy data from Home Assistant"""

    def __init__(self, ha_client, cache_ttl: int = 60):
        """
        Initialize data processor

        Args:
            ha_client: HomeAssistantClient instance
            cache_ttl: Cache time-to-live in seconds
        """
        self.ha_client = ha_client
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._cache_timestamps = {}

    def _get_cached(self, key: str) -> Optional[Dict]:
        """
        Get cached data if still valid

        Args:
            key: Cache key

        Returns:
            Cached data or None if expired/missing
        """
        if key in self._cache:
            timestamp = self._cache_timestamps.get(key, 0)
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(f"Cache hit: {key}")
                return self._cache[key]
            else:
                logger.debug(f"Cache expired: {key}")

        return None

    def _set_cache(self, key: str, data: Dict):
        """
        Store data in cache

        Args:
            key: Cache key
            data: Data to cache
        """
        self._cache[key] = data
        self._cache_timestamps[key] = time.time()
        logger.debug(f"Cache set: {key}")

    def get_overview_data(self) -> Dict:
        """
        Get overview dashboard data

        Returns:
            Dictionary with overview statistics
        """
        cached = self._get_cached('overview')
        if cached:
            return cached

        power_sensors = self.ha_client.get_power_sensors()
        energy_sensors = self.ha_client.get_energy_sensors()

        # Calculate total current power
        total_power = self._calculate_total_power(power_sensors)

        # Get top consumers
        top_consumers = self._get_top_consumers(power_sensors, limit=5)

        # Calculate daily energy consumption
        daily_energy = self._calculate_daily_energy(energy_sensors)

        # Get device count
        device_count = len(power_sensors)

        data = {
            'total_power': total_power,
            'daily_energy': daily_energy,
            'device_count': device_count,
            'top_consumers': top_consumers,
            'timestamp': datetime.now().isoformat()
        }

        self._set_cache('overview', data)
        return data

    def get_realtime_data(self) -> Dict:
        """
        Get real-time monitoring data

        Returns:
            Dictionary with current power usage by room and device
        """
        cached = self._get_cached('realtime')
        if cached:
            return cached

        power_sensors = self.ha_client.get_power_sensors()
        rooms = self.ha_client.get_devices_by_room()

        # Calculate power by room
        room_power = {}
        for room, sensors in rooms.items():
            room_power[room] = sum(
                self._parse_power(sensor) for sensor in sensors
            )

        # Format device list with room information
        devices = []
        for sensor in power_sensors:
            friendly_name = sensor.get('attributes', {}).get('friendly_name', sensor['entity_id'])
            entity_id = sensor['entity_id']
            room = self.ha_client._extract_room(friendly_name, entity_id)

            devices.append({
                'id': entity_id,
                'name': friendly_name,
                'room': room,
                'power': self._parse_power(sensor),
                'unit': sensor.get('attributes', {}).get('unit_of_measurement', 'W'),
                'state': sensor['state']
            })

        data = {
            'room_power': room_power,
            'rooms': [{'name': room, 'power': power} for room, power in room_power.items()],
            'devices': devices,
            'total_power': sum(room_power.values()),
            'timestamp': datetime.now().isoformat()
        }

        self._set_cache('realtime', data)
        return data

    def get_cost_data(self) -> Dict:
        """
        Get cost analysis data

        Returns:
            Dictionary with cost breakdowns and projections
        """
        cached = self._get_cached('costs')
        if cached:
            return cached

        energy_sensors = self.ha_client.get_energy_sensors()
        power_sensors = self.ha_client.get_power_sensors()

        # Get electricity rate from config (should be passed in, but using default for now)
        rate = 0.12  # $ per kWh

        # Calculate daily cost
        daily_energy = self._calculate_daily_energy(energy_sensors)
        daily_cost = daily_energy * rate

        # Calculate current power cost per hour
        current_power = self._calculate_total_power(power_sensors)
        hourly_cost = (current_power / 1000) * rate

        # Project monthly cost
        monthly_projection = daily_cost * 30

        # Calculate cost by device
        device_costs = []
        for sensor in power_sensors:
            friendly_name = sensor.get('attributes', {}).get('friendly_name', sensor['entity_id'])
            entity_id = sensor['entity_id']
            power = self._parse_power(sensor)

            if power > 0:
                room = self.ha_client._extract_room(friendly_name, entity_id)
                device_costs.append({
                    'name': friendly_name,
                    'room': room,
                    'power': power,
                    'daily_cost': (power / 1000) * 24 * rate,
                    'monthly_cost': (power / 1000) * 24 * 30 * rate
                })

        # Sort by monthly cost
        device_costs.sort(key=lambda x: x['monthly_cost'], reverse=True)

        # Generate projection data (last 30 days estimate)
        projection_data = []
        for i in range(30, 0, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            projection_data.append({
                'date': date,
                'cost': daily_cost  # Using average daily cost as estimate
            })

        data = {
            'daily_cost': daily_cost,
            'weekly_cost': daily_cost * 7,
            'monthly_cost': daily_cost * 30,
            'hourly_cost': hourly_cost,
            'monthly_projection': monthly_projection,
            'device_costs': device_costs[:10],  # Top 10
            'projection_data': projection_data,
            'rate': rate,
            'timestamp': datetime.now().isoformat()
        }

        self._set_cache('costs', data)
        return data

    def get_history_data(self, period: str = '24h') -> Dict:
        """
        Get historical trend data

        Args:
            period: Time period ('24h', '7d', '30d')

        Returns:
            Dictionary with historical data
        """
        cache_key = f'history_{period}'
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        # Parse period
        hours = self._parse_period(period)
        start_time = datetime.now() - timedelta(hours=hours)

        power_sensors = self.ha_client.get_power_sensors()

        # Get history for main power sensor (assuming first one is main)
        if not power_sensors:
            return {
                'history': [],
                'labels': [],
                'values': [],
                'period': period,
                'insights': [],
                'timestamp': datetime.now().isoformat()
            }

        main_sensor = power_sensors[0]
        history_raw = self.ha_client.get_history(
            main_sensor['entity_id'],
            start_time.isoformat()
        )

        # Process history data
        history = []

        for entry in history_raw:
            try:
                timestamp = parser.parse(entry['last_changed'])
                power = float(entry['state'])
                history.append({
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M'),
                    'power': power
                })
            except (ValueError, KeyError):
                continue

        data = {
            'history': history,
            'labels': [h['timestamp'] for h in history],
            'values': [h['power'] for h in history],
            'period': period,
            'sensor_name': main_sensor.get('attributes', {}).get('friendly_name', 'Power'),
            'timestamp': datetime.now().isoformat(),
            'insights': []
        }

        self._set_cache(cache_key, data)
        return data

    def get_device_data(self, device_id: str) -> Dict:
        """
        Get detailed data for a specific device

        Args:
            device_id: Device entity ID

        Returns:
            Dictionary with device details
        """
        cache_key = f'device_{device_id}'
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        # Get current state
        state = self.ha_client.get_state(device_id)

        if not state:
            raise ValueError(f"Device not found: {device_id}")

        # Get 24h history
        start_time = datetime.now() - timedelta(hours=24)
        history = self.ha_client.get_history(device_id, start_time.isoformat())

        # Process history
        labels = []
        values = []

        for entry in history:
            try:
                timestamp = parser.parse(entry['last_changed'])
                power = float(entry['state'])
                labels.append(timestamp.strftime('%H:%M'))
                values.append(power)
            except (ValueError, KeyError):
                continue

        # Calculate statistics
        current_power = self._parse_power(state)
        avg_power = sum(values) / len(values) if values else 0
        max_power = max(values) if values else 0
        daily_energy = (avg_power / 1000) * 24  # kWh

        data = {
            'device_id': device_id,
            'name': state.get('attributes', {}).get('friendly_name', device_id),
            'current_power': current_power,
            'average_power': avg_power,
            'max_power': max_power,
            'daily_energy': daily_energy,
            'unit': state.get('attributes', {}).get('unit_of_measurement', 'W'),
            'state': state['state'],
            'labels': labels,
            'values': values,
            'timestamp': datetime.now().isoformat()
        }

        self._set_cache(cache_key, data)
        return data

    def _calculate_total_power(self, sensors: List[Dict]) -> float:
        """Calculate total power from sensors"""
        return sum(self._parse_power(sensor) for sensor in sensors)

    def _parse_power(self, sensor: Dict) -> float:
        """
        Parse power value from sensor state

        Args:
            sensor: Sensor state dictionary

        Returns:
            Power value in watts
        """
        try:
            state = sensor['state']
            if state in ['unknown', 'unavailable', 'none', None]:
                return 0.0

            value = float(state)
            unit = sensor.get('attributes', {}).get('unit_of_measurement', 'W')

            # Convert to watts
            if unit in ['kW', 'kilowatt']:
                value *= 1000

            return value
        except (ValueError, KeyError):
            return 0.0

    def _get_top_consumers(self, sensors: List[Dict], limit: int = 5) -> List[Dict]:
        """
        Get top power consuming devices

        Args:
            sensors: List of power sensors
            limit: Number of top consumers to return

        Returns:
            List of top consuming devices
        """
        consumers = [
            {
                'name': sensor.get('attributes', {}).get('friendly_name', sensor['entity_id']),
                'power': self._parse_power(sensor),
                'entity_id': sensor['entity_id']
            }
            for sensor in sensors
            if self._parse_power(sensor) > 0
        ]

        consumers.sort(key=lambda x: x['power'], reverse=True)
        return consumers[:limit]

    def _calculate_daily_energy(self, sensors: List[Dict]) -> float:
        """
        Calculate total daily energy consumption (today only)

        Args:
            sensors: List of energy sensors

        Returns:
            Daily energy in kWh (today's consumption, not cumulative)
        """
        total = 0.0

        # Get midnight today as start time
        now = datetime.now()
        midnight = datetime(now.year, now.month, now.day, 0, 0, 0)

        for sensor in sensors:
            try:
                entity_id = sensor.get('entity_id')
                if not entity_id:
                    continue

                # Get history from midnight to now
                history = self.ha_client.get_history(entity_id, midnight.isoformat())

                if history and len(history) > 0:
                    states = history  # history is already the states list

                    # Get first state after midnight (or current if only one)
                    first_value = None
                    for state in states:
                        try:
                            if state['state'] not in ['unknown', 'unavailable', 'none', None]:
                                first_value = float(state['state'])
                                break
                        except (ValueError, KeyError):
                            continue

                    # Get latest state
                    current_state = sensor['state']
                    if current_state not in ['unknown', 'unavailable', 'none', None] and first_value is not None:
                        current_value = float(current_state)

                        # Calculate difference (today's consumption)
                        daily_value = current_value - first_value

                        # Convert to kWh if needed
                        unit = sensor.get('attributes', {}).get('unit_of_measurement', 'kWh')
                        if unit == 'Wh':
                            daily_value /= 1000

                        # Only add positive values (in case sensor was reset)
                        if daily_value > 0:
                            total += daily_value

            except (ValueError, KeyError, IndexError) as e:
                logger.debug(f"Error calculating daily energy for sensor: {e}")
                continue

        return total

    def _parse_period(self, period: str) -> int:
        """
        Parse period string to hours

        Args:
            period: Period string ('24h', '7d', '30d')

        Returns:
            Number of hours
        """
        period_map = {
            '24h': 24,
            '7d': 168,
            '30d': 720
        }

        return period_map.get(period, 24)

    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Cache cleared")
