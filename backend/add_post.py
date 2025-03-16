from app import app, db, User, Category, Post
from datetime import datetime

def add_new_post():
    with app.app_context():
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
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        print(f"New post '{new_post.title}' added successfully!")

if __name__ == '__main__':
    add_new_post() 