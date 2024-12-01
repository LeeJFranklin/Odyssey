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

// Registration form validation
document.getElementById("register-form")?.addEventListener("submit", function(event) {
    const registerUsername = document.getElementById("register-username");
    const registerEmail = document.getElementById("register-email")
    const registerPass = document.getElementById("register-password");
    const confirmRegisterPass = document.getElementById("confirm-register-password")
    const errorMsg = document.getElementById("register-error")

    // Clear previous error messages
    errorMsg.innerHTML = "";

    // Prevent submission if there are validation errors
    let validationError = false;

    if (registerUsername.value === "") {
        errorMsg.innerHTML = "Please choose a Username";
        validationError = true;
    } else if (!usernameIsValid(registerUsername.value)) {
        errorMsg.innerHTML = "Username must not contain spaces";
        validationError = true;
    } else if (!emailIsValid(registerEmail.value)) {
        errorMsg.innerHTML = "Please enter a valid email address";
        validationError = true;
    } else if (!passwordIsValid(registerPass.value)) {
        errorMsg.innerHTML = "Password must be 8+ characters with 1 uppercase, 1 lowercase, 1 number, and 1 special character";
        validationError = true;
    } else if (confirmRegisterPass.value != registerPass.value) {
        errorMsg.innerHTML = "Passwords do not match";
        validationError = true;
    };

    // Prevent form submission if there were any validation errors
    if (validationError) {
        event.preventDefault();
    }
});
    
document.getElementById("change-password-form")?.addEventListener("submit", function(event) {
    const currentPassword = document.getElementById("current-password");
    const newPassword = document.getElementById("new-password");
    const confirmNewPassword = document.getElementById("confirm-new-password");
    const changePasswordError = document.getElementById("change-password-error")

    // Clear previous error messages
    changePasswordError.innerHTML = "";

    // Changing password validation
    if (currentPassword.value === "") {
        changePasswordError.innerHTML = "Please input your current password";
        validationError = true;
    } else if (!passwordIsValid(newPassword.value)) {
        changePasswordError.innerHTML = "Password must be 8+ characters with 1 uppercase, 1 lowercase, 1 number, and 1 special character";
        validationError = true;
    } else if (newPassword.value != confirmNewPassword.value) {
        changePasswordError.innerHTML = "Passwords do not match";
        validationError = true;
    }

    // Prevent form submission if there were any validation errors
    if (validationError) {
        event.preventDefault();
    }
});

// Trip planning input validation
document.getElementById("planner-form")?.addEventListener("submit", function(event) {
    const city = document.getElementById("city-input");
    const country = document.getElementById("country-input");
    const planningErrorMsg = document.getElementById("planning-error");

    // Clear previous error messages
    planningErrorMsg.innerHTML = "";

    // Prevent submission if there are validation errors
    let validationError = false;

    if (city.value === "") {
        planningErrorMsg.innerHTML = "Please choose a city";
        validationError = true;
    } else if (country.value === "") {
        planningErrorMsg.innerHTML = "Please choose a country";
        validationError = true;
    };

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
document.addEventListener("DOMContentLoaded", function () {
    const surpriseButton = document.getElementById("explore-surprise-btn");

    // Check if the button exists
    if (surpriseButton) {
        surpriseButton.addEventListener("click", function(event) {
            event.preventDefault();  // Prevent default behavior, such as form submission
            surpriseLocation();  // Call the surpriseLocation function
        });
    }
});

const locationName = document.getElementById("location-name");

let marker;  // Variable to store the map marker

async function surpriseLocation() {
    const hiddenCity = document.getElementById("hidden-city-input")
    const hiddenCountry = document.getElementById("hidden-country-input")

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
        hiddenCity.value = `${city}`;
        hiddenCountry.value = `${country}`

        // Set the map view to the random city's location
        map.setView([lat, lon], 5);

        // Get location info
        getLocationInfo(city);
    })
    .catch(error => console.error('Error loading the JSON data:', error));
}

