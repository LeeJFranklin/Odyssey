import requests

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
        