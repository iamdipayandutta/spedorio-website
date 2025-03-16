from app import app, db, User, Category, Post
from datetime import datetime

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(username='admin', email='sp3dorio@gmail.com')
            admin.set_password('admin123')  # Change this to a secure password
            db.session.add(admin)
            db.session.commit()
            print("Admin user created")
        
        # Create categories if they don't exist
        categories = [
            {'name': 'Web Development', 'slug': 'web-development', 'icon': 'fa-code'},
            {'name': 'UI/UX Design', 'slug': 'ui-ux-design', 'icon': 'fa-paint-brush'},
            {'name': 'Innovation', 'slug': 'innovation', 'icon': 'fa-lightbulb'}
        ]
        
        for cat_data in categories:
            category = Category.query.filter_by(slug=cat_data['slug']).first()
            if not category:
                category = Category(
                    name=cat_data['name'],
                    slug=cat_data['slug'],
                    icon=cat_data['icon']
                )
                db.session.add(category)
                print(f"Category {cat_data['name']} created")
        
        db.session.commit()
        
        # Create sample posts if none exist
        if Post.query.count() == 0:
            web_dev = Category.query.filter_by(slug='web-development').first()
            ui_ux = Category.query.filter_by(slug='ui-ux-design').first()
            innovation = Category.query.filter_by(slug='innovation').first()
            
            posts = [
                {
                    'title': 'The Future of Web Development: What\'s Next?',
                    'slug': 'future-of-web-development',
                    'content': """
# The Future of Web Development

Web development is constantly evolving, with new technologies and approaches emerging regularly. Here are some trends that are shaping the future of web development:

## AI Integration

Artificial intelligence is becoming increasingly integrated into web applications. From chatbots to personalized content recommendations, AI is enhancing user experiences and automating complex tasks.

## WebAssembly

WebAssembly (Wasm) allows high-performance code written in languages like C, C++, and Rust to run in the browser. This opens up new possibilities for web applications, including games, video editing, and more.

## Serverless Architecture

Serverless computing allows developers to build and run applications without managing servers. This approach can lead to reduced costs, improved scalability, and faster development cycles.

## Progressive Web Apps (PWAs)

PWAs combine the best of web and mobile apps, offering offline capabilities, push notifications, and app-like experiences. They're becoming increasingly popular due to their cross-platform nature and improved user engagement.

## Conclusion

The future of web development is exciting, with new technologies making it possible to create more powerful, efficient, and user-friendly applications. Staying updated with these trends is essential for any web developer looking to remain competitive in the field.
                    """,
                    'summary': 'Exploring the latest trends and technologies shaping the future of web development, from AI integration to WebAssembly.',
                    'read_time': 5,
                    'published': True,
                    'category_id': web_dev.id,
                    'user_id': admin.id
                },
                {
                    'title': 'Creating User-Centric Design Experiences',
                    'slug': 'user-centric-design-experiences',
                    'content': """
# Creating User-Centric Design Experiences

User-centric design puts the user at the center of the design process. Here's how to create experiences that users will love:

## Understand Your Users

Before designing anything, you need to understand who your users are, what they need, and how they behave. User research, personas, and journey maps can help you gain these insights.

## Focus on Usability

A beautiful design is worthless if users can't figure out how to use it. Prioritize clarity, consistency, and simplicity in your designs.

## Design for Accessibility

Accessible design ensures that your product can be used by everyone, including people with disabilities. This includes considerations for color contrast, keyboard navigation, and screen reader compatibility.

## Test with Real Users

User testing is crucial for validating your design decisions. Observe how real users interact with your product and iterate based on their feedback.

## Conclusion

User-centric design is not just about creating aesthetically pleasing interfaces; it's about solving real problems for real people. By putting users at the center of your design process, you can create experiences that are not only beautiful but also useful and usable.
                    """,
                    'summary': 'A deep dive into the principles of user-centric design and how to create interfaces that users love.',
                    'read_time': 4,
                    'published': True,
                    'category_id': ui_ux.id,
                    'user_id': admin.id
                },
                {
                    'title': 'Emerging Technologies in 2024',
                    'slug': 'emerging-technologies-2024',
                    'content': """
# Emerging Technologies in 2024

Technology is evolving at an unprecedented pace. Here are some of the most exciting technological innovations that are shaping 2024:

## Quantum Computing

Quantum computing is moving from theoretical to practical applications. Companies are beginning to use quantum computers to solve complex problems in fields like cryptography, drug discovery, and optimization.

## Extended Reality (XR)

XR, which encompasses virtual reality (VR), augmented reality (AR), and mixed reality (MR), is becoming more mainstream. From immersive gaming experiences to virtual workspaces, XR is changing how we interact with digital content.

## Sustainable Tech

As environmental concerns grow, so does the focus on sustainable technology. This includes energy-efficient hardware, carbon-neutral data centers, and software designed to minimize resource usage.

## Edge Computing

Edge computing brings computation and data storage closer to the location where it's needed, reducing latency and bandwidth use. This is particularly important for IoT devices and real-time applications.

## Conclusion

These emerging technologies are not just changing the tech landscape; they're reshaping industries and creating new opportunities for innovation. Staying informed about these developments is crucial for anyone working in technology or looking to leverage tech for business advantage.
                    """,
                    'summary': 'An overview of the most exciting technological innovations and their impact on software development.',
                    'read_time': 6,
                    'published': True,
                    'category_id': innovation.id,
                    'user_id': admin.id
                }
            ]
            
            for post_data in posts:
                post = Post(**post_data)
                db.session.add(post)
                print(f"Post '{post_data['title']}' created")
            
            db.session.commit()
            print("Sample posts created")
        
        print("Database initialization complete")

if __name__ == '__main__':
    init_db() 