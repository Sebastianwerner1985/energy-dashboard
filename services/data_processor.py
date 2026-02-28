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

        # Separate bitshake from tracked devices
        bitshake_power = 0
        tracked_sensors = []

        for sensor in power_sensors:
            entity_id = sensor['entity_id']
            friendly_name = sensor.get('attributes', {}).get('friendly_name', entity_id)

            if 'bitshake' in entity_id.lower() or 'bitshake' in friendly_name.lower():
                bitshake_power = self._parse_power(sensor)
            else:
                tracked_sensors.append(sensor)

        # Use bitshake as total power, or sum of tracked if no bitshake
        total_power = bitshake_power if bitshake_power > 0 else self._calculate_total_power(tracked_sensors)

        # Get top consumers (from tracked devices only)
        top_consumers = self._get_top_consumers(tracked_sensors, limit=5)

        # Calculate daily energy consumption
        daily_energy = self._calculate_daily_energy(energy_sensors)

        # Device count (tracked devices only, exclude bitshake)
        device_count = len(tracked_sensors)

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

        # Separate bitshake (whole-house meter) from tracked devices
        bitshake_power = 0
        tracked_sensors = []

        for sensor in power_sensors:
            entity_id = sensor['entity_id']
            friendly_name = sensor.get('attributes', {}).get('friendly_name', entity_id)

            # Check if this is a bitshake entity (whole-house meter)
            if 'bitshake' in entity_id.lower() or 'bitshake' in friendly_name.lower():
                bitshake_power = self._parse_power(sensor)
            else:
                tracked_sensors.append(sensor)

        # Calculate power by room (only tracked devices)
        rooms = {}
        for sensor in tracked_sensors:
            friendly_name = sensor.get('attributes', {}).get('friendly_name', sensor['entity_id'])
            entity_id = sensor['entity_id']
            room = self.ha_client._extract_room(friendly_name, entity_id)

            if room not in rooms:
                rooms[room] = 0
            rooms[room] += self._parse_power(sensor)

        # Calculate tracked vs untracked
        tracked_total = sum(rooms.values())
        untracked_power = max(0, bitshake_power - tracked_total)

        # Add untracked to rooms if there's any
        if untracked_power > 0:
            rooms['Untracked'] = untracked_power

        # Format device list with room information (tracked devices only)
        devices = []
        for sensor in tracked_sensors:
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
            'room_power': rooms,
            'rooms': [{'name': room, 'power': power} for room, power in rooms.items()],
            'devices': devices,
            'total_power': bitshake_power if bitshake_power > 0 else tracked_total,  # Use bitshake as true total
            'tracked_power': tracked_total,
            'untracked_power': untracked_power,
            'bitshake_power': bitshake_power,
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
        rate = 0.26  # € per kWh

        # Separate bitshake from tracked devices
        bitshake_power = 0
        tracked_sensors = []

        for sensor in power_sensors:
            entity_id = sensor['entity_id']
            friendly_name = sensor.get('attributes', {}).get('friendly_name', entity_id)

            if 'bitshake' in entity_id.lower() or 'bitshake' in friendly_name.lower():
                bitshake_power = self._parse_power(sensor)
            else:
                tracked_sensors.append(sensor)

        # Use bitshake for calculations if available, otherwise tracked total
        current_power = bitshake_power if bitshake_power > 0 else self._calculate_total_power(tracked_sensors)

        # Calculate daily cost
        daily_energy = self._calculate_daily_energy(energy_sensors)
        daily_cost = daily_energy * rate

        # Calculate current power cost per hour
        hourly_cost = (current_power / 1000) * rate

        # Project monthly cost
        monthly_projection = daily_cost * 30

        # Calculate cost by device (tracked devices only, not bitshake)
        device_costs = []
        for sensor in tracked_sensors:
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

        # Process history data - aggregate by day
        daily_data = {}

        for entry in history_raw:
            try:
                timestamp = parser.parse(entry['last_changed'])
                power = float(entry['state'])

                # Group by date only (ignore time)
                date_key = timestamp.strftime('%Y-%m-%d')

                if date_key not in daily_data:
                    daily_data[date_key] = {
                        'count': 0,
                        'total': 0,
                        'max': 0
                    }

                daily_data[date_key]['count'] += 1
                daily_data[date_key]['total'] += power
                daily_data[date_key]['max'] = max(daily_data[date_key]['max'], power)

            except (ValueError, KeyError):
                continue

        # Calculate daily averages
        history = []
        for date_key in sorted(daily_data.keys()):
            avg_power = daily_data[date_key]['total'] / daily_data[date_key]['count']
            history.append({
                'timestamp': date_key,
                'power': round(avg_power, 1)
            })

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
        Calculate total daily energy consumption

        Args:
            sensors: List of energy sensors

        Returns:
            Daily energy in kWh
        """
        # Try to use HA Energy Dashboard sensors first (they track daily automatically)
        # Look for sensors with "energy" and "daily" or "today" in the name
        for sensor in sensors:
            try:
                entity_id = sensor.get('entity_id', '').lower()
                friendly_name = sensor.get('attributes', {}).get('friendly_name', '').lower()

                # Check for daily energy sensors
                if any(keyword in entity_id or keyword in friendly_name for keyword in ['daily', 'today', '_day']):
                    state = sensor['state']
                    if state not in ['unknown', 'unavailable', 'none', None]:
                        value = float(state)
                        unit = sensor.get('attributes', {}).get('unit_of_measurement', 'kWh')

                        # Convert to kWh
                        if unit == 'Wh':
                            value /= 1000

                        if value > 0 and value < 1000:  # Sanity check (not cumulative)
                            logger.info(f"Using daily energy sensor: {sensor.get('entity_id')} = {value} kWh")
                            return value
            except (ValueError, KeyError):
                continue

        # Fallback: estimate from current power usage
        # This is less accurate but doesn't show cumulative values
        power_sensors = self.ha_client.get_power_sensors()

        # Filter out bitshake
        bitshake_power = 0
        tracked_power = 0

        for sensor in power_sensors:
            entity_id = sensor['entity_id']
            friendly_name = sensor.get('attributes', {}).get('friendly_name', entity_id)

            if 'bitshake' in entity_id.lower() or 'bitshake' in friendly_name.lower():
                bitshake_power = self._parse_power(sensor)
            else:
                tracked_power += self._parse_power(sensor)

        # Use bitshake if available, otherwise tracked
        current_power = bitshake_power if bitshake_power > 0 else tracked_power

        # Estimate today's energy based on time of day and current power
        now = datetime.now()
        hours_today = now.hour + now.minute / 60.0

        # Estimate: assume current power for all hours so far today
        estimated_kwh = (current_power / 1000) * hours_today

        logger.warning(f"Using estimated daily energy: {estimated_kwh:.2f} kWh (no daily sensor found)")
        return estimated_kwh

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
