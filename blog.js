// Blog API Integration
const API_BASE_URL = 'http://localhost:5000/api';

// Fetch all blog posts
async function fetchBlogPosts() {
    try {
        const response = await fetch(`${API_BASE_URL}/posts`);
        if (!response.ok) {
            throw new Error('Failed to fetch posts');
        }
        const posts = await response.json();
        return posts;
    } catch (error) {
        console.error('Error fetching blog posts:', error);
        return [];
    }
}

// Fetch a single blog post by slug
async function fetchBlogPost(slug) {
    try {
        const response = await fetch(`${API_BASE_URL}/posts/${slug}`);
        if (!response.ok) {
            throw new Error('Failed to fetch post');
        }
        const post = await response.json();
        return post;
    } catch (error) {
        console.error(`Error fetching blog post ${slug}:`, error);
        return null;
    }
}

// Fetch all categories
async function fetchCategories() {
    try {
        const response = await fetch(`${API_BASE_URL}/categories`);
        if (!response.ok) {
            throw new Error('Failed to fetch categories');
        }
        const categories = await response.json();
        return categories;
    } catch (error) {
        console.error('Error fetching categories:', error);
        return [];
    }
}

// Fetch posts by category
async function fetchPostsByCategory(categorySlug) {
    try {
        const response = await fetch(`${API_BASE_URL}/categories/${categorySlug}/posts`);
        if (!response.ok) {
            throw new Error('Failed to fetch posts for category');
        }
        const posts = await response.json();
        return posts;
    } catch (error) {
        console.error(`Error fetching posts for category ${categorySlug}:`, error);
        return [];
    }
}

// Render blog posts in the blog section
async function renderBlogPosts() {
    const blogGrid = document.querySelector('.blog-grid');
    if (!blogGrid) return;
    
    const posts = await fetchBlogPosts();
    
    // Clear existing content
    blogGrid.innerHTML = '';
    
    if (posts.length === 0) {
        blogGrid.innerHTML = '<p class="text-center">No blog posts found.</p>';
        return;
    }
    
    // Display up to 3 posts
    const postsToShow = posts.slice(0, 3);
    
    postsToShow.forEach(post => {
        const articleHtml = `
            <article class="blog-card">
                <div class="blog-image">
                    <img src="${post.featured_image ? `/backend/static/uploads/${post.featured_image}` : 'assets/blog-placeholder.jpg'}" alt="${post.title}">
                    <div class="blog-category">${post.category}</div>
                </div>
                <div class="blog-content">
                    <div class="blog-meta">
                        <span><i class="far fa-calendar"></i> ${post.created_at}</span>
                        <span><i class="far fa-clock"></i> ${post.read_time} min read</span>
                    </div>
                    <h3>${post.title}</h3>
                    <p>${post.summary}</p>
                    <a href="blog-post.html?slug=${post.slug}" class="read-more">Read More <i class="fas fa-arrow-right"></i></a>
                </div>
            </article>
        `;
        
        blogGrid.innerHTML += articleHtml;
    });
}

// Render a single blog post
async function renderBlogPost() {
    const blogContent = document.querySelector('.blog-post-content');
    if (!blogContent) return;
    
    // Get slug from URL
    const urlParams = new URLSearchParams(window.location.search);
    const slug = urlParams.get('slug');
    
    if (!slug) {
        blogContent.innerHTML = '<p class="text-center">Blog post not found.</p>';
        return;
    }
    
    const post = await fetchBlogPost(slug);
    
    if (!post) {
        blogContent.innerHTML = '<p class="text-center">Blog post not found.</p>';
        return;
    }
    
    // Update page title
    document.title = `${post.title} - Dipayan Dutta Blog`;
    
    // Convert Markdown content to HTML (requires marked.js)
    const contentHtml = typeof marked !== 'undefined' ? marked.parse(post.content) : post.content;
    
    const postHtml = `
        <div class="blog-post-header">
            <h1>${post.title}</h1>
            <div class="blog-post-meta">
                <span><i class="far fa-calendar"></i> ${post.created_at}</span>
                <span><i class="far fa-clock"></i> ${post.read_time} min read</span>
                <span><i class="far fa-folder"></i> ${post.category}</span>
            </div>
        </div>
        
        <div class="blog-post-featured-image">
            <img src="${post.featured_image ? `/backend/static/uploads/${post.featured_image}` : 'assets/blog-placeholder.jpg'}" alt="${post.title}">
        </div>
        
        <div class="blog-post-body">
            ${contentHtml}
        </div>
        
        <div class="blog-post-author">
            <p>Written by <strong>${post.author}</strong></p>
        </div>
    `;
    
    blogContent.innerHTML = postHtml;
}

// Update sidebar categories
async function updateSidebarCategories() {
    const categoriesList = document.querySelector('.sidebar-section:nth-child(2) ul');
    if (!categoriesList) return;
    
    const categories = await fetchCategories();
    
    if (categories.length === 0) return;
    
    // Clear existing categories
    categoriesList.innerHTML = '';
    
    categories.forEach(category => {
        const categoryHtml = `
            <li>
                <a href="blog-category.html?category=${category.slug}">
                    <div class="category-indicator"></div>
                    <div class="link-content">
                        <i class="fas ${category.icon}"></i>
                        ${category.name}
                    </div>
                    <i class="fas fa-chevron-right nav-arrow"></i>
                </a>
            </li>
        `;
        
        categoriesList.innerHTML += categoryHtml;
    });
}

// Initialize blog functionality
document.addEventListener('DOMContentLoaded', function() {
    // Render blog posts on the home page
    renderBlogPosts();
    
    // Render single blog post on the blog post page
    if (window.location.pathname.includes('blog-post.html')) {
        renderBlogPost();
    }
    
    // Update sidebar categories
    updateSidebarCategories();
}); 