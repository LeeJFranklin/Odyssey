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
var map = L.map('map').setView([21.000, 10.00], 2);

// Add OpenStreetMap tiles to Leaflet map
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,  // Maximum zoom level to control zooming in
    minZoom: 2,    // Minimum zoom level to control zooming out
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

let currentMarker;  // Variable to store the current marker

// Add event listener to input field for Enter key
document.getElementById('location-search').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        searchLocation();  // Call the searchLocation function when Enter is pressed
    }
});

// Add GeoLocation search with Photon API
async function searchLocation() {
    const location = document.getElementById('location-search').value;
    const url = `https://photon.komoot.io/api/?q=${encodeURIComponent(location)}`;

    try {
        const response = await fetch(url);
        const data = await response.json();
        L.marker()

        if (data && data.features && data.features.length > 0) {
            const { coordinates } = data.features[0].geometry;
            const [lon, lat] = coordinates;

            // Remove the existing marker if there is one
            if (currentMarker) {
                map.removeLayer(currentMarker);
            }

            // Set the map view to the location
            map.setView([lat, lon], 5);

            // Add the new marker and store it in currentMarker
            currentMarker = L.marker([lat, lon]).addTo(map)
                .bindPopup(`${location}`)
                .openPopup();
        } else {
            alert("Location not found.");
        }
    } catch (error) {
        console.error("Error with Photon API:", error);
    }
}