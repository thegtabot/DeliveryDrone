import requests
import urllib.parse

import urllib.parse
import requests

def geocode_address(address):
    # Check if the address is a valid string
    if not isinstance(address, str) or not address.strip():
        raise ValueError("Invalid address: address must be a non-empty string.")

    # URL-encode the address
    encoded_address = urllib.parse.quote_plus(address)
    api_key = "AIzaSyAkzDb_af-rW_9gP3v43RNS0MFVBXSA7JU"  # Make sure this is a valid API key
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        response = requests.get(geocode_url)
        result = response.json()

        if result['status'] == 'OK':
            location = result['results'][0]['geometry']['location']
            lat = location['lat']
            lon = location['lng']
            return lat, lon
        else:
            print("Error accessing Google API: ", result['status'])  # Improved error logging
            return None, None
    except Exception as e:
        print("An error occurred while accessing the Google API:", str(e))
        return None, None


def send_delivery_request(lat, lon):
    pi_url = "10.0.0.2:5000"
    payload = {'lat': lat, 'lon': lon}
    response = requests.post(pi_url, json=payload)
    
    if response.status_code == 200:
        return True
    return False
