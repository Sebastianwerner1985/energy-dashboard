"""
Home Assistant REST API Client
"""
import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class HomeAssistantClient:
    """Client for interacting with Home Assistant REST API"""

    def __init__(self, base_url: str, token: str):
        """
        Initialize Home Assistant client

        Args:
            base_url: Base URL of Home Assistant instance
            token: Long-lived access token
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self.timeout = 10

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make HTTP request to Home Assistant API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            Response object

        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        kwargs.setdefault('headers', self.headers)
        kwargs.setdefault('timeout', self.timeout)

        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Home Assistant API request failed: {e}")
            raise

    def get_states(self) -> List[Dict]:
        """
        Get all entity states from Home Assistant

        Returns:
            List of entity state dictionaries
        """
        response = self._request('GET', 'states')
        return response.json()

    def get_state(self, entity_id: str) -> Optional[Dict]:
        """
        Get state of a specific entity

        Args:
            entity_id: Entity ID (e.g., 'sensor.power_consumption')

        Returns:
            Entity state dictionary or None if not found
        """
        try:
            response = self._request('GET', f'states/{entity_id}')
            return response.json()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Entity not found: {entity_id}")
                return None
            raise

    def get_history(self, entity_id: str, start_time: str, end_time: Optional[str] = None) -> List[Dict]:
        """
        Get historical data for an entity

        Args:
            entity_id: Entity ID
            start_time: Start time in ISO format
            end_time: End time in ISO format (optional, defaults to now)

        Returns:
            List of historical state dictionaries
        """
        params = {'filter_entity_id': entity_id}
        endpoint = f'history/period/{start_time}'

        if end_time:
            params['end_time'] = end_time

        response = self._request('GET', endpoint, params=params)
        data = response.json()

        # History API returns list of lists, one per entity
        return data[0] if data else []

    def get_power_sensors(self) -> List[Dict]:
        """
        Get all power monitoring sensors

        Returns:
            List of power sensor state dictionaries
        """
        all_states = self.get_states()

        # Filter for power sensors (watts/kilowatts)
        power_sensors = [
            state for state in all_states
            if state['entity_id'].startswith('sensor.') and
            state.get('attributes', {}).get('unit_of_measurement') in ['W', 'kW', 'watt', 'kilowatt']
        ]

        return power_sensors

    def get_energy_sensors(self) -> List[Dict]:
        """
        Get all energy monitoring sensors (kWh)

        Returns:
            List of energy sensor state dictionaries
        """
        all_states = self.get_states()

        # Filter for energy sensors (kilowatt-hours)
        energy_sensors = [
            state for state in all_states
            if state['entity_id'].startswith('sensor.') and
            state.get('attributes', {}).get('unit_of_measurement') in ['kWh', 'Wh']
        ]

        return energy_sensors

    def get_devices_by_room(self) -> Dict[str, List[Dict]]:
        """
        Organize power sensors by room/area

        Returns:
            Dictionary mapping room names to lists of sensors
        """
        power_sensors = self.get_power_sensors()
        rooms = {}

        for sensor in power_sensors:
            # Try to extract room from friendly_name or entity_id
            friendly_name = sensor.get('attributes', {}).get('friendly_name', '')
            entity_id = sensor['entity_id']

            # Extract room from friendly name (assuming format "Room Name Device")
            # or from entity_id (assuming format "sensor.room_device_power")
            room = self._extract_room(friendly_name, entity_id)

            if room not in rooms:
                rooms[room] = []

            rooms[room].append(sensor)

        return rooms

    def _extract_room(self, friendly_name: str, entity_id: str) -> str:
        """
        Extract room name from sensor name

        Args:
            friendly_name: Sensor friendly name
            entity_id: Sensor entity ID

        Returns:
            Room name or 'Other' if not determinable
        """
        # Common room names
        rooms = ['living room', 'bedroom', 'kitchen', 'bathroom', 'office',
                 'garage', 'basement', 'attic', 'dining room', 'laundry']

        # Check friendly name first
        name_lower = friendly_name.lower()
        for room in rooms:
            if room in name_lower:
                return room.title()

        # Check entity_id
        entity_lower = entity_id.lower()
        for room in rooms:
            room_slug = room.replace(' ', '_')
            if room_slug in entity_lower:
                return room.title()

        return 'Other'

    def call_service(self, domain: str, service: str, entity_id: str, **kwargs) -> Dict:
        """
        Call a Home Assistant service

        Args:
            domain: Service domain (e.g., 'light', 'switch')
            service: Service name (e.g., 'turn_on', 'turn_off')
            entity_id: Target entity ID
            **kwargs: Additional service data

        Returns:
            Service call response
        """
        data = {
            'entity_id': entity_id,
            **kwargs
        }

        response = self._request('POST', f'services/{domain}/{service}', json=data)
        return response.json()

    def test_connection(self) -> bool:
        """
        Test connection to Home Assistant

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self._request('GET', '')
            return response.json().get('message') == 'API running.'
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
