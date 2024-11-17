from flask import Flask, jsonify
from dronekit import connect
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# Connect to the Pixhawk via DroneKit
vehicle = connect('/dev/ttyAMA0', wait_ready=True, baud=57600)

@app.route('/get-drone-coordinates', methods=['GET'])
def get_drone_coordinates():
    try:
        location = vehicle.location.global_frame
        print("Location: ", location.lat , location.lon)
        return jsonify({
            'status': 'success',
            'latitude': location.lat,
            'longitude': location.lon
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)   
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
