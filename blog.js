// Blog API Integration
console.log('Blog.js is loading from the root directory...');
const API_BASE_URL = '/api';  // Use relative URL instead of hardcoded localhost
console.log('API Base URL:', API_BASE_URL);
console.log('Full URL for posts will be:', window.location.origin + API_BASE_URL + '/posts');

// Add debug logging
const DEBUG = true;
function logDebug(...args) {
    if (DEBUG) {
        console.log('[Blog Debug]', ...args);
    }
}

// Simple cache mechanism
const postCache = {
    data: {},
    invalidateAll() {
        console.log('Invalidating all cache');
        this.data = {};
    }
};

// Listen for blog updates from admin panel
document.addEventListener('blog-updated', async function(event) {
    logDebug('Received blog update event:', event.detail);
    
    // Invalidate cache
    postCache.invalidateAll();
    
    // Refresh blog content
    await renderBlogPosts();
    
    // Show notification
    const notification = document.createElement('div');
    notification.className = 'blog-update-notification';
    notification.innerHTML = `
        <i class="fas fa-sync"></i>
        Blog content updated!
    `;
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
});

// Add styles for notification
const style = document.createElement('style');
style.textContent = `
    .blog-update-notification {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #39ff14;
        color: #000;
        padding: 10px 20px;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        animation: slideIn 0.3s ease-out;
        z-index: 1000;
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Fetch all blog posts with caching
async function fetchBlogPosts() {
    try {
        logDebug('Fetching blog posts');
        // Check if we have cached data
        const cachedPosts = postCache.get('all_posts');
        if (cachedPosts) {
            logDebug('Using cached posts');
            return cachedPosts;
        }
        
        // Add a cache busting parameter to prevent browser caching
        const cacheBuster = `?_=${Date.now()}`;
        logDebug('Making network request for posts');
        
        // No cache or expired, make a new request
        const response = await fetch(`${API_BASE_URL}/posts${cacheBuster}`, {
            // Add cache busting query parameter
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            cache: 'no-store'
        });
        
        logDebug('Response received:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch posts: ${response.status} ${response.statusText}`);
        }
        
        const posts = await response.json();
        logDebug('Posts fetched successfully:', posts.length);
        
        // Store in cache
        postCache.set('all_posts', posts);
        
        return posts;
    } catch (error) {
        console.error('Error fetching blog posts:', error);
        return [];
    }
}

