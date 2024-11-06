const username = document.getElementById("username");
const password = document.getElementById("password");
const passwordError = document.getElementById("password-error")

if (password.length < 8) {
    passwordError.innerHTML = "Password must contain at least 8 characters.";
    return;
}
