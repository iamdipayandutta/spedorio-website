from app import app, db
import sqlite3
import os

def list_posts():
    # Connect directly to the SQLite database in the instance folder
    db_path = os.path.join('instance', 'blog.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return
    
    print(f"Using database at {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all posts
    cursor.execute('''
        SELECT p.id, p.title, p.slug, p.category_id, c.name, p.user_id, u.username, 
               p.published, p.created_at, p.summary
        FROM post p
        LEFT JOIN category c ON p.category_id = c.id
        LEFT JOIN user u ON p.user_id = u.id
    ''')
    
    posts = cursor.fetchall()
    
    print(f"Total posts: {len(posts)}")
    for post in posts:
        post_id, title, slug, category_id, category_name, user_id, username, published, created_at, summary = post
        
        print(f"\nPost ID: {post_id}")
        print(f"Title: {title}")
        print(f"Slug: {slug}")
        print(f"Category ID: {category_id}")
        print(f"Category: {category_name}")
        print(f"User ID: {user_id}")
        print(f"Author: {username}")
        print(f"Published: {'Yes' if published else 'No'}")
        print(f"Created: {created_at}")
        
        if summary:
            summary_text = summary[:50] + "..." if len(summary) > 50 else summary
            print(f"Summary: {summary_text}")
        else:
            print("Summary: None")
    
    # Close the connection
    conn.close()

if __name__ == "__main__":
    list_posts() 