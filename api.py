import requests

from flask import jsonify, request

def init_api_routes(app):
    # Photon API Geocode endpoint
    @app.route("/api/geocode", methods=["GET"])
    def geocode():
        location = request.args.get("location")
        lon = request.args.get("lon")
        lat = request.args.get("lat")

        if location:
            # Geocoding (Location to Coordinates)
            photon_url = f"https://photon.komoot.io/api/?q={location}"
            response = requests.get(photon_url)
            if response.status_code != 200:
                return jsonify({"error": "Error contacting Photon API"}), 500

            data = response.json()
            if data.get("features"):
                coordinates = data["features"][0]["geometry"]["coordinates"]
                return jsonify({"lon": coordinates[0], "lat": coordinates[1]})
            return jsonify({"error": "Location not found"}), 404
        
        elif lon is not None and lat is not None:
            # Reverse Geocoding (Coordinates to Location)
            photon_url = f"https://photon.komoot.io/reverse?lon={lon}&lat={lat}"
            response = requests.get(photon_url)
            if response.status_code != 200:
                return jsonify({"error": "Error contacting Photon API"}), 500

            data = response.json()
            if data.get("features"):
                coordinates = data["features"][0]["geometry"]["coordinates"]
                properties = data["features"][0]["properties"]
                country = properties.get("country", "Unknown country")
                city = properties.get("city", "Unknown location")
                return jsonify({
                    "lon": coordinates[0], 
                    "lat": coordinates[1],
                    "location": f"{city}, {country}" if city != "Unknown City" else country
                })
            return jsonify({"error": "Location not found"}), 404
        
        print("Neither location nor lon/lat provided")
        return jsonify({"error": "Location or coordinates (lon and lat) are required"}), 400