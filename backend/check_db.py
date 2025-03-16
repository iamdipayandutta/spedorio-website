from app import app, db
from app import User, Category, Post

def check_db():
    with app.app_context():
        # Check users
        users = User.query.all()
        print(f"Users: {len(users)}")
        for user in users:
            print(f"  - {user.username} ({user.email})")
        print()

        # Check categories
        categories = Category.query.all()
        print(f"Categories: {len(categories)}")
        for category in categories:
            print(f"  - {category.name} (slug: {category.slug}, icon: {category.icon})")
        print()

        # Check posts
        posts = Post.query.all()
        print(f"Posts: {len(posts)}")
        
        # Print each post separately to avoid issues
        for post in posts:
            print(f"\nPost ID: {post.id}")
            print(f"Title: {post.title}")
            print(f"Slug: {post.slug}")
            print(f"Category ID: {post.category_id}")
            
            # Get category name
            category = Category.query.get(post.category_id)
            if category:
                print(f"Category: {category.name}")
            else:
                print("Category: Not found")
            
            print(f"User ID: {post.user_id}")
            
            # Get user name
            user = User.query.get(post.user_id)
            if user:
                print(f"Author: {user.username}")
            else:
                print("Author: Not found")
            
            print(f"Published: {'Yes' if post.published else 'No'}")
            print(f"Created: {post.created_at}")
            
            if post.summary:
                summary = post.summary[:50] + "..." if len(post.summary) > 50 else post.summary
                print(f"Summary: {summary}")
            else:
                print("Summary: None")

if __name__ == "__main__":
    check_db() 