// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Active navigation link highlighting
const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('.nav-links a');

window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.pageYOffset >= sectionTop - 150) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href').slice(1) === current) {
            link.classList.add('active');
        }
    });
});

// Animate elements on scroll
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.project-card, .highlight-box, .section-icon');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementBottom = element.getBoundingClientRect().bottom;
        
        if (elementTop < window.innerHeight - 100 && elementBottom > 0) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
};

// Initial setup for scroll animations
document.addEventListener('DOMContentLoaded', () => {
    const elementsToAnimate = document.querySelectorAll('.project-card, .highlight-box, .section-icon');
    elementsToAnimate.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });
    
    // Animate name and logo
    const name = document.querySelector('.name');
    const logo = document.querySelector('.hero-logo');
    
    if (name) {
        name.style.opacity = '0';
        name.style.transform = 'translateY(20px)';
        setTimeout(() => {
            name.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            name.style.opacity = '1';
            name.style.transform = 'translateY(0)';
        }, 300);
    }
    
    if (logo) {
        logo.style.opacity = '0';
        logo.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            logo.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            logo.style.opacity = '1';
            logo.style.transform = 'translateY(0)';
        }, 100);
    }
    
    // Start scroll animations
    animateOnScroll();
});

// Update animations on scroll
window.addEventListener('scroll', animateOnScroll);

// Parallax effect for background
window.addEventListener('mousemove', (e) => {
    const mouseX = e.clientX / window.innerWidth;
    const mouseY = e.clientY / window.innerHeight;
    
    document.querySelector('.background-animation').style.transform = 
        `translate(${mouseX * 20}px, ${mouseY * 20}px)`;
});

// Sidebar functionality
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');

    // Function to open sidebar
    function openSidebar() {
        sidebar.classList.add('active');
        sidebarOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    // Function to close sidebar
    function closeSidebar() {
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Mobile menu button click
    mobileMenuBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        openSidebar();
    });

    // Close sidebar when clicking overlay
    sidebarOverlay.addEventListener('click', closeSidebar);

    // Close sidebar when clicking a link (mobile)
    document.querySelectorAll('.sidebar a').forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                closeSidebar();
            }
        });
    });

    // Handle touch events for swipe
    let touchStartX = 0;
    let touchEndX = 0;

    document.addEventListener('touchstart', function(e) {
        touchStartX = e.touches[0].clientX;
    }, false);

    document.addEventListener('touchmove', function(e) {
        touchEndX = e.touches[0].clientX;
    }, false);

    document.addEventListener('touchend', function() {
        const swipeThreshold = 50;
        const swipeDistance = touchEndX - touchStartX;
        
        // Swipe right to open
        if (swipeDistance > swipeThreshold && touchStartX < 50) {
            openSidebar();
        }
        
        // Swipe left to close
        if (swipeDistance < -swipeThreshold && sidebar.classList.contains('active')) {
            closeSidebar();
        }
    }, false);

    // Close sidebar when pressing Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            closeSidebar();
        }
    });
});

// Category Navigation
const categories = document.querySelectorAll('.sidebar-section:nth-child(2) ul li a');
const prevButton = document.getElementById('prevCategory');
const nextButton = document.getElementById('nextCategory');
let currentCategoryIndex = 0;

// Initialize navigation state
function updateNavigationState() {
    // Remove active class from all categories
    categories.forEach(category => category.classList.remove('active'));
    
    // Add active class to current category
    categories[currentCategoryIndex].classList.add('active');
    
    // Update button states
    prevButton.classList.toggle('disabled', currentCategoryIndex === 0);
    nextButton.classList.toggle('disabled', currentCategoryIndex === categories.length - 1);
}

// Navigate to previous category
prevButton.addEventListener('click', () => {
    if (currentCategoryIndex > 0) {
        currentCategoryIndex--;
        updateNavigationState();
        
        // Smooth scroll to the category if needed
        categories[currentCategoryIndex].scrollIntoView({ behavior: 'smooth' });
    }
});

// Navigate to next category
nextButton.addEventListener('click', () => {
    if (currentCategoryIndex < categories.length - 1) {
        currentCategoryIndex++;
        updateNavigationState();
        
        // Smooth scroll to the category if needed
        categories[currentCategoryIndex].scrollIntoView({ behavior: 'smooth' });
    }
});

