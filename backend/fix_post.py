from app import app, db
from app import User, Category, Post
from datetime import datetime

def fix_posts():
    with app.app_context():
        # Find the post with title "Building a Flask Blog Backend"
        post = Post.query.filter_by(title="Building a Flask Blog Backend").first()
        
        if post:
            print(f"Found post: {post.title} (ID: {post.id})")
            print(f"Current details:")
            print(f"  Slug: {post.slug}")
            print(f"  Category ID: {post.category_id}")
            print(f"  User ID: {post.user_id}")
            print(f"  Published: {post.published}")
            print(f"  Created: {post.created_at}")
            print(f"  Summary: {post.summary[:50]}..." if post.summary and len(post.summary) > 50 else f"  Summary: {post.summary}")
            
            # Get the Web Development category
            web_dev_category = Category.query.filter_by(slug="web-development").first()
            print(f"\nWeb Development category: {web_dev_category.id if web_dev_category else 'Not found'}")
            
            # Get the admin user
            admin_user = User.query.filter_by(username="admin").first()
            print(f"Admin user: {admin_user.id if admin_user else 'Not found'}")
            
            if web_dev_category and admin_user:
                # Update the post with all required fields
                post.category_id = web_dev_category.id
                post.user_id = admin_user.id
                post.published = True
                
                # Ensure all required fields are set
                if not post.created_at:
                    post.created_at = datetime.utcnow()
                
                if not post.updated_at:
                    post.updated_at = datetime.utcnow()
                
                if not post.read_time:
                    post.read_time = 8
                
                db.session.commit()
                
                # Verify the post after update
                updated_post = Post.query.get(post.id)
                print("\nPost updated successfully!")
                print(f"  Category ID: {updated_post.category_id}")
                print(f"  User ID: {updated_post.user_id}")
                print(f"  Published: {updated_post.published}")
                print(f"  Created: {updated_post.created_at}")
                print(f"  Updated: {updated_post.updated_at}")
                print(f"  Read time: {updated_post.read_time}")
                
                # Test relationships
                try:
                    print(f"  Category name: {updated_post.category.name}")
                except Exception as e:
                    print(f"  Category relationship error: {str(e)}")
                
                try:
                    print(f"  Author name: {updated_post.author.username}")
                except Exception as e:
                    print(f"  Author relationship error: {str(e)}")
            else:
                print("Could not find required category or user")
        else:
            print("Post 'Building a Flask Blog Backend' not found")

if __name__ == "__main__":
    fix_posts() 