from flask import render_template, request, redirect, url_for, flash, jsonify, Flask
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, login_manager
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from utils import geocode_address, send_delivery_request
import sqlite3

# Global variable to store the drone's latest GPS coordinates
drone_location = {'latitude': 0, 'longitude': 0}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        address = request.form.get('address')
        
        print(f"Debug: Address entered by the user: {address}")
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, address=address)
        db.session.add(new_user)
        db.session.commit()

        flash('User created successfully! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials, try again!')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_lat = current_user.lat or 39.2904  # Default to Baltimore if latitude not set
    user_lon = current_user.lon or -76.6122  # Default to Baltimore if longitude not set
    print(f"Debug: User latitude: {user_lat}, longitude: {user_lon}")
    return render_template(
        'dashboard.html',
        username=current_user.username,
        user_lat=user_lat,
        user_lon=user_lon
    )

@app.route('/admin_controls')
@login_required
def admin_controls():
    return render_template('admin_controls.html')

@app.route('/change_username', methods=['GET', 'POST'])
@login_required
def change_username():
    if request.method == 'POST':
        new_username = request.form.get('username')
        current_user.username = new_username
        db.session.commit()
        flash('Username updated successfully!')
        return redirect(url_for('admin_controls'))
    return render_template('change_username.html')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        new_password = request.form.get('password')
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        current_user.password = hashed_password
        db.session.commit()
        flash('Password updated successfully!')
        return redirect(url_for('admin_controls'))
    return render_template('change_password.html')

@app.route('/manage_users')
@login_required
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/drone-location', methods=['GET'])
@login_required
def drone_location_api():
    print(f"Debug: Returning drone location: {drone_location}")
    return jsonify(drone_location)

@app.route('/update_drone_location', methods=['POST'])
def update_drone_location():
    global drone_location
    try:
        data = request.json
        drone_location['latitude'] = data.get('latitude')
        drone_location['longitude'] = data.get('longitude')
        print(f"Updated drone location: {drone_location}")
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"Error updating location: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/set_location', methods=['POST'])
@login_required
def set_location():
    address = request.form.get('address')
    lat, lon = geocode_address(address)
    print(f"Debug: Geocoded address {address} to lat: {lat}, lon: {lon}")

    current_user.address = address
    current_user.lat = lat
    print('User lat: ', lat)
    current_user.lon = lon
    print('User lon: ', lon)
    db.session.commit()

    flash('Location updated successfully!')
    return redirect(url_for('dashboard'))

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    if not current_user.lat or not current_user.lon:
        flash('Please set your delivery location first.')
        return redirect(url_for('dashboard'))

    success = send_delivery_request(current_user.lat, current_user.lon)
    if success:
        flash('Your order has been placed and the drone is on its way!')
    else:
        flash('Failed to place the order. Please try again.')

    return redirect(url_for('dashboard'))

@app.route('/get_coordinates', methods=['GET'])
@login_required
def get_coordinates():
    
    address = request.form.get('address')
    lat, lon = geocode_address(address)
    print(f"Debug: Geocoded address {address} to lat: {lat}, lon: {lon}")

    current_user.address = address
    current_user.lat = lat
    print('User lat: ', lat)
    current_user.lon = lon
    print('User lon: ', lon)
    db.session.commit()

    print("Debug: get_coordinates called")
    if current_user.lat and current_user.lon:
        return jsonify({'status': 'success', 'latitude': current_user.lat, 'longitude': current_user.lon})
    else:
        print(f"Debug: User latitude: {current_user.lat}, longitude: {current_user.lon}")
        return jsonify({'status': 'success', 'latitude': current_user.lat, 'longitude': current_user.lon})

        #return jsonify({'status': 'error', 'message': 'Failed to get GPS coordinates'})

@app.route('/request_changes', methods=['POST'])
@login_required
def request_changes():
    new_username = request.form.get('new_username')
    new_password = request.form.get('new_password')
    new_address = request.form.get('new_address')

    if new_username:
        current_user.username = new_username
    if new_password:
        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
    if new_address:
        current_user.address = new_address
    
    db.session.commit()
    flash('Account details updated successfully!')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
