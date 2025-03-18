from app import app, db, User
import re
from bs4 import BeautifulSoup

def test_signup_form():
    with app.test_client() as client:
        # Get the signup page to retrieve the CSRF token
        response = client.get('/signup')
        print(f"GET /signup status code: {response.status_code}")
        
        # Extract CSRF token from the form using BeautifulSoup
        soup = BeautifulSoup(response.data, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        print(f"Extracted CSRF token: {csrf_token[:10]}...")
        
        # Create test data
        test_username = "formtest"
        test_email = "formtest@example.com"
        test_password = "password123"
        
        data = {
            'csrf_token': csrf_token,
            'username': test_username,
            'email': test_email,
            'password': test_password,
            'confirm_password': test_password
        }
        
        # Post the form data
        response = client.post('/signup', data=data, follow_redirects=True)
        print(f"POST /signup status code: {response.status_code}")
        
        # Check if we got redirected to login page successfully
        soup = BeautifulSoup(response.data, 'html.parser')
        title = soup.find('title')
        print(f"Redirected to page with title: {title.text if title else 'Unknown'}")
        
        # Check for flash messages
        flash_messages = soup.find_all(class_='alert')
        for msg in flash_messages:
            print(f"Flash message: {msg.text.strip()}")
        
        # Verify user creation
        with app.app_context():
            user = User.query.filter_by(username=test_username).first()
            if user:
                print(f"User {test_username} created successfully with ID: {user.id}")
            else:
                print(f"Failed to create user {test_username}")

if __name__ == '__main__':
    test_signup_form() 