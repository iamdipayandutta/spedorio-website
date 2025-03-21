from app import app
import os

# Configure to allow requests from your Netlify frontend
app.config['CORS_ORIGINS'] = [
    'http://localhost:3000',  # For local frontend testing
    'https://your-netlify-site.netlify.app',  # Replace with your actual Netlify domain
    '*'  # Temporarily allow all origins for testing
]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 