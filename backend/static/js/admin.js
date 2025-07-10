// Handle automatic logout when admin panel is closed
document.addEventListener('DOMContentLoaded', function() {
    // Function to handle page visibility change
    function handleVisibilityChange() {
        if (document.hidden) {
            // Page is hidden (user switched tabs or minimized window)
            console.log('Admin panel hidden - logging out...');
            // Perform logout
            fetch('/admin/logout', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(response => {
                if (response.ok) {
                    // Redirect to login page after successful logout
                    window.location.href = '/admin/login';
                }
            }).catch(error => {
                console.error('Logout failed:', error);
            });
        }
    }

    // Listen for visibility change events
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Handle window close event
    window.addEventListener('beforeunload', function() {
        // Attempt to logout when window is closed
        navigator.sendBeacon('/admin/logout');
    });
}); 