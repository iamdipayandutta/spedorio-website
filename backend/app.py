from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_session import Session
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from routes.api import api  # Import the API blueprint

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # Set CSRF token expiration to 1 hour

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# Cache invalidation mechanism
app.config['LAST_MODIFIED'] = datetime.utcnow()

# Function to update last modified timestamp for cache invalidation
def update_last_modified():
    app.config['LAST_MODIFIED'] = datetime.utcnow()

# Ensure upload and session directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

# Initialize extensions
Session(app)  # Initialize Flask-Session first
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)  # Enable CORS for API endpoints
login_manager = LoginManager(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)

# Configure CSRF to exempt API routes
@csrf.exempt
def csrf_exempt_api():
    if request.path.startswith('/api/'):
        return True
    return False

csrf._exempt_views.add(csrf_exempt_api)

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
    is_admin = current_user.is_authenticated and current_user.username == 'admin'
    auth_status = {
        'is_logged_in': 'true' if current_user.is_authenticated else 'false',
        'username': current_user.username if current_user.is_authenticated else '',
        'is_admin': 'true' if is_admin else 'false'
    }
    # Create script to inject authentication status into the frontend
    auth_script = f"""
    <script>
        window.authStatus = {{
            is_logged_in: {auth_status['is_logged_in']},
            username: "{auth_status['username']}",
            is_admin: {auth_status['is_admin']}
        }};
        document.addEventListener('DOMContentLoaded', function() {{
            // Hide/show admin-only elements
            if (window.authStatus && window.authStatus.is_admin === 'true') {{
                document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'block');
            }} else {{
                document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'none');
            }}
            // Handle sidebar account section
            const accountSection = document.querySelector('.sidebar-section:nth-child(2)');
            if (accountSection && accountSection.querySelector('h3').textContent === 'Account') {{
                const accountLinks = accountSection.querySelector('ul');
                if (window.authStatus.is_logged_in === 'true') {{
                    accountLinks.innerHTML = `
                        <li>
                            <a href="/dashboard" class="sidebar-link">
                                <i class="fas fa-user-circle"></i>
                                <span>Dashboard</span>
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
                    const usernameElement = document.createElement('div');
                    usernameElement.className = 'user-info';
                    usernameElement.innerHTML = '<p>Logged in as: <strong>' + window.authStatus.username + '</strong></p>';
                    accountSection.insertBefore(usernameElement, accountLinks);
                }}
            }}
            // Toggle auth buttons in nav
            const authButtons = document.querySelector('.auth-buttons');
            if (authButtons) {{
                if (window.authStatus.is_logged_in === 'true' && window.authStatus.is_admin === 'true') {{
                    authButtons.innerHTML = `
                        <a href="/dashboard" class="auth-btn login-btn">Dashboard</a>
                        <a href="/logout" class="auth-btn signup-btn">Logout</a>
                    `;
                }} else {{
                    authButtons.innerHTML = '';
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

# Register blueprints
app.register_blueprint(api, url_prefix='/api')

# API Routes
@app.route('/api/posts')
def get_posts():
    posts = Post.query.filter_by(published=True).order_by(Post.created_at.desc()).all()
    response = jsonify([post.to_dict() for post in posts])
    # Add cache control headers to prevent browser caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = app.config['LAST_MODIFIED'].strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

@app.route('/api/posts/<slug>')
def get_post(slug):
    post = Post.query.filter_by(slug=slug, published=True).first_or_404()
    post_data = post.to_dict()
    post_data['content'] = post.content
    response = jsonify(post_data)
    # Add cache control headers to prevent browser caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = app.config['LAST_MODIFIED'].strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

@app.route('/api/categories')
def get_categories():
    categories = Category.query.all()
    response = jsonify([{
        'id': category.id,
        'name': category.name,
        'slug': category.slug,
        'icon': category.icon
    } for category in categories])
    # Add cache control headers to prevent browser caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = app.config['LAST_MODIFIED'].strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

@app.route('/api/categories/<slug>/posts')
def get_category_posts(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    posts = Post.query.filter_by(category_id=category.id, published=True).order_by(Post.created_at.desc()).all()
    response = jsonify([post.to_dict() for post in posts])
    # Add cache control headers to prevent browser caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = app.config['LAST_MODIFIED'].strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

@app.route('/api/check-updates')
def check_updates():
    """Check if there have been any updates to the blog content"""
    last_modified = app.config['LAST_MODIFIED'].strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # Check if client sent If-Modified-Since header
    if_modified_since = request.headers.get('If-Modified-Since')
    
    if if_modified_since:
        try:
            # Parse the If-Modified-Since header
            ims_date = datetime.strptime(if_modified_since, '%a, %d %b %Y %H:%M:%S GMT')
            
            # Convert last_modified to datetime for comparison
            last_mod_date = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S GMT')
            
            # If client's version is current, return 304 Not Modified
            if ims_date >= last_mod_date:
                return '', 304
        except Exception as e:
            print(f"Error parsing If-Modified-Since header: {str(e)}")
    
    # Return 200 OK with Last-Modified header
    response = jsonify({'updated': True, 'last_modified': last_modified})
    response.headers['Last-Modified'] = last_modified
    return response

# User authentication routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
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
def login():
    if current_user.is_authenticated:
        print(f"User already authenticated, redirecting to dashboard")
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        print(f"Login attempt: username='{username}', password='{password}'")
        print(f"CSRF token present: {'csrf_token' in request.form}")
        
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User found: {user.username}, checking password...")
            is_valid = user.check_password(password)
            print(f"Password valid: {is_valid}")
            
            if is_valid:
                # Update last login time
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Login the user with a new session
                try:
                    login_user(user, remember=remember)
                    
                    # Add user info to session
                    session['user_id'] = user.id
                    session['username'] = user.username
                    session.modified = True
                    
                    print(f"User logged in, session cookie set")
                    print(f"current_user.is_authenticated: {current_user.is_authenticated}")
                    print(f"session data: {session}")
                    
                    # Force redirect to dashboard
                    response = redirect(url_for('dashboard'))
                    print(f"Redirecting to: {response.location}")
                    return response
                except Exception as e:
                    print(f"Error during login: {str(e)}")
                    flash(f"Login error: {str(e)}", 'danger')
        
        # If we get here, authentication failed
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
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
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
        
        # Update last-modified timestamp for cache invalidation
        update_last_modified()
        
        flash('Post created successfully!')
        return redirect(url_for('admin_posts'))
    
    # Create a form object with CSRF token for the template
    form = FlaskForm()
    
    return render_template('admin/post_form.html', categories=categories, form=form)

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
        
        # Update last-modified timestamp for cache invalidation
        update_last_modified()
        
        flash('Post updated successfully!')
        return redirect(url_for('admin_posts'))
    
    # Create a form object with CSRF token for the template
    form = FlaskForm()
    
    return render_template('admin/post_form.html', post=post, categories=categories, form=form)

@app.route('/admin/posts/delete/<int:id>', methods=['POST'])
@login_required
def delete_post(id):
    try:
        post = Post.query.get_or_404(id)
        
        # Optional: Add authorization check
        # if post.user_id != current_user.id and not current_user.is_admin:
        #     flash('You do not have permission to delete this post.', 'danger')
        #     return redirect(url_for('admin_posts'))
        
        # Store the title and slug for the flash message and cache invalidation
        title = post.title
        slug = post.slug
        category_id = post.category_id
        
        # Get the category for cache invalidation
        category = Category.query.get(category_id)
        category_slug = category.slug if category else None
        
        # Delete the post
        db.session.delete(post)
        db.session.commit()
        
        # Update last-modified timestamp for cache invalidation
        update_last_modified()
        
        flash(f'Post "{title}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting post: {str(e)}', 'danger')
        print(f"Error in delete_post: {str(e)}")
    
    return redirect(url_for('admin_posts'))

@app.route('/admin/posts/autosave', methods=['POST'])
@login_required
@csrf.exempt  # Exempt from CSRF for AJAX
def autosave_post():
    data = request.get_json()
    
    # Validate required fields
    if not data or 'content' not in data or 'title' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    try:
        # Handle existing post update
        if 'post_id' in data and data['post_id'] and data['post_id'] != 'new-post':
            post = Post.query.get(data['post_id'])
            
            if not post:
                return jsonify({'status': 'error', 'message': 'Post not found'}), 404
                
            # Check ownership
            if post.user_id != current_user.id:
                return jsonify({'status': 'error', 'message': 'Not authorized'}), 403
                
            # Update draft data
            post.title = data.get('title', post.title)
            post.content = data.get('content', post.content)
            post.summary = data.get('summary', post.summary)
            post.slug = data.get('slug', post.slug)
            if 'category_id' in data and data['category_id']:
                post.category_id = data['category_id']
            post.read_time = data.get('read_time', post.read_time)
            post.published = data.get('published', post.published)
            
            # Save in database
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Draft saved successfully',
                'post_id': post.id,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            # For new posts, just return success without saving to DB
            return jsonify({
                'status': 'success',
                'message': 'Draft saved locally',
                'timestamp': datetime.utcnow().isoformat()
            })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

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

@app.route('/dashboard')
@login_required
def dashboard():
    # Check if template exists
    template_path = os.path.join(app.root_path, 'templates', 'auth', 'dashboard.html')
    if not os.path.exists(template_path):
        print(f"WARNING: Dashboard template not found at {template_path}")
        flash("Dashboard template not found. Please check your installation.", "danger")
        return redirect(url_for('index'))
        
    try:
        # Calculate days since joined
        if current_user.created_at:
            delta = datetime.utcnow() - current_user.created_at
            days_since_joined = delta.days
        else:
            days_since_joined = 0
        
        # Calculate days since last login
        days_since_last_login = None
        if current_user.last_login:
            delta = datetime.utcnow() - current_user.last_login
            if delta.days > 0:
                days_since_last_login = delta.days
        
        # Get total posts count
        total_posts = Post.query.count()
        
        # Get recent posts (only for the current user)
        recent_posts = Post.query.filter_by(user_id=current_user.id, published=True).order_by(Post.created_at.desc()).limit(4).all()
        
        # Get categories
        categories = Category.query.all()
        
        return render_template('auth/dashboard.html',
                            days_since_joined=days_since_joined,
                            days_since_last_login=days_since_last_login,
                            total_posts=total_posts,
                            recent_posts=recent_posts,
                            categories=categories)
    except Exception as e:
        print(f"Error in dashboard route: {str(e)}")
        flash(f"Error loading dashboard: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def user_edit_post(id):
    # Get the post and verify ownership
    post = Post.query.get_or_404(id)
    
    # Check if current user is the author of the post
    if post.user_id != current_user.id:
        flash('You do not have permission to edit this post.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Redirect to the admin edit functionality
    return redirect(url_for('edit_post', id=id))

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)