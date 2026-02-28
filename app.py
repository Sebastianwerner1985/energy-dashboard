"""
Energy Dashboard Flask Application
"""
from flask import Flask, render_template, jsonify, request
from services.home_assistant import HomeAssistantClient
from services.data_processor import DataProcessor
from utils.logger import setup_logger
import config

app = Flask(__name__)
app.config.from_object(config)

# Initialize logger
logger = setup_logger(__name__)

# Initialize services
ha_client = HomeAssistantClient(config.HA_URL, config.HA_TOKEN)
data_processor = DataProcessor(ha_client, config.CACHE_TTL)


@app.route('/')
def index():
    """Redirect to overview page"""
    return render_template('overview.html')


@app.route('/overview')
def overview():
    """Overview page with summary statistics"""
    try:
        data = data_processor.get_overview_data()
        return render_template('overview.html', data=data, config=config)
    except Exception as e:
        logger.error(f"Error loading overview: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/realtime')
def realtime():
    """Real-time monitoring page"""
    try:
        data = data_processor.get_realtime_data()
        return render_template('realtime.html', data=data, config=config)
    except Exception as e:
        logger.error(f"Error loading realtime data: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/costs')
def costs():
    """Cost analysis page"""
    try:
        data = data_processor.get_cost_data()
        return render_template('costs.html', data=data, config=config)
    except Exception as e:
        logger.error(f"Error loading cost data: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/history')
def history():
    """Historical trends page"""
    try:
        period = request.args.get('period', '24h')
        data = data_processor.get_history_data(period)
        return render_template('history.html', data=data, config=config, period=period)
    except Exception as e:
        logger.error(f"Error loading history data: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/device/<device_id>')
def device(device_id):
    """Device details page"""
    try:
        data = data_processor.get_device_data(device_id)
        return render_template('device.html', data=data, config=config, device_id=device_id)
    except Exception as e:
        logger.error(f"Error loading device data: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Configuration settings page"""
    if request.method == 'POST':
        # Handle settings update
        try:
            # TODO: Implement settings persistence
            return jsonify({'success': True, 'message': 'Settings updated'})
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    return render_template('settings.html', config=config)


@app.route('/api/realtime')
def api_realtime():
    """API endpoint for real-time data updates"""
    try:
        data = data_processor.get_realtime_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/test-connection')
def api_test_connection():
    """API endpoint to test Home Assistant connection"""
    try:
        # Test connection by attempting to get states
        states = ha_client.get_states()
        if states is not None:
            return jsonify({
                'success': True,
                'message': 'Connected successfully',
                'sensors_found': len(states)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to retrieve states from Home Assistant'
            }), 500
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return jsonify({
            'success': False,
            'message': f'Connection failed: {str(e)}'
        }), 500


@app.route('/api/device/<device_id>')
def api_device(device_id):
    """API endpoint for device data"""
    try:
        data = data_processor.get_device_data(device_id)
        return jsonify(data)
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return render_template('error.html', error='Internal server error'), 500


if __name__ == '__main__':
    logger.info(f"Starting Energy Dashboard on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=config.DEBUG)
