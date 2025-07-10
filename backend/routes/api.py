from flask import Blueprint, jsonify, request
from app import db
from models import BlogPost, Category
from sqlalchemy import desc

api = Blueprint('api', __name__)

@api.route('/posts', methods=['GET'])
def get_posts():
    """Get all published blog posts"""
    posts = BlogPost.query.filter_by(published=True).order_by(desc(BlogPost.created_at)).all()
    return jsonify([{
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'summary': post.summary,
        'content': post.content,
        'featured_image': post.featured_image,
        'category': {
            'id': post.category.id,
            'name': post.category.name,
            'slug': post.category.slug
        } if post.category else None,
        'read_time': post.read_time,
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat() if post.updated_at else None
    } for post in posts])

@api.route('/posts/<slug>', methods=['GET'])
def get_post(slug):
    """Get a specific blog post by slug"""
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    return jsonify({
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'summary': post.summary,
        'content': post.content,
        'featured_image': post.featured_image,
        'category': {
            'id': post.category.id,
            'name': post.category.name,
            'slug': post.category.slug
        } if post.category else None,
        'read_time': post.read_time,
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat() if post.updated_at else None
    })

@api.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    categories = Category.query.all()
    return jsonify([{
        'id': category.id,
        'name': category.name,
        'slug': category.slug
    } for category in categories])

@api.route('/categories/<slug>/posts', methods=['GET'])
def get_posts_by_category(slug):
    """Get all published posts in a specific category"""
    category = Category.query.filter_by(slug=slug).first_or_404()
    posts = BlogPost.query.filter_by(category_id=category.id, published=True).order_by(desc(BlogPost.created_at)).all()
    return jsonify([{
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'summary': post.summary,
        'content': post.content,
        'featured_image': post.featured_image,
        'category': {
            'id': category.id,
            'name': category.name,
            'slug': category.slug
        },
        'read_time': post.read_time,
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat() if post.updated_at else None
    } for post in posts])

@api.route('/check-updates', methods=['GET'])
def check_updates():
    """Check for any blog updates"""
    latest_post = BlogPost.query.filter_by(published=True).order_by(desc(BlogPost.updated_at)).first()
    if latest_post:
        return jsonify({
            'last_update': latest_post.updated_at.isoformat(),
            'has_updates': True
        })
    return jsonify({
        'has_updates': False
    }) 