// Add click handlers for categories
categories.forEach((category, index) => {
    category.addEventListener('click', (e) => {
        e.preventDefault();
        currentCategoryIndex = index;
        updateNavigationState();
    });
});

// Initialize navigation state
updateNavigationState();

// Add hover animation for category indicators
categories.forEach(category => {
    category.addEventListener('mouseenter', () => {
        const indicator = category.querySelector('.category-indicator');
        indicator.style.transform = 'scaleX(1)';
    });
    
    category.addEventListener('mouseleave', () => {
        const indicator = category.querySelector('.category-indicator');
        if (!category.classList.contains('active')) {
            indicator.style.transform = 'scaleX(0)';
        }
    });
});

// Scroll Indicators
const scrollIndicator = document.querySelector('.scroll-indicator');
const scrollArrows = document.querySelector('.scroll-arrows');
const scrollDots = document.querySelectorAll('.scroll-dot');

// Show/hide scroll indicators based on scroll position
function updateScrollIndicators() {
    const scrollPosition = window.scrollY;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    
    // Show/hide main scroll indicators
    if (scrollPosition > 100) {
        scrollIndicator.classList.add('visible');
    } else {
        scrollIndicator.classList.remove('visible');
    }
    
    // Show/hide scroll arrows
    if (scrollPosition < 100) {
        scrollArrows.classList.add('visible');
    } else {
        scrollArrows.classList.remove('visible');
    }
    
    // Update active dot based on current section
    sections.forEach((section, index) => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        
        if (scrollPosition >= sectionTop - windowHeight/2 && 
            scrollPosition < sectionTop + sectionHeight - windowHeight/2) {
            scrollDots.forEach(dot => dot.classList.remove('active'));
            scrollDots[index].classList.add('active');
        }
    });
    
    // Keep indicators visible at the last section
    const lastSectionTop = sections[sections.length - 1].offsetTop;
    const lastSectionHeight = sections[sections.length - 1].clientHeight;
    const isLastSection = scrollPosition >= lastSectionTop - windowHeight/2;
    
    if (isLastSection) {
        scrollIndicator.style.opacity = '1';
        // Only hide arrows at last section
        scrollArrows.style.opacity = '0';
    }
}

// Add click handlers for scroll dots
scrollDots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
        sections[index].scrollIntoView({ behavior: 'smooth' });
    });
});

// Scroll arrow click handler
scrollArrows.addEventListener('click', () => {
    if (sections[1]) {
        sections[1].scrollIntoView({ behavior: 'smooth' });
    }
});

// Update indicators on scroll
window.addEventListener('scroll', updateScrollIndicators);
window.addEventListener('resize', updateScrollIndicators);

// Initialize indicators
document.addEventListener('DOMContentLoaded', () => {
    updateScrollIndicators();
    
    // Add intersection observer for section indicators
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const indicator = entry.target.querySelector('.section-indicator');
            if (indicator) {
                if (entry.isIntersecting) {
                    indicator.style.opacity = '1';
                    setTimeout(() => {
                        indicator.style.opacity = '0';
                    }, 2000);
                }
            }
        });
    }, {
        threshold: 0.5
    });
    
    sections.forEach(section => {
        sectionObserver.observe(section);
    });
});

// Create matrix rain effect
function createMatrixRain() {
    const matrixContainer = document.querySelector('.matrix-rain');
    if (!matrixContainer) return;

    const numberOfDrops = 20;
    
    for (let i = 0; i < numberOfDrops; i++) {
        const drop = document.createElement('div');
        drop.className = 'matrix-drop';
        drop.style.left = `${Math.random() * 100}%`;
        drop.style.animationDelay = `${Math.random() * 2}s`;
        drop.style.height = `${Math.random() * 30 + 10}px`;
        matrixContainer.appendChild(drop);
    }
}

// Initialize matrix rain
createMatrixRain();

