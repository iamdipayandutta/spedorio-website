from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'development-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)
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

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(200), nullable=True)
    url = db.Column(db.String(500), nullable=False)
    github_url = db.Column(db.String(500), nullable=True)
    tech_stack = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image': self.image,
            'url': self.url,
            'github_url': self.github_url,
            'tech_stack': self.tech_stack.split(',') if self.tech_stack else [],
            'created_at': self.created_at.strftime('%B %d, %Y')
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    # Check if user is logged in and is admin
    is_admin = current_user.is_authenticated and current_user.is_admin and current_user.username == 'admin'
    
    # Store admin status in session
    session['is_admin'] = is_admin
    
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
            // Handle edit buttons visibility
            if (window.authStatus.is_admin && window.authStatus.username === 'admin') {{
                document.querySelectorAll('.admin-controls').forEach(btn => {{
                    btn.style.display = 'block';
                }});
            }}
            
            // Handle sidebar account section
            const accountSection = document.querySelector('.sidebar-section:nth-child(2)');
            if (accountSection && accountSection.querySelector('h3').textContent === 'Account') {{
                const accountLinks = accountSection.querySelector('ul');
                
                if (window.authStatus.is_logged_in) {{
                    // User is logged in
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
                    
                    // Add username to the sidebar
                    const usernameElement = document.createElement('div');
                    usernameElement.className = 'user-info';
                    usernameElement.innerHTML = '<p>Logged in as: <strong>' + window.authStatus.username + '</strong></p>';
                    accountSection.insertBefore(usernameElement, accountLinks);
                }}
            }}
            
            // Remove auth buttons if they exist
            const authButtons = document.querySelector('.auth-buttons');
            if (authButtons) {{
                authButtons.remove();
            }}
            
            // Add project showcase section
            fetch('/api/projects')
                .then(response => response.json())
                .then(projects => {{
                    const projectSection = document.createElement('div');
                    projectSection.className = 'project-showcase';
                    projectSection.innerHTML = `
                        <h2>Project Showcase</h2>
                        <div class="project-grid">
                            ${{projects.map(project => `
                                <div class="project-card">
                                    <img src="/static/uploads/${{project.image}}" alt="${{project.title}}">
                                    <h3>${{project.title}}</h3>
                                    <p>${{project.description}}</p>
                                    <div class="tech-stack">
                                        ${{project.tech_stack.map(tech => `<span class="tech-tag">${{tech}}</span>`).join('')}}
                                    </div>
                                    <div class="project-links">
                                        <a href="${{project.url}}" target="_blank" class="project-link">Live Demo</a>
                                        ${{project.github_url ? `
                                            <a href="${{project.github_url}}" target="_blank" class="project-link github">
                                                <i class="fab fa-github"></i> Code
                                            </a>
                                        ` : ''}}
                                    </div>
                                </div>
                            `).join('')}}
                        </div>
                    `;
                    
                    // Insert project section before the footer
                    const footer = document.querySelector('footer');
                    if (footer) {{
                        footer.parentNode.insertBefore(projectSection, footer);
                    }}
                }});
        }});
    </script>
    """
    
    # Use render_template_string to create HTML content with the auth script injected
    try:
        # Get the index.html content
        with open('../index.html', 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Replace relative paths with absolute paths
        content = content.replace('href="styles.css"', 'href="/styles.css"')
        content = content.replace('src="assets/', 'src="/assets/')
        
        # Add flash messages template
        flash_messages = render_template('flash_messages.html')
        
        # Inject auth script and flash messages before </body>
        modified_content = content.replace('</body>', f'{flash_messages}{auth_script}</body>')
        
        # Return the modified content with proper MIME type
        response = app.make_response(modified_content)
        response.mimetype = 'text/html'
        return response
    except Exception as e:
        print(f"Error serving index.html: {e}")
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

@app.route('/api/projects')
def get_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return jsonify([project.to_dict() for project in projects])

# User authentication routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('user_dashboard'))
    
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
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            
            # Set admin status in session
            session['is_admin'] = user.is_admin and user.username == 'admin'
            
            db.session.commit()
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
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
    # Clear admin status from session
    session.pop('is_admin', None)
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
        flash('Post created successfully!')
        return redirect(url_for('admin_posts'))
    
    return render_template('admin/post_form.html', categories=categories)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin or current_user.username != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/edit-post/<int:post_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
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
        flash('Post updated successfully!', 'success')
        return redirect(url_for('admin_posts'))
        
    return render_template('admin/post_form.html', post=post, categories=categories)

@app.route('/admin/posts/<int:post_id>/edit')
@login_required
@admin_required
def frontend_edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    return redirect(url_for('edit_post', post_id=post.id))

@app.route('/admin/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.is_admin:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully.', 'success')
    return redirect(url_for('manage_posts'))

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

@app.route('/admin/projects')
@login_required
@admin_required
def admin_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('admin/projects.html', projects=projects)

@app.route('/admin/projects/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        url = request.form.get('url')
        github_url = request.form.get('github_url')
        tech_stack = request.form.get('tech_stack')
        
        # Handle image upload
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        project = Project(
            title=title,
            description=description,
            image=image,
            url=url,
            github_url=github_url,
            tech_stack=tech_stack
        )
        
        db.session.add(project)
        db.session.commit()
        flash('Project added successfully!', 'success')
        return redirect(url_for('admin_projects'))
    
    return render_template('admin/project_form.html')

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
def user_dashboard():
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
    
    # Get recent posts
    recent_posts = Post.query.filter_by(published=True).order_by(Post.created_at.desc()).limit(4).all()
    
    # Get categories
    categories = Category.query.all()
    
    return render_template('auth/dashboard.html',
                          days_since_joined=days_since_joined,
                          days_since_last_login=days_since_last_login,
                          total_posts=total_posts,
                          recent_posts=recent_posts,
                          categories=categories)

# Spotify callback route
@app.route('/callback')
def spotify_callback():
    try:
        # Get the index.html content
        with open('../index.html', 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Replace relative paths with absolute paths
        content = content.replace('href="styles.css"', 'href="/styles.css"')
        content = content.replace('src="assets/', 'src="/assets/')
        content = content.replace('src="scripts/', 'src="/scripts/')
        
        # Return the modified content with proper MIME type
        response = app.make_response(content)
        response.mimetype = 'text/html'
        return response
    except Exception as e:
        print(f"Error in spotify_callback: {e}")
        return redirect('/')

@app.route('/scripts/<path:filename>')
def serve_scripts(filename):
    return send_from_directory('../scripts', filename)

# Create admin user function
def create_admin_user():
    try:
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully")
        else:
            # Ensure existing admin user has admin privileges
            if not admin.is_admin:
                admin.is_admin = True
                db.session.commit()
                print("Existing admin user updated with admin privileges")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# Create tables and admin user
def init_db():
    with app.app_context():
        db.create_all()
        create_admin_user()
        
        # Add sample project if none exist
        if not Project.query.first():
            sample_project = Project(
                title='Sample Project',
                description='This is a sample project to showcase the layout.',
                url='https://example.com',
                github_url='https://github.com/yourusername/sample-project',
                tech_stack='Python,Flask,JavaScript',
                image='sample-project.png'
            )
            db.session.add(sample_project)
            db.session.commit()

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)