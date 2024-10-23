import requests

def geocode_address(address):
    # Example using Google Maps Geocoding API
    api_key = "AIzaSyAkzDb_af-rW_9gP3v43RNS0MFVBXSA7JU"
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(geocode_url)
    result = response.json()

    if result['status'] == 'OK':
        location = result['results'][0]['geometry']['location']
        lat = location['lat']
        lon = location['lng']
        return lat, lon
    else:
        return None, None

def send_delivery_request(lat, lon):
    pi_url = "10.0.0.2:5000"
    payload = {'lat': lat, 'lon': lon}
    response = requests.post(pi_url, json=payload)
    
    if response.status_code == 200:
        return True
    return False
