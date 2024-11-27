import requests
import openmeteo_requests
import requests_cache
import pandas as pd

from retry_requests import retry
from flask import jsonify, request

def init_api_routes(app):
    # Photon API Geocode endpoint
    @app.route("/api/geocode", methods=["GET", "POST"])
    def geocode():
        location = request.args.get("location")

        # Geocoding (Location to Coordinates)
        photon_url = f"https://photon.komoot.io/api/?q={location}&lang=en"
        response = requests.get(photon_url)
        if response.status_code != 200:
            return jsonify({"error": "Error contacting Photon API"}), 500

        data = response.json()
        if data.get("features"):
            coordinates = data["features"][0]["geometry"]["coordinates"]
            return jsonify({"lon": coordinates[0], "lat": coordinates[1]})
        return jsonify({"error": "Location not found"}), 404       
        
    # Open-Meteo API route
    @app.route("/api/weather", methods=["GET", "POST"])
    def weather():
        # Get latitude and longitude from request arguments
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')

        if not latitude or not longitude:
            # Return an error if latitude or longitude is missing
            return jsonify({"error": "Latitude and longitude are required"}), 400

        # Setup Open-Meteo API client
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        # Open-Meteo API call
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m"
        }
        try:
            response = openmeteo.weather_api(url, params=params)[0]

            # Extract and return relevant weather data
            current = response.Current()
            weather_data = {
                "temperature": current.Variables(0).Value(),
            }

            return jsonify(weather_data)

        except Exception as e:
            # Catch and return errors in the API call
            return jsonify({"error": f"Failed to fetch weather data: {str(e)}"}), 500
