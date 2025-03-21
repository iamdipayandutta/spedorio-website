// Base API URL - Replace with your Railway app URL
const API_BASE_URL = 'https://web-production-b4b2.up.railway.app';

// Handle Login
async function handleLogin(e) {
    if (e) e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginAlert = document.getElementById('login-alert');
    
    if (!username || !password) {
        loginAlert.textContent = 'Please enter both username and password';
        loginAlert.style.display = 'block';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Store auth in localStorage
            localStorage.setItem('auth', JSON.stringify({
                username: data.user.username,
                isAdmin: data.user.is_admin,
                isLoggedIn: true
            }));
            
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            loginAlert.style.display = 'block';
        }
    } catch (error) {
        console.error('Login error:', error);
        loginAlert.textContent = 'An error occurred during login';
        loginAlert.style.display = 'block';
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Other initialization code can go here
}); 