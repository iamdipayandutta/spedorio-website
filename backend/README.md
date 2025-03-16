# Blog Backend for Dipayan Dutta's Portfolio

This is a Flask-based backend for managing blog content on Dipayan Dutta's portfolio website.

## Features

- RESTful API for blog posts and categories
- Admin dashboard for content management
- Markdown support for blog content
- Image upload functionality
- User authentication for admin access

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository (if you haven't already)

2. Navigate to the backend directory:
   ```
   cd backend
   ```

3. Create a virtual environment:
   ```
   python -m venv venv
   ```

4. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

6. Initialize the database:
   ```
   python init_db.py
   ```

### Running the Application

1. Start the Flask development server:
   ```
   python app.py
   ```

2. The server will start at `http://localhost:5000`

3. Access the admin dashboard at `http://localhost:5000/admin/login`
   - Default credentials:
     - Username: admin
     - Password: admin123 (change this in production)

## API Endpoints

- `GET /api/posts` - Get all published posts
- `GET /api/posts/<slug>` - Get a specific post by slug
- `GET /api/categories` - Get all categories
- `GET /api/categories/<slug>/posts` - Get posts by category

## Frontend Integration

To integrate with the frontend:

1. Include the `blog.js` file in your HTML:
   ```html
   <script src="blog.js"></script>
   ```

2. Make sure the API_BASE_URL in blog.js points to your backend:
   ```javascript
   const API_BASE_URL = 'http://localhost:5000/api';
   ```

3. The JavaScript will automatically fetch and display blog posts on your website.

## Deployment

For production deployment:

1. Set a secure SECRET_KEY in app.py
2. Change the default admin password
3. Consider using a production-ready database like PostgreSQL
4. Set up a proper web server (Nginx, Apache) with WSGI (Gunicorn, uWSGI)
5. Enable HTTPS

## License

This project is licensed under the MIT License. 