// Logo hover effect
document.addEventListener('DOMContentLoaded', () => {
    const logoContainer = document.querySelector('.hero-logo-container');
    const logo = document.querySelector('.hero-logo');
    
    if (logoContainer && logo) {
        logoContainer.addEventListener('mousemove', (e) => {
            const rect = logoContainer.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;
            
            // Set CSS variables for the gradient effect
            logoContainer.style.setProperty('--mouse-x', `${x}%`);
            logoContainer.style.setProperty('--mouse-y', `${y}%`);
            
            // Calculate 3D rotation based on mouse position
            const rotateY = 20 * ((x / 100) - 0.5);
            const rotateX = -20 * ((y / 100) - 0.5);
            
            // Apply 3D transform to logo
            logo.style.transform = `perspective(1000px) rotateY(${rotateY}deg) rotateX(${rotateX}deg) translateZ(20px)`;
        });

        logoContainer.addEventListener('mouseleave', () => {
            // Reset CSS variables
            logoContainer.style.setProperty('--mouse-x', '50%');
            logoContainer.style.setProperty('--mouse-y', '50%');
            
            // Reset logo transform
            logo.style.transform = 'perspective(1000px) rotateY(0deg) rotateX(0deg) translateZ(0)';
        });
    }
});

// Blog Article Reading Functionality
function readArticle(articleId, event) {
    event.preventDefault();
    
    // Get the article data
    const article = document.querySelector(`[data-article-id="${articleId}"]`);
    const title = article.querySelector('h3').textContent;
    const category = article.querySelector('.blog-category span').textContent;
    const date = article.querySelector('.blog-meta span:first-child').textContent;
    const readTime = article.querySelector('.blog-meta span:last-child').textContent;
    const description = article.querySelector('p').textContent;
    const tags = Array.from(article.querySelectorAll('.blog-tags span')).map(tag => tag.textContent);
    
    // Create modal content with full-screen design
    const modal = document.createElement('div');
    modal.className = 'article-modal fullscreen';
    modal.innerHTML = `
        <div class="article-modal-content fullscreen">
            <div class="article-modal-header">
                <div class="modal-nav">
                    <button class="back-to-blog" onclick="closeArticle(event)">
                        <i class="fas fa-arrow-left"></i>
                        Back to Blog
                    </button>
                    <div class="modal-actions">
                        <button class="theme-toggle" onclick="toggleReadingMode(event)">
                            <i class="fas fa-moon"></i>
                        </button>
                        <button class="share-btn" onclick="shareArticle('${encodeURIComponent(title)}')">
                            <i class="fas fa-share-alt"></i>
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="article-content-wrapper">
                <div class="article-header">
                    <div class="article-meta-top">
                        <div class="article-category">
                            <i class="fas fa-${getCategoryIcon(category)}"></i>
                            <span>${category}</span>
                        </div>
                        <div class="article-info">
                            <span><i class="far fa-calendar"></i> ${date}</span>
                            <span><i class="far fa-clock"></i> ${readTime}</span>
                        </div>
                    </div>
                    <h1>${title}</h1>
                    <div class="article-tags">
                        ${tags.map(tag => `<span>${tag}</span>`).join('')}
                    </div>
                </div>

                <div class="article-featured-image">
                    <img src="assets/blog${articleId}.jpg" alt="${title}" onerror="this.src='assets/placeholder.jpg'">
                </div>

                <div class="article-body">
                    <div class="article-lead">
                        ${description}
                    </div>
                    <div class="article-full-content">
                        <h2>Introduction</h2>
                        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
                        
                        <h2>Main Content</h2>
                        <p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
                        
                        <blockquote>
                            "Technology is best when it brings people together." - Matt Mullenweg
                        </blockquote>
                        
                        <h2>Conclusion</h2>
                        <p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.</p>
                    </div>
                </div>

                <div class="article-footer">
                    <div class="article-share">
                        <h3>Share this article</h3>
                        <div class="share-buttons">
                            <button onclick="shareArticle('${encodeURIComponent(title)}', 'twitter')">
                                <i class="fab fa-twitter"></i> Twitter
                            </button>
                            <button onclick="shareArticle('${encodeURIComponent(title)}', 'linkedin')">
                                <i class="fab fa-linkedin"></i> LinkedIn
                            </button>
                            <button onclick="shareArticle('${encodeURIComponent(title)}', 'copy')">
                                <i class="fas fa-link"></i> Copy Link
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.appendChild(modal);
    
    // Prevent body scrolling
    document.body.style.overflow = 'hidden';
    
    // Add keyboard navigation
    document.addEventListener('keydown', handleArticleKeyPress);
    
    // Animate modal entrance
    requestAnimationFrame(() => {
        modal.classList.add('active');
    });
}

// Close article modal
function closeArticle(event) {
    if (event) {
        event.preventDefault();
    }
    const modal = document.querySelector('.article-modal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => {
            document.body.removeChild(modal);
            document.body.style.overflow = '';
        }, 300);
    }
    // Remove keyboard listener
    document.removeEventListener('keydown', handleArticleKeyPress);
}

// Handle keyboard navigation
function handleArticleKeyPress(event) {
    if (event.key === 'Escape') {
        closeArticle();
    }
}

// Toggle reading mode (light/dark)
function toggleReadingMode(event) {
    event.preventDefault();
    const modal = document.querySelector('.article-modal');
    modal.classList.toggle('light-mode');
    const icon = event.currentTarget.querySelector('i');
    if (modal.classList.contains('light-mode')) {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
    }
}

// Enhanced share functionality
function shareArticle(title, platform = 'copy') {
    const url = window.location.href;
    const text = `Check out this article: ${title}`;
    
    switch (platform) {
        case 'twitter':
            window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, '_blank');
            break;
        case 'linkedin':
            window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`, '_blank');
            break;
        case 'copy':
        default:
            navigator.clipboard.writeText(url).then(() => {
                const button = document.querySelector('.share-btn');
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(() => {
                    button.innerHTML = originalText;
                }, 2000);
            });
            break;
    }
}