// Fetch a single blog post by slug with caching
async function fetchBlogPost(slug) {
    try {
        logDebug('Fetching blog post:', slug);
        // Check if we have cached data
        const cacheKey = `post_${slug}`;
        const cachedPost = postCache.get(cacheKey);
        if (cachedPost) {
            logDebug('Using cached post for:', slug);
            return cachedPost;
        }
        
        // Add a cache busting parameter to prevent browser caching
        const cacheBuster = `?_=${Date.now()}`;
        logDebug('Making network request for post:', slug);
        
        // No cache or expired, make a new request
        const response = await fetch(`${API_BASE_URL}/posts/${slug}${cacheBuster}`, {
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            cache: 'no-store'
        });
        
        logDebug('Response received for post:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch post: ${response.status} ${response.statusText}`);
        }
        
        const post = await response.json();
        logDebug('Post fetched successfully:', post.title);
        
        // Store in cache
        postCache.set(cacheKey, post);
        
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

// Fetch posts by category with caching
async function fetchPostsByCategory(categorySlug) {
    try {
        logDebug('Fetching posts for category:', categorySlug);
        // Check if we have cached data
        const cacheKey = `category_${categorySlug}`;
        const cachedPosts = postCache.get(cacheKey);
        if (cachedPosts) {
            logDebug('Using cached posts for category:', categorySlug);
            return cachedPosts;
        }
        
        // Add a cache busting parameter to prevent browser caching
        const cacheBuster = `?_=${Date.now()}`;
        logDebug('Making network request for category posts:', categorySlug);
        
        // No cache or expired, make a new request
        const response = await fetch(`${API_BASE_URL}/categories/${categorySlug}/posts${cacheBuster}`, {
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            cache: 'no-store'
        });
        
        logDebug('Response received for category posts:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch posts for category: ${response.status} ${response.statusText}`);
        }
        
        const posts = await response.json();
        logDebug('Category posts fetched successfully:', posts.length);
        
        // Store in cache
        postCache.set(cacheKey, posts);
        
        return posts;
    } catch (error) {
        console.error(`Error fetching posts for category ${categorySlug}:`, error);
        return [];
    }
}

// Function to check for blog updates periodically
async function checkForUpdates() {
    try {
        logDebug('Checking for blog updates...');
        
        // Add cache buster to prevent browser caching
        const cacheBuster = `?_=${Date.now()}`;
        
        // Make a request to check for updates
        const response = await fetch(`${API_BASE_URL}/check-updates${cacheBuster}`, {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            cache: 'no-store'
        });
        
        logDebug('Update check response:', response.status, response.statusText);
        
        // Force refresh regardless of response
        // This makes development easier by always refreshing content
        postCache.invalidateAll();
        
        // Refresh the current view
        if (window.location.pathname.includes('blog-post.html')) {
            logDebug('Refreshing blog post');
            renderBlogPost();
        } else {
            logDebug('Refreshing blog listing');
            renderBlogPosts();
        }
        
        return true;
    } catch (error) {
        console.error('Error checking for updates:', error);
        return false;
    }
}

// Render blog posts in the blog section
async function renderBlogPosts() {
    console.log('Rendering blog posts...');
    
    // Try to find the blog grid
    const blogGrid = document.querySelector('.blog-grid');
    
    if (!blogGrid) {
        console.error('Blog grid not found with class .blog-grid');
        return;
    }
    
    try {
        // Show loading state
        blogGrid.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Loading blog posts...</div>';
        
        // Fetch posts from API
        const response = await fetch(`${API_BASE_URL}/posts`);
        console.log('API Response:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch posts: ${response.status} ${response.statusText}`);
        }
        
        const posts = await response.json();
        console.log('Fetched posts:', posts);
        
        // Clear existing content
        blogGrid.innerHTML = '';
        
        if (!posts || posts.length === 0) {
            blogGrid.innerHTML = `
                <div class="no-posts-message">
                    <i class="fas fa-newspaper"></i>
                    <p>No blog posts available yet.</p>
                    <p>Check back soon for new content!</p>
                </div>
            `;
            return;
        }
        
        // Render each post
        posts.forEach(post => {
            const article = document.createElement('article');
            article.className = 'blog-card';
            article.setAttribute('data-post-id', post.id);
            
            const categoryIcon = post.category ? post.category.icon || 'fa-folder' : 'fa-folder';
            const categoryName = post.category ? post.category.name : 'Uncategorized';
            const categorySlug = post.category ? post.category.slug : '';
            
            article.innerHTML = `
                <div class="blog-card-inner">
                    <div class="blog-image">
                        <div class="blog-category">
                            <i class="fas ${categoryIcon}"></i>
                            <span>${categoryName}</span>
                        </div>
                        <img src="${post.featured_image ? `/backend/static/uploads/${post.featured_image}` : 'assets/blog-placeholder.jpg'}" 
                             alt="${post.title}" 
                             loading="lazy"
                             onerror="this.src='assets/blog-placeholder.jpg'">
                        <div class="blog-overlay">
                            <div class="blog-meta">
                                <span><i class="far fa-calendar"></i> ${post.created_at}</span>
                                <span><i class="far fa-clock"></i> ${post.read_time} min read</span>
                            </div>
                        </div>
                    </div>
                    <div class="blog-content">
                        <h3>${post.title}</h3>
                        <p>${post.summary || 'No summary available.'}</p>
                        <div class="blog-footer">
                            <a href="/blog/${post.slug}" class="read-more">
                                Read Article
                                <i class="fas fa-arrow-right"></i>
                            </a>
                            <div class="blog-tags">
                                <span>#${categorySlug}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            blogGrid.appendChild(article);
        });
        
        console.log('Blog posts rendered successfully');
        
    } catch (error) {
        console.error('Error rendering blog posts:', error);
        blogGrid.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <p>Failed to load blog posts.</p>
                <p class="error-details">${error.message}</p>
            </div>
        `;
    }
}

// Render a single blog post
async function renderBlogPost() {
    console.log('Rendering single blog post...');
    
    const blogContent = document.querySelector('.blog-post-content');
    if (!blogContent) {
        console.error('Blog post content element not found!');
        return;
    }
    
    // Show loading state
    blogContent.innerHTML = '<p class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading blog post...</p>';
    
    // Get slug from URL
    const urlParams = new URLSearchParams(window.location.search);
    const slug = urlParams.get('slug');
    
    if (!slug) {
        blogContent.innerHTML = '<p class="text-center">Blog post not found. No slug parameter in URL.</p>';
        return;
    }
    
    try {
        // Force clear any cached data
        postCache.invalidateAll();
        
        // Get completely fresh post with timestamp to avoid any caching
        const cacheBuster = Date.now();
        logDebug(`Fetching fresh post with slug ${slug} and cache buster: ${cacheBuster}`);
        
        const response = await fetch(`${API_BASE_URL}/posts/${slug}?_=${cacheBuster}`, {
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            cache: 'no-store'
        });
        
        if (!response.ok) {
            throw new Error(`Failed to fetch post: ${response.status} ${response.statusText}`);
        }
        
        const post = await response.json();
        logDebug(`Post "${post.title}" fetched successfully`);
        
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
                <img src="${post.featured_image ? `/backend/static/uploads/${post.featured_image}` : 'assets/blog-placeholder.jpg'}" alt="${post.title}" loading="lazy">
            </div>
            
            <div class="blog-post-body">
                ${contentHtml}
            </div>
            
            <div class="blog-post-author">
                <p>Written by <strong>${post.author}</strong></p>
            </div>
        `;
        
        blogContent.innerHTML = postHtml;
        logDebug('Blog post rendered successfully');
    } catch (error) {
        console.error(`Error rendering blog post ${slug}:`, error);
        blogContent.innerHTML = `<p class="text-center text-danger">Error loading blog post: ${error.message}</p>`;
    }
}

// Update sidebar categories
async function updateSidebarCategories() {
    const categoriesList = document.querySelector('.sidebar-categories');
    if (!categoriesList) return;
    
    try {
        // Add cache buster for fresh content
        const cacheBuster = `?_=${Date.now()}`;
        logDebug('Fetching categories');
        
        const response = await fetch(`${API_BASE_URL}/categories${cacheBuster}`, {
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            cache: 'no-store'
        });
        
        if (!response.ok) {
            throw new Error(`Failed to fetch categories: ${response.status}`);
        }
        
        const categories = await response.json();
        logDebug('Categories fetched:', categories.length);
        
        if (categories.length > 0) {
            let categoriesHTML = '';
            categories.forEach(category => {
                categoriesHTML += `
                    <li>
                        <a href="blog.html?category=${category.slug}" class="sidebar-link">
                            <i class="fas fa-${category.icon || 'folder'}"></i>
                            <span>${category.name}</span>
                            <i class="fas fa-chevron-right nav-arrow"></i>
                        </a>
                    </li>
                `;
            });
            categoriesList.innerHTML = categoriesHTML;
        }
    } catch (error) {
        console.error('Error fetching categories:', error);
    }
}

// Force refresh blog content right now
function forceRefreshBlog() {
    logDebug('Forcing blog refresh with aggressive cache clearing');
    
    // Use our more aggressive cache invalidation
    forceHardRefresh();
}

// Function to perform a hard refresh that forces browser cache reload
function forceHardRefresh() {
    logDebug('Performing hard refresh to bypass all caches...');
    
    // Update cache time to 0 to force expiration
    postCache.cacheTime = 0;
    
    // Clear all caches
    postCache.invalidateAll();
    
    // Force a complete page reload bypassing cache
    window.location.reload(true);
}

// Add this function to force clear all caches on a regular basis
function setupRegularCacheInvalidation() {
    // Check for updates every 5 seconds during development
    setInterval(() => {
        logDebug('Regular cache invalidation check');
        postCache.invalidateAll();
        
        // If we're on the blog page, refresh the content
        if (window.location.pathname.includes('blog') || 
            document.querySelector('.blog-grid') || 
            document.querySelector('#blog')) {
            logDebug('Refreshing blog content automatically');
            renderBlogPosts();
        }
    }, 5000);
}

// Try to load blog posts immediately when the script is loaded
// This helps avoid the hardcoded content being visible to users
console.log('Setting up immediate blog render before DOMContentLoaded');
// Use a short timeout to ensure the DOM has loaded the blog section
setTimeout(() => {
    console.log('Executing immediate blog render');
    renderBlogPosts();
}, 500);

// Initialize blog functionality with aggressive cache busting
document.addEventListener('DOMContentLoaded', function() {
    logDebug('Blog.js initialized with aggressive cache control');
    
    // Invalidate cache when page loads
    postCache.invalidateAll();
    
    // Render blog posts on the home page with a delay to ensure DOM is ready
    setTimeout(() => {
        renderBlogPosts();
    }, 100);
    
    // Setup regular cache invalidation
    setupRegularCacheInvalidation();
    
    // Render single blog post on the blog post page
    if (window.location.pathname.includes('blog-post.html')) {
        renderBlogPost();
    }
    
    // Update sidebar categories
    updateSidebarCategories();
    
    // Listen for visibility change to refresh content when user returns to the tab
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            logDebug('Tab became visible, refreshing content');
            // User has returned to the tab, invalidate cache and refresh
            forceRefreshBlog();
        }
    });
    
    // Add a more prominent debug button for testing
    if (DEBUG) {
        const debugButton = document.createElement('button');
        debugButton.textContent = '🔄 Force Hard Refresh';
        debugButton.style.position = 'fixed';
        debugButton.style.bottom = '10px';
        debugButton.style.right = '10px';
        debugButton.style.zIndex = '9999';
        debugButton.style.background = '#ff3838';
        debugButton.style.color = '#fff';
        debugButton.style.border = 'none';
        debugButton.style.borderRadius = '4px';
        debugButton.style.padding = '8px 12px';
        debugButton.style.cursor = 'pointer';
        debugButton.style.fontWeight = 'bold';
        
        debugButton.onclick = forceHardRefresh;
        
        document.body.appendChild(debugButton);
    }
});

// Add styles for loading and error states
const style = document.createElement('style');
style.textContent = `
    .loading-spinner {
        text-align: center;
        padding: 40px;
        color: #39ff14;
        font-size: 1.2em;
    }
    
    .no-posts-message {
        text-align: center;
        padding: 40px;
        color: #666;
    }
    
    .no-posts-message i {
        font-size: 3em;
        color: #39ff14;
        margin-bottom: 20px;
    }
    
    .error-message {
        text-align: center;
        padding: 40px;
        color: #ff3838;
    }
    
    .error-message i {
        font-size: 3em;
        margin-bottom: 20px;
    }
    
    .error-details {
        font-size: 0.9em;
        color: #666;
    }
`;
document.head.appendChild(style);