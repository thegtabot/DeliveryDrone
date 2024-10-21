from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, login_manager
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from utils import geocode_address, send_delivery_request

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        address = request.form.get('address')

        # Hash the password and create the user
        hashed_password = generate_password_hash(password, method='sha256')
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
    return render_template('dashboard.html')

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

@app.route('/order', methods=['POST'])
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))