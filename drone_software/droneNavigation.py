# On Raspberry Pi (10.0.0.2)
from flask import Flask, jsonify
from dronekit import connect
import time

app = Flask(__name__)

# Connect to the Pixhawk (adjust connection string as needed)
vehicle = connect('/dev/ttyAMA0', wait_ready=True, baud=57600)

@app.route('/drone-location')
def drone_location():
    try:
        location = vehicle.location.global_frame
        if location:
            return jsonify({
                'status': 'success',
                'latitude': location.lat,
                'longitude': location.lon
            })
        else:
            return jsonify({'status': 'error', 'message': 'No GPS fix.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Ensure the vehicle connection is closed when the Flask app stops
@app.teardown_appcontext
def close_vehicle(exception=None):
    vehicle.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Make accessible over VPN
