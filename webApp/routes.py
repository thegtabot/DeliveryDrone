from flask import render_template, request, redirect, url_for, flash, jsonify, Flask 
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, login_manager
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
import requests
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
        # Hash the password and create the user
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
    return render_template('dashboard.html', username=current_user.username)

# Fetch current drone location
@app.route('/drone-location', methods=['GET'])
@login_required
def drone_location_api():
    return jsonify(drone_location)

# Update the drone's location (POST request sent by Raspberry Pi)
@app.route('/update-drone-location', methods=['POST'])
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

@app.route('/set-location', methods=['POST'])
@login_required
def set_location():
    address = request.form.get('address')
    lat, lon = geocode_address(address)

    current_user.address = address
    current_user.lat = lat
    current_user.lon = lon
    db.session.commit()

    flash('Location updated successfully!')
    return redirect(url_for('dashboard'))

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    if not current_user.lat or not current_user.lon:
        flash('Please set your delivery location first.')
        return redirect(url_for('dashboard'))

    # Send GPS coordinates to the Raspberry Pi
    success = send_delivery_request(current_user.lat, current_user.lon)
    
    if success:
        flash('Your order has been placed and the drone is on its way!')
    else:
        flash('Failed to place the order. Please try again.')

    return redirect(url_for('dashboard'))

@app.route('/get-coordinates', methods=['GET'])
@login_required
def get_coordinates():
    address = current_user.address  # Get the address of the logged-in user
    lat, lon = geocode_address(address)  # Get the GPS coordinates using the function above
    print("clicked")
    if lat and lon:
        print("pressed")
        return jsonify({'status': 'success', 'latitude': lat, 'longitude': lon})
        
    else:
        return jsonify({'status': 'error', 'message': 'Failed to get GPS coordinates'})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Request Changes Route
@app.route('/request_changes', methods=['POST'])
@login_required
def request_changes():
    new_username = request.form.get('new_username')
    new_password = request.form.get('new_password')
    new_address = request.form.get('new_address')

    # Update user information if provided
    if new_username:
        current_user.username = new_username
    if new_password:
        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
    if new_address:
        current_user.address = new_address

    # Commit changes to the database
    db.session.commit()
    flash('Your account changes have been submitted successfully.', 'success')

    return redirect(url_for('dashboard'))


@app.route('/account-settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    if request.method == 'POST':
        # Process form data to update account settings
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')
        new_address = request.form.get('new_address')

        # Add logic to validate and save changes to the database
        if new_username:
            # Update username in the database
            current_user.username = new_username
        if new_password:
            # Update password securely (hash before saving)
            current_user.set_password(new_password)
        if new_address:
            # Update address in the database
            current_user.address = new_address

        # Save changes to the database (commit if using SQLAlchemy)
        db.session.commit()
        flash('Your account settings have been updated.', 'success')
        return redirect(url_for('account_settings'))

    # Render account settings template
    return render_template('account_settings.html', user=current_user)