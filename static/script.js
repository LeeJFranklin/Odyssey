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
const map = L.map("map").setView([21.000, 10.00], 2);

// Add OpenStreetMap tiles to Leaflet map
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,  // Maximum zoom level to control zooming in
    minZoom: 2,    // Minimum zoom level to control zooming out
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

// Add event listener to the button for click event
document.getElementById("explore-search-btn").addEventListener("click", function(event) {
    event.preventDefault();  // Prevent default behavior, such as form submission
    searchLocation();  // Call the searchLocation function
});

// Add event listener to input field for Enter key
document.getElementById("location-search").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Prevent default behavior, such as form submission
        searchLocation();  // Call the searchLocation function when Enter is pressed
    }
});

// Add event listener to the button for click event
document.getElementById("explore-surprise-btn").addEventListener("click", function(event) {
    event.preventDefault();  // Prevent default behavior, such as form submission
    surpriseLocation();  // Call the searchLocation function
});

const locationName = document.getElementById("location-name");

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

        locationName.innerHTML = `<b>${location.toUpperCase()}</b>`;

        // Set the map view to the location
        map.setView([data.lat, data.lon], 5);

        // Get location info
        getLocationInfo(location);
    } else {
        alert(data.error || "Location not found");
    }
}

async function surpriseLocation() {
    fetch("static/data/destinations.json")
    .then(response => response.json())  // Parse the JSON from the response
    .then(data => {
        // Select a random entry from the data array
        const randomIndex = Math.floor(Math.random() * data.length);
        const randomCity = data[randomIndex];  // Get the random city entry
        
        const city = randomCity.city;  // Access the city
        const country = randomCity.country // Access the country
        const lat = randomCity.coordinates.lat;  // Access the latitude
        const lon = randomCity.coordinates.lon;  // Access the longitude

        // Add a marker for the random city on the map
        if (marker) map.removeLayer(marker);  // Remove previous marker if it exists
        marker = L.marker([lat, lon]).addTo(map)
            
        locationName.innerHTML = `${city}, ${country}`;

        // Set the map view to the random city's location
        map.setView([lat, lon], 5);

        // Get location info
        getLocationInfo(city);
    })
    .catch(error => console.error('Error loading the JSON data:', error));
}

// Function to send data to Flask using AJAX (fetch)
async function getLocationInfo(location) {  
    // Sending POST request to Flask route
    const response = await fetch("/explore", {
        method: "POST",
        body: JSON.stringify({ location: location }), // Send location to Flask
        headers: { "Content-Type": "application/json" }
    });

    const data = await response.json();

    // Update the HTML with the new data received from Flask (partial render)
    document.getElementById("location-info").innerHTML = data.location_info;
}

function addToFavourites() {
    const locationName = document.getElementById("location-name").textContent;

    fetch("/add_to_favourites", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ location: locationName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Location added to favourites!");
        } else {
            alert("Failed to add location.");
        }
    })
    .catch(error => console.error("Error:", error));
}
