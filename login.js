// Login page JavaScript
// Hardcoded credentials - change these as needed
const VALID_USERNAME = 'admin';
const VALID_PASSWORD = 'admin123';

document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');
    
    // Validate credentials
    if (username === VALID_USERNAME && password === VALID_PASSWORD) {
        // Store login state
        sessionStorage.setItem('isLoggedIn', 'true');
        // Redirect to home page
        window.location.href = 'home.html';
    } else {
        // Show error message
        errorMessage.textContent = 'Invalid username or password';
        errorMessage.style.display = 'block';
        
        // Clear password field
        document.getElementById('password').value = '';
    }
});

// Clear error message when user starts typing
document.getElementById('username').addEventListener('input', clearError);
document.getElementById('password').addEventListener('input', clearError);

function clearError() {
    document.getElementById('errorMessage').style.display = 'none';
}
