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
        
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 52.52,
            "longitude": 13.41,
            "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "is_day", "precipitation", "rain", "showers", "snowfall", "weather_code", "cloud_cover", "pressure_msl", "surface_pressure", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
            "wind_speed_unit": "mph",
            "timeformat": "unixtime",
            "timezone": "auto",
            "forecast_days": 1
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Current values. The order of variables needs to be the same as requested.
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_relative_humidity_2m = current.Variables(1).Value()
        current_apparent_temperature = current.Variables(2).Value()
        current_is_day = current.Variables(3).Value()
        current_precipitation = current.Variables(4).Value()
        current_rain = current.Variables(5).Value()
        current_showers = current.Variables(6).Value()
        current_snowfall = current.Variables(7).Value()
        current_weather_code = current.Variables(8).Value()
        current_cloud_cover = current.Variables(9).Value()
        current_pressure_msl = current.Variables(10).Value()
        current_surface_pressure = current.Variables(11).Value()
        current_wind_speed_10m = current.Variables(12).Value()
        current_wind_direction_10m = current.Variables(13).Value()
        current_wind_gusts_10m = current.Variables(14).Value()

        print(f"Current time {current.Time()}")
        print(f"Current temperature_2m {current_temperature_2m}")
        print(f"Current relative_humidity_2m {current_relative_humidity_2m}")
        print(f"Current apparent_temperature {current_apparent_temperature}")
        print(f"Current is_day {current_is_day}")
        print(f"Current precipitation {current_precipitation}")
        print(f"Current rain {current_rain}")
        print(f"Current showers {current_showers}")
        print(f"Current snowfall {current_snowfall}")
        print(f"Current weather_code {current_weather_code}")
        print(f"Current cloud_cover {current_cloud_cover}")
        print(f"Current pressure_msl {current_pressure_msl}")
        print(f"Current surface_pressure {current_surface_pressure}")
        print(f"Current wind_speed_10m {current_wind_speed_10m}")
        print(f"Current wind_direction_10m {current_wind_direction_10m}")
        print(f"Current wind_gusts_10m {current_wind_gusts_10m}")