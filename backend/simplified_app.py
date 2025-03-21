from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'development-key'
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Sample data for testing
posts = [
    {
        'id': 1,
        'title': 'Getting Started with Python and AI',
        'slug': 'getting-started-python-ai',
        'summary': 'A beginner\'s guide to Python for AI development',
        'featured_image': '/static/blog/images/python-ai.jpg',
        'read_time': 5,
        'created_at': 'March 15, 2024',
        'category': 'Programming',
        'category_slug': 'programming',
        'author': 'Dipayan Dutta'
    },
    {
        'id': 2,
        'title': 'Creating User-Centric Design Experiences',
        'slug': 'creating-user-centric-design',
        'summary': 'How to design digital products with users in mind',
        'featured_image': '/static/blog/images/ux-design.jpg',
        'read_time': 4,
        'created_at': 'March 10, 2024',
        'category': 'UI/UX Design',
        'category_slug': 'ui-ux-design',
        'author': 'Dipayan Dutta'
    },
    {
        'id': 3,
        'title': 'Emerging Technologies in 2024',
        'slug': 'emerging-technologies-2024',
        'summary': 'An overview of the most exciting technological innovations',
        'featured_image': '/static/blog/images/emerging-tech.jpg',
        'read_time': 6,
        'created_at': 'March 5, 2024',
        'category': 'Innovation',
        'category_slug': 'innovation',
        'author': 'Dipayan Dutta'
    }
]

categories = [
    {
        'id': 1,
        'name': 'Programming',
        'slug': 'programming',
        'icon': 'fa-code'
    },
    {
        'id': 2,
        'name': 'UI/UX Design',
        'slug': 'ui-ux-design',
        'icon': 'fa-paint-brush'
    },
    {
        'id': 3,
        'name': 'Innovation',
        'slug': 'innovation',
        'icon': 'fa-lightbulb'
    }
]

# API Routes
@app.route('/api/posts')
def get_posts():
    return jsonify(posts)

@app.route('/api/posts/<slug>')
def get_post(slug):
    post = next((post for post in posts if post['slug'] == slug), None)
    if post:
        post_data = post.copy()
        post_data['content'] = f"This is the content for {post['title']}"
        return jsonify(post_data)
    return jsonify({'error': 'Post not found'}), 404

@app.route('/api/categories')
def get_categories():
    return jsonify(categories)

@app.route('/api/categories/<slug>/posts')
def get_category_posts(slug):
    category_posts = [post for post in posts if post['category_slug'] == slug]
    return jsonify(category_posts)

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'online',
        'message': 'API is running and available for connections from Netlify'
    })

# Simple authentication endpoint for testing
@app.route('/api/auth/login', methods=['POST'])
def login_api():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    # Very simple auth for testing
    if username == 'admin' and password == 'password':
        return jsonify({
            'success': True,
            'user': {
                'username': username,
                'is_admin': True
            }
        })
    return jsonify({
        'success': False,
        'message': 'Invalid credentials'
    }), 401

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 