// Helper function to get category icon
function getCategoryIcon(category) {
    const icons = {
        'Web Development': 'code',
        'UI/UX Design': 'paint-brush',
        'Innovation': 'lightbulb'
    };
    return icons[category] || 'article';
}

// Handle admin controls visibility
document.addEventListener('DOMContentLoaded', function() {
    // Check if authStatus exists and user is specifically the admin user
    if (window.authStatus && 
        window.authStatus.is_admin === true && 
        window.authStatus.username === 'admin') {
        // Show admin controls for all blog posts
        document.querySelectorAll('.admin-controls').forEach(controls => {
            controls.style.display = 'block';
        });
    } else {
        // Hide admin controls for all other users
        document.querySelectorAll('.admin-controls').forEach(controls => {
            controls.style.display = 'none';
        });
    }
});

// Configure API URL based on environment
const API_BASE_URL = 'https://web-production-b4b2.up.railway.app';

// Login function
async function handleLogin(event) {
    if (event && event.preventDefault) {
        event.preventDefault();
    }
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Store auth info
            localStorage.setItem('authUser', JSON.stringify(data.user));
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            // Show error message
            alert(data.message || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Login failed. Please try again.');
    }
}

// Initialize login form
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('form[action="/login"]');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});

// Example of how to fetch data
async function fetchPosts() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/posts`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching posts:', error);
    return [];
  }
}

function toggleProjectDetails() {
    const detailsSection = document.querySelector('.project-details');
    const knowMoreBtn = document.querySelector('.project-btn.know-more');
    
    if (detailsSection.style.display === 'none') {
        detailsSection.style.display = 'block';
        knowMoreBtn.innerHTML = '<i class="fas fa-chevron-up"></i> Show Less';
    } else {
        detailsSection.style.display = 'none';
        knowMoreBtn.innerHTML = '<i class="fas fa-info-circle"></i> Know More';
    }
}

function expandImage(element) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('expandedImage');
    const img = element.querySelector('img');
    
    modal.style.display = 'block';
    modalImg.src = img.src;
    modalImg.style.width = 'auto';
    modalImg.style.height = 'auto';

    // Center the image after it loads
    modalImg.onload = function() {
        const windowAspect = window.innerWidth / window.innerHeight;
        const imageAspect = this.naturalWidth / this.naturalHeight;

        if (this.naturalWidth > window.innerWidth * 0.9 || this.naturalHeight > window.innerHeight * 0.9) {
            if (windowAspect > imageAspect) {
                this.style.height = '90vh';
                this.style.width = 'auto';
            } else {
                this.style.width = '90vw';
                this.style.height = 'auto';
            }
        } else {
            this.style.width = this.naturalWidth + 'px';
            this.style.height = this.naturalHeight + 'px';
        }
    };

    // Close modal when clicking outside the image or on close button
    modal.onclick = function(e) {
        if (e.target === modal || e.target.className === 'close-modal-btn') {
            modal.style.display = 'none';
        }
    };
}

// Mobile menu functionality
document.querySelector('.mobile-menu-btn').addEventListener('click', function() {
    document.querySelector('.sidebar').classList.toggle('active');
});

// Close sidebar when clicking outside
document.addEventListener('click', function(e) {
    const sidebar = document.querySelector('.sidebar');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    
    if (!sidebar.contains(e.target) && !mobileMenuBtn.contains(e.target) && sidebar.classList.contains('active')) {
        sidebar.classList.remove('active');
    }
});

// Close sidebar when clicking a link (mobile)
document.querySelectorAll('.sidebar a').forEach(link => {
    link.addEventListener('click', function() {
        if (window.innerWidth <= 768) {
            document.querySelector('.sidebar').classList.remove('active');
        }
    });
});

// Samsung S24 Touch Optimizations
document.addEventListener('DOMContentLoaded', function() {
    // Check if device is Samsung S24 or similar high-end Android
    const isHighEndAndroid = /Android.*Chrome\/[.0-9]*/.test(navigator.userAgent) && 
                            window.devicePixelRatio >= 3;

    if (isHighEndAndroid) {
        // Enable smooth scrolling with touch momentum
        document.documentElement.style.scrollBehavior = 'smooth';
        
        // Optimize touch response
        document.body.style.touchAction = 'manipulation';
        
        // Add haptic feedback for buttons
        const buttons = document.querySelectorAll('.project-btn, .mobile-menu-btn, .social-btn');
        buttons.forEach(button => {
            button.addEventListener('touchstart', function() {
                if (navigator.vibrate) {
                    navigator.vibrate(1);
                }
            });
        });

        // Enhanced bottom sheet behavior
        const detailsSection = document.querySelector('.project-details');
        if (detailsSection) {
            let startY = 0;
            let currentY = 0;
            let initialScroll = 0;
            let isScrolling = false;

            detailsSection.addEventListener('touchstart', function(e) {
                startY = e.touches[0].clientY;
                currentY = startY;
                initialScroll = this.scrollTop;
                isScrolling = false;
            }, { passive: true });

            detailsSection.addEventListener('touchmove', function(e) {
                if (!detailsSection.classList.contains('active')) return;
                
                const touch = e.touches[0];
                const diff = touch.clientY - startY;
                
                // Check if user is scrolling content or trying to dismiss
                if (!isScrolling) {
                    isScrolling = Math.abs(diff) > 5;
                }
                
                if (diff > 0 && this.scrollTop <= 0) {
                    e.preventDefault();
                    currentY = touch.clientY;
                    const transform = Math.min(diff * 0.5, 200);
                    this.style.transform = `translateY(${transform}px)`;
                    this.style.transition = 'none';
                }
            }, { passive: false });

            detailsSection.addEventListener('touchend', function() {
                if (!detailsSection.classList.contains('active')) return;
                
                const diff = currentY - startY;
                this.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                
                if (diff > 100 && !isScrolling) {
                    this.style.transform = 'translateY(100%)';
                    setTimeout(() => {
                        toggleProjectDetails();
                        this.style.transform = '';
                    }, 300);
                } else {
                    this.style.transform = '';
                }
            });
        }

        // Enhanced image gallery interactions
        const gallery = document.querySelector('.preview-gallery');
        if (gallery) {
            let touchStartX = 0;
            let touchStartY = 0;
            let currentScale = 1;
            let initialDistance = 0;

            gallery.addEventListener('touchstart', function(e) {
                if (e.touches.length === 2) {
                    initialDistance = Math.hypot(
                        e.touches[0].pageX - e.touches[1].pageX,
                        e.touches[0].pageY - e.touches[1].pageY
                    );
                }
            }, { passive: true });

            gallery.addEventListener('touchmove', function(e) {
                if (e.touches.length === 2) {
                    const distance = Math.hypot(
                        e.touches[0].pageX - e.touches[1].pageX,
                        e.touches[0].pageY - e.touches[1].pageY
                    );
                    currentScale = Math.min(Math.max(distance / initialDistance, 0.5), 2);
                    e.target.style.transform = `scale(${currentScale})`;
                }
            }, { passive: true });

            gallery.addEventListener('touchend', function(e) {
                if (e.target.tagName === 'IMG') {
                    e.target.style.transform = '';
                    currentScale = 1;
                }
            });
        }
    }
}); 