// Add GeoLocation search with Photon API
async function searchLocation() {
    const location = document.getElementById("planner-location").textContent;
    const response = await fetch(`/api/geocode?location=${encodeURIComponent(location)}`);
    const data = await response.json();
    if (data.lat && data.lon) {
        if (marker) map.removeLayer(marker);

        // Add the new marker and store it in marker
        marker = L.marker([data.lat, data.lon]).addTo(map)

        // Set the map view to the location
        map.setView([data.lat, data.lon], 4);

        // Fetch weather data for the selected location
        const weatherResponse = await fetch(`/api/weather?latitude=${data.lat}&longitude=${data.lon}`);
        const weatherData = await weatherResponse.json();

        if (weatherData.error) {
            alert(`Weather API Error: ${weatherData.error}`);
        } else {
            const forecast = weatherData.daily.map(day => `
                <li class="list-style-none">
                   <span class="material-symbols-outlined weather">calendar_today</span> ${day.date} <span class="material-symbols-outlined weather">sunny</span> ${Math.round(day.temperature_max)}°C <span class="material-symbols-outlined weather">bedtime</span> ${Math.round(day.temperature_min)}°C <span class="material-symbols-outlined weather">rainy</span> ${Math.round(day.rain_sum)}mm
                </li>
            `).join("");
        
            document.getElementById("weather-info").innerHTML = `
                <h3>7 Day Weather Forecast</h3>
                <ul>${forecast}</ul>
            `;
        }

    } else {
        alert(data.error || "Location not found");
    }
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

// Runs the surpriseLocation() function on page load
document.addEventListener("DOMContentLoaded", function () {
    if (document.querySelector("#explore-div")) {
        surpriseLocation();
    }
});

// Runs the searchLocation() function on page load
document.addEventListener("DOMContentLoaded", function () {
    // Check if the element exists
    if (document.getElementById("planner-location")) {
        searchLocation();
    }
});

// Get the element
const container = document.getElementById("editContainer");
// Dynamically get the Trip ID from each page using the hidden <span>
const tripId = document.getElementById("trip-id").textContent

function loadEditForm() {
    // Dynamically load the form into the container
    container.innerHTML = `
            <table class="trip-details-table">
                <thead>
                    <tr>
                        <th class="th-start"><p class="yellow-text">Details</p></th>
                        <th class="right-align"><button id="save-button" class="icon-submit-btn"><span class="material-symbols-outlined">check</span></button></th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Start Date</td>
                        <td class="right-align"><input type="date" class="trip-details-input" id="startdate" name="startdate"></td>
                    </tr>
                    <tr>
                        <td>End Date</td>
                        <td class="right-align"><input type="date" class="trip-details-input" id="enddate" name="enddate"></td>
                    </tr>
                    <tr>
                        <td>Transport Type</td>
                        <td class="right-align"><input type="text" class="trip-details-input" id="transport" name="transport"></td>
                    </tr>
                    <tr>
                        <td>Accommodation</td>
                        <td class="right-align"><input type="text" class="trip-details-input" id="accommodation" name="accommodation"></td>
                    </tr>
                    <tr>
                        <td>Budget</td>
                        <td class="right-align"><input type="text" class="trip-details-input" id="budget" name="budget"></td>
                    </tr>
                </tbody>
            </table>
    `;
};

function deleteAccount() {
    const deleteAccountForm = document.getElementById("delete-account-form");
    // Dynamically load delete account HTML
    deleteAccountForm.innerHTML = `
        <h3>DELETE ACCOUNT</h3>
        <p id="delete-error"></p>
        <input class="input-field" type="password" id="delete-account-password" name="delete-account-password" placeholder="Password">
        <input class="input-field" type="password" id="delete-account-confirm-password" name="delete-account-confirm-password" placeholder="Confirm Password">
        <button type="submit" class="red-btn" id="delete-account-btn" name="delete-account-btn">DELETE ACCOUNT</button>
    `;
};
