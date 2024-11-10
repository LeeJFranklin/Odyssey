document.querySelector("form").addEventListener("submit", function(event) {
    const registerUsername = document.getElementById("register-username");
    const registerEmail = document.getElementById("register-email")
    const registerPass = document.getElementById("register-password");
    const confirmRegisterPass = document.getElementById("confirm-register-password")
    const errorMsg = document.getElementById("register-error")

    // Function for checking if username is valid
    const usernameIsValid = (username) => {
        return /^[^\s]+$/.test(username);
    };
    
    // Function for checking if email address is valid
    const emailIsValid = (email) => {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    };

    // Function for checking if password is valid, conatining
    // 8+ characters with 1 uppercase, 1 lowercase, 1 number, and 1 special character
    const passwordIsValid = (password) => {
        return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/.test(password);
    };

    // Clear previous error message
    errorMsg.innerHTML = "";

    // Prevent submission if there are validation errors
    let validationError = false;

    if (registerUsername.value === "") {
        errorMsg.innerHTML = "Please choose a Username";
        validationError = true;
    }
    else if (!usernameIsValid(registerUsername.value)) {
        errorMsg.innerHTML = "Username must not contain spaces";
        validationError = true;
    }
    else if (!emailIsValid(registerEmail.value)) {
        errorMsg.innerHTML = "Please enter a valid email address";
        validationError = true;
    }
    else if (!passwordIsValid(registerPass.value)) {
        errorMsg.innerHTML = "Password must be 8+ characters with 1 uppercase, 1 lowercase, 1 number, and 1 special character";
        validationError = true;
    }
    else if (confirmRegisterPass.value != registerPass.value) {
        errorMsg.innerHTML = "Passwords do not match";
        validationError = true;
    }

    // Prevent form submission if there were any validation errors
    if (validationError) {
        event.preventDefault();
    }
});

// Initialize the Leaflet map
var map = L.map("map").setView([21.000, 10.00], 2);

// Add OpenStreetMap tiles to Leaflet map
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,  // Maximum zoom level to control zooming in
    minZoom: 2,    // Minimum zoom level to control zooming out
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

// Add event listener to input field for Enter key
document.getElementById("location-search").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        searchLocation();  // Call the searchLocation function when Enter is pressed
    }
});

let marker;  // Variable to store the map marker

// Adds GeoLocation search to front-end from Photon
async function searchLocation() {
    const location = document.getElementById("location-search").value;
    const response = await fetch(`/api/geocode?location=${encodeURIComponent(location)}`);
    const data = await response.json();
    if (data.lat && data.lon) {
        if (marker) map.removeLayer(marker);

        // Add the new marker and store it in marker
        marker = L.marker([data.lat, data.lon]).addTo(map)

        // Set the map view to the location
        map.setView([data.lat, data.lon], 5);
    } else {
        alert(data.error || "Location not found");
    }
}

// Generates a random float between -90 and 90 for Latitude
const randomLat = () => (Math.random() < 0.5 ? -1 : 1) * (Math.random() * 90);

// Generates a random float between -180 and 180 for Longitude
const randomLon = () => (Math.random() < 0.5 ? -1 : 1) * (Math.random() * 180);

async function supriseLocation() {
    let lon = randomLon().toFixed(5);
    let lat = randomLat().toFixed(5);
    const response = await fetch(`api/geocode?lon=${encodeURIComponent(lon)}&lat=${encodeURIComponent(lat)}`);
    const data = await response.json();
    if (data.lat && data.lon) {
        if (marker) map.removeLayer(marker);

        // Add the new marker and store it in marker
        marker = L.marker([data.lat, data.lon]).addTo(map)
            .bindPopup(data.location)
            .openPopup();

        // Set the map view to the location
        map.setView([data.lat, data.lon], 5);
    } else {
        supriseLocation();
    }
}