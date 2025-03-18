from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)  # Enable CORS for API endpoints
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    posts = db.relationship('Post', backref='author', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    icon = db.Column(db.String(50), nullable=True)
    posts = db.relationship('Post', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(300), nullable=True)
    featured_image = db.Column(db.String(200), nullable=True)
    read_time = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<Post {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'summary': self.summary,
            'featured_image': self.featured_image,
            'read_time': self.read_time,
            'created_at': self.created_at.strftime('%B %d, %Y'),
            'category': self.category.name,
            'category_slug': self.category.slug,
            'author': self.author.username
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    # Check if user is logged in
    auth_status = {
        'is_logged_in': 'true' if current_user.is_authenticated else 'false',
        'username': current_user.username if current_user.is_authenticated else ''
    }
    
    # Create script to inject authentication status into the frontend
    auth_script = f"""
    <script>
        window.authStatus = {{
            is_logged_in: {auth_status['is_logged_in']},
            username: "{auth_status['username']}"
        }};
        
        document.addEventListener('DOMContentLoaded', function() {{
            const accountSection = document.querySelector('.sidebar-section:nth-child(2)');
            if (accountSection && accountSection.querySelector('h3').textContent === 'Account') {{
                const accountLinks = accountSection.querySelector('ul');
                
                if (window.authStatus.is_logged_in) {{
                    // User is logged in
                    accountLinks.innerHTML = `
                        <li>
                            <a href="/profile" class="sidebar-link">
                                <i class="fas fa-user-circle"></i>
                                <span>My Profile</span>
                                <i class="fas fa-chevron-right nav-arrow"></i>
                            </a>
                        </li>
                        <li>
                            <a href="/logout" class="sidebar-link">
                                <i class="fas fa-sign-out-alt"></i>
                                <span>Logout</span>
                                <i class="fas fa-chevron-right nav-arrow"></i>
                            </a>
                        </li>
                    `;
                    
                    // Add username to the sidebar
                    const usernameElement = document.createElement('div');
                    usernameElement.className = 'user-info';
                    usernameElement.innerHTML = '<p>Logged in as: <strong>' + window.authStatus.username + '</strong></p>';
                    accountSection.insertBefore(usernameElement, accountLinks);
                }}
            }}
        }});
    </script>
    """
    
    # Use render_template_string to create HTML content with the auth script injected
    try:
        # Get the index.html content
        with open('../index.html', 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Inject auth script before </body>
        modified_content = content.replace('</body>', f'{auth_script}</body>')
        
        # Return the modified content with proper MIME type
        response = app.make_response(modified_content)
        response.mimetype = 'text/html'
        return response
    except Exception as e:
        # If there's an error, fallback to the direct approach
        return send_from_directory('../', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Serve other static files like CSS, JS, images
    return send_from_directory('../', path)

# Admin routes start at /admin
@app.route('/admin')
def admin_index():
    return render_template('admin/index.html')

# API Routes
@app.route('/api/posts')
def get_posts():
    posts = Post.query.filter_by(published=True).order_by(Post.created_at.desc()).all()
    return jsonify([post.to_dict() for post in posts])

@app.route('/api/posts/<slug>')
def get_post(slug):
    post = Post.query.filter_by(slug=slug, published=True).first_or_404()
    post_data = post.to_dict()
    post_data['content'] = post.content
    return jsonify(post_data)

@app.route('/api/categories')
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': category.id,
        'name': category.name,
        'slug': category.slug,
        'icon': category.icon
    } for category in categories])

@app.route('/api/categories/<slug>/posts')
def get_category_posts(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    posts = Post.query.filter_by(category_id=category.id, published=True).order_by(Post.created_at.desc()).all()
    return jsonify([post.to_dict() for post in posts])

# User authentication routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form data
        if not username or not email or not password or not confirm_password:
            flash('All fields are required', 'danger')
            return render_template('auth/signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/signup.html')
        
        # Check if user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists', 'danger')
            return render_template('auth/signup.html')
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/signup.html')

@app.route('/login', methods=['GET', 'POST'])
def public_login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

# Now update the existing admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('admin/login.html')

# Update logout route to handle both public and admin logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    posts_count = Post.query.count()
    categories_count = Category.query.count()
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', 
                          posts_count=posts_count, 
                          categories_count=categories_count,
                          recent_posts=recent_posts)

@app.route('/admin/posts')
@login_required
def admin_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/posts.html', posts=posts)

@app.route('/admin/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    categories = Category.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content')
        summary = request.form.get('summary')
        category_id = request.form.get('category_id')
        read_time = request.form.get('read_time', 5)
        published = 'published' in request.form
        
        # Handle image upload
        featured_image = None
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                featured_image = filename
        
        post = Post(
            title=title,
            slug=slug,
            content=content,
            summary=summary,
            featured_image=featured_image,
            read_time=read_time,
            published=published,
            category_id=category_id,
            user_id=current_user.id
        )
        
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!')
        return redirect(url_for('admin_posts'))
    
    return render_template('admin/post_form.html', categories=categories)

@app.route('/admin/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.slug = request.form.get('slug')
        post.content = request.form.get('content')
        post.summary = request.form.get('summary')
        post.category_id = request.form.get('category_id')
        post.read_time = request.form.get('read_time', 5)
        post.published = 'published' in request.form
        
        # Handle image upload
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                post.featured_image = filename
        
        db.session.commit()
        flash('Post updated successfully!')
        return redirect(url_for('admin_posts'))
    
    return render_template('admin/post_form.html', post=post, categories=categories)

@app.route('/admin/posts/delete/<int:id>', methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!')
    return redirect(url_for('admin_posts'))

@app.route('/admin/categories')
@login_required
def admin_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/new', methods=['GET', 'POST'])
@login_required
def new_category():
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        icon = request.form.get('icon')
        
        category = Category(name=name, slug=slug, icon=icon)
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/category_form.html')

@app.route('/admin/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.slug = request.form.get('slug')
        category.icon = request.form.get('icon')
        
        db.session.commit()
        flash('Category updated successfully!')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/category_form.html', category=category)

@app.route('/admin/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!')
    return redirect(url_for('admin_categories'))

# Profile management routes
@app.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    email = request.form.get('email')
    
    if not email:
        flash('Email is required', 'danger')
        return redirect(url_for('profile'))
    
    # Check if email already exists
    existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
    if existing_user:
        flash('Email already in use by another account', 'danger')
        return redirect(url_for('profile'))
    
    current_user.email = email
    db.session.commit()
    flash('Profile updated successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        flash('All fields are required', 'danger')
        return redirect(url_for('profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'danger')
        return redirect(url_for('profile'))
    
    if not current_user.check_password(current_password):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    flash('Password changed successfully', 'success')
    return redirect(url_for('profile'))

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 