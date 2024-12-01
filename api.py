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
        
    @app.route("/api/weather", methods=["GET", "POST"])
    def weather():
        # Get latitude and longitude from request arguments
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')

        if not latitude or not longitude:
            # Return an error if latitude or longitude is missing
            return jsonify({"error": "Latitude and longitude are required"}), 400

        # Setup Open-Meteo API client
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # Open-Meteo API call
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "rain_sum"],
            "timezone": "auto"
        }

        try:
            # Fetch weather data from Open-Meteo API
            response = openmeteo.weather_api(url, params=params)[0]

            # Extract daily data
            daily = response.Daily()

            # Generate dates using pd.date_range
            daily_dates = pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            ).strftime('%d-%m-%Y')  # Format dates as strings

            # Extract weather variables
            daily_weather_code = daily.Variables(0).ValuesAsNumpy()
            daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
            daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
            daily_rain_sum = daily.Variables(3).ValuesAsNumpy()

            # Format daily weather data
            daily_weather = []
            for i, date in enumerate(daily_dates):
                daily_weather.append({
                    "date": date,
                    "weather_code": int(daily_weather_code[i]),
                    "temperature_max": float(daily_temperature_2m_max[i]),
                    "temperature_min": float(daily_temperature_2m_min[i]),
                    "rain_sum": float(daily_rain_sum[i])
                })

            # Prepare API response
            return jsonify({"daily": daily_weather})

        except Exception as e:
            # Handle and return any errors
            return jsonify({"error": f"Failed to fetch weather data: {str(e)}"}), 500