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
    console.log('Rendering blog posts with complete replacement...');
    
    // Try to find the blog grid
    const blogGrid = document.querySelector('.blog-grid');
    
    if (!blogGrid) {
        console.error('Blog grid not found with class .blog-grid');
        // Try adding an error message to the blog section
        const blogSection = document.querySelector('#blog');
        if (blogSection) {
            const errorDiv = document.createElement('div');
            errorDiv.style.color = 'red';
            errorDiv.style.padding = '20px';
            errorDiv.style.textAlign = 'center';
            errorDiv.textContent = 'ERROR: Blog grid not found. Check HTML structure.';
            blogSection.appendChild(errorDiv);
        }
        return;
    }
    
    // We found the primary .blog-grid element
    console.log('Found blog grid with class .blog-grid, clearing hardcoded content');
    
    try {
        // Show loading state
        blogGrid.innerHTML = '<p class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading blog posts...</p>';
        
        // Direct fetch with error handling
        console.log('Fetching posts from', `${API_BASE_URL}/posts?_=${Date.now()}`);
        
        const response = await fetch(`${API_BASE_URL}/posts?_=${Date.now()}`, {
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            cache: 'no-store'
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        
        const posts = await response.json();
        console.log('Posts received:', posts.length, posts);
        
        // Clear existing content
        blogGrid.innerHTML = '';
        
        if (!posts || posts.length === 0) {
            blogGrid.innerHTML = '<p class="text-center">No blog posts found. Create some in the admin panel.</p>';
            return;
        }
        
        // Display up to 3 posts
        const postsToShow = posts.slice(0, 3);
        
        postsToShow.forEach(post => {
            // Create a fresh element instead of using innerHTML for better performance
            const article = document.createElement('article');
            article.className = 'blog-card';
            
            article.innerHTML = `
                <div class="blog-card-inner">
                    <div class="blog-image">
                        <div class="blog-category">
                            <i class="fas fa-folder"></i>
                            <span>${post.category}</span>
                        </div>
                        <img src="${post.featured_image ? `/backend/static/uploads/${post.featured_image}` : 'assets/blog-placeholder.jpg'}" alt="${post.title}" loading="lazy">
                        <div class="blog-overlay">
                            <div class="blog-meta">
                                <span><i class="far fa-calendar"></i> ${post.created_at}</span>
                                <span><i class="far fa-clock"></i> ${post.read_time} min read</span>
                            </div>
                        </div>
                    </div>
                    <div class="blog-content">
                        <h3>${post.title}</h3>
                        <p>${post.summary}</p>
                        <div class="blog-footer">
                            <a href="blog-post.html?slug=${post.slug}" class="read-more">
                                Read Article
                                <i class="fas fa-arrow-right"></i>
                            </a>
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
            <div style="text-align: center; padding: 20px; color: #ff3838;">
                <p><strong>Error loading blog posts:</strong> ${error.message}</p>
                <p>Check console for more details</p>
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