from app import app, db
from app import User, Category, Post
from datetime import datetime

def recreate_post():
    with app.app_context():
        # Find the post with title "Building a Flask Blog Backend"
        post = Post.query.filter_by(title="Building a Flask Blog Backend").first()
        
        if post:
            print(f"Found post: {post.title} (ID: {post.id})")
            print("Deleting post...")
            
            # Delete the post
            db.session.delete(post)
            db.session.commit()
            print("Post deleted successfully")
        
        # Get admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Admin user not found!")
            return
        
        # Get a category
        category = Category.query.filter_by(slug='web-development').first()
        if not category:
            print("Category not found!")
            return
        
        # Create a new post
        new_post = Post(
            title="Building a Flask Blog Backend",
            slug="building-flask-blog-backend",
            content="""
# Building a Flask Blog Backend

In this tutorial, we'll explore how to build a robust blog backend using Flask and SQLAlchemy.

## Setting Up the Environment

First, we need to set up our development environment:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)
```

## Creating Models

Next, we'll define our database models:

```python
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # More fields...
```

## Adding API Endpoints

Finally, we'll create API endpoints to serve our blog content:

```python
@app.route('/api/posts')
def get_posts():
    posts = Post.query.all()
    return jsonify([post.to_dict() for post in posts])
```

## Conclusion

With Flask and SQLAlchemy, building a blog backend is straightforward and flexible. This approach allows for easy integration with any frontend technology.
            """,
            summary="Learn how to build a robust blog backend using Flask and SQLAlchemy with a complete step-by-step guide.",
            read_time=8,
            published=True,
            category_id=category.id,
            user_id=admin.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        print(f"New post '{new_post.title}' created successfully with ID: {new_post.id}")
        
        # Verify the post
        created_post = Post.query.filter_by(title="Building a Flask Blog Backend").first()
        print("\nVerifying created post:")
        print(f"  ID: {created_post.id}")
        print(f"  Title: {created_post.title}")
        print(f"  Slug: {created_post.slug}")
        print(f"  Category ID: {created_post.category_id}")
        print(f"  User ID: {created_post.user_id}")
        print(f"  Published: {created_post.published}")
        print(f"  Created: {created_post.created_at}")
        
        # Test relationships
        try:
            print(f"  Category name: {created_post.category.name}")
        except Exception as e:
            print(f"  Category relationship error: {str(e)}")
        
        try:
            print(f"  Author name: {created_post.author.username}")
        except Exception as e:
            print(f"  Author relationship error: {str(e)}")

if __name__ == "__main__":
    recreate_post() 