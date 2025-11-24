// Home page JavaScript
// Check if user is logged in
function checkAuth() {
    if (sessionStorage.getItem('isLoggedIn') !== 'true') {
        window.location.href = 'login.html';
    }
}

// Check authentication on page load
checkAuth();

// Navigate to different pages
function navigateTo(page) {
    if (page === 'ums.html') {
        window.location.href = page;
    } else {
        // Placeholder for other pages
        alert('This feature is coming soon!');
    }
}

// Add logout functionality (optional)
function logout() {
    sessionStorage.removeItem('isLoggedIn');
    window.location.href = 'login.html';
}
