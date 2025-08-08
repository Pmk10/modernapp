// static/js/app.js - Flask-Enhanced JavaScript Application

/**
 * Flask Blog Application JavaScript
 * Combines original frontend features with Flask backend integration
 * Demonstrates AJAX, theme switching, and modern JavaScript patterns
 */

// Main Blog Application Class (Enhanced for Flask)
class FlaskBlogApp {
    constructor() {
        // Theme management
        this.theme = localStorage.getItem('theme') || 'light';
        
        // Flask CSRF token (if available)
        this.csrfToken = document.querySelector('meta[name=csrf-token]')?.getAttribute('content');
        
        // State management
        this.currentPage = 1;
        this.currentFilter = 'all';
        this.searchQuery = '';
        this.isLoading = false;
        
        // Bind methods
        this.toggleTheme = this.toggleTheme.bind(this);
        this.handleSearch = this.handleSearch.bind(this);
        this.handleFilter = this.handleFilter.bind(this);
        this.loadMorePosts = this.loadMorePosts.bind(this);
        this.submitComment = this.submitComment.bind(this);
    }

    // Initialize the application
    init() {
        console.log('🚀 Initializing Flask Blog App...');
        
        // Theme setup
        this.initializeTheme();
        
        // Event listeners
        this.setupEventListeners();
        
        // Form enhancements
        this.enhanceForms();
        
        // AJAX setup
        this.setupAjax();
        
        // Animation effects
        this.setupAnimations();
        
        console.log('✅ Flask Blog App initialized successfully!');
        
        // Show initialization toast
        this.showToast('Welcome to ModernBlog! 🎉', 'success');
    }

    // Theme Management
    initializeTheme() {
        this.setTheme(this.theme);
        
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', this.toggleTheme);
        }
    }

    toggleTheme() {
        const newTheme = this.theme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
        this.showToast(`Switched to ${newTheme} theme`, 'info');
    }

    setTheme(theme) {
        this.theme = theme;
        document.documentElement.setAttribute('data-color-scheme', theme);
        localStorage.setItem('theme', theme);
        
        // Update theme toggle icon
        const themeIcon = document.querySelector('#themeToggle i');
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'bi bi-moon-fill' : 'bi bi-sun-fill';
        }
        
        console.log(`Theme set to: ${theme}`);
    }

    // Event Listeners Setup
    setupEventListeners() {
        console.log('Setting up event listeners...');
        
        // Search functionality
        const searchForm = document.getElementById('search-form');
        const searchInput = document.getElementById('search-input');
        
        if (searchForm) {
            searchForm.addEventListener('submit', this.handleSearch);
        }
        
        if (searchInput) {
            // Live search with debouncing
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    if (e.target.value.length >= 3) {
                        this.performSearch(e.target.value);
                    }
                }, 500);
            });
        }
        
        // Filter buttons
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(btn => {
            btn.addEventListener('click', this.handleFilter);
        });
        
        // Category and tag filters
        const categoryFilter = document.getElementById('category-filter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', (e) => {
                this.filterByCategory(e.target.value);
            });
        }
        
        const tagFilters = document.querySelectorAll('.tag-filter');
        tagFilters.forEach(button => {
            button.addEventListener('click', (e) => {
                this.filterByTag(e.target.dataset.tag);
            });
        });
        
        // Load more posts
        const loadMoreBtn = document.getElementById('load-more-btn');
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', this.loadMorePosts);
        }
        
        // Comment form
        const commentForm = document.getElementById('comment-form');
        if (commentForm) {
            commentForm.addEventListener('submit', this.submitComment);
        }
        
        console.log('Event listeners configured');
    }

    // Search Functionality
    handleSearch(e) {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        const searchTerm = searchInput?.value.trim();
        
        if (!searchTerm || searchTerm.length < 3) {
            this.showToast('Please enter at least 3 characters', 'warning');
            return;
        }
        
        this.performSearch(searchTerm);
    }

    async performSearch(searchTerm) {
        this.searchQuery = searchTerm;
        
        try {
            const response = await this.fetchWithCSRF('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ search: searchTerm })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displaySearchResults(data.results);
                this.showSearchModal();
                this.showToast(`Found ${data.results.length} results`, 'info');
            } else {
                this.showToast('Search failed. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showToast('Search failed. Please try again.', 'error');
        }
    }

    displaySearchResults(results) {
        const container = document.getElementById('search-results');
        if (!container) return;
        
        if (results.length === 0) {
            container.innerHTML = '<p class="text-center">No results found.</p>';
            return;
        }
        
        const resultsHtml = results.map(result => `
            <div class="search-result-item mb-3 p-3 border rounded">
                <h6>
                    <a href="${result.url}" class="text-decoration-none">
                        ${this.highlightSearchTerm(result.title, this.searchQuery)}
                    </a>
                </h6>
                <p class="text-muted mb-1">
                    ${this.highlightSearchTerm(result.excerpt, this.searchQuery)}
                </p>
                <small class="text-secondary">
                    Category: ${result.category} | Author: ${result.author} | ${result.date}
                </small>
            </div>
        `).join('');
        
        container.innerHTML = resultsHtml;
    }

    highlightSearchTerm(text, term) {
        if (!term) return text;
        const regex = new RegExp(`(${term})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    showSearchModal() {
        const searchModal = document.getElementById('searchModal');
        if (searchModal && window.bootstrap) {
            const modal = new bootstrap.Modal(searchModal);
            modal.show();
        }
    }

    // Filter Functionality
    handleFilter(e) {
        const filterValue = e.target.dataset.filter;
        this.setActiveFilter(e.target);
        this.currentFilter = filterValue;
        this.filterPosts();
    }

    setActiveFilter(activeButton) {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        activeButton.classList.add('active');
    }

    filterByCategory(categoryId) {
        this.loadFilteredPosts({ category_id: categoryId });
    }

    filterByTag(tag) {
        const button = event.target;
        button.classList.toggle('active');
        button.classList.toggle('btn-primary');
        button.classList.toggle('btn-outline-secondary');
        
        const activeTags = Array.from(document.querySelectorAll('.tag-filter.active'))
            .map(btn => btn.dataset.tag);
        
        this.loadFilteredPosts({ tag: activeTags.join(',') });
    }

async loadFilteredPosts(filters) {
  try {
    this.setLoadingState(true);
    
    // Build query string
    const params = new URLSearchParams(filters);
    const response = await fetch(`/api/posts?${params}`);
    const data = await response.json();
    
    if (data.success) {
      // Clear existing posts
      document.getElementById('posts-container').innerHTML = '';
      
      // Append new posts if any
      if (data.posts.length > 0) {
        this.displayPosts(data.posts, true);
      }
      
      // Always hide or show Load More button based solely on has_next
      const loadMoreBtn = document.getElementById('load-more-btn');
      loadMoreBtn.style.display = data.has_next ? 'block' : 'none';
      
    } else {
      // On API failure flag, just hide Load More—no error card
      document.getElementById('load-more-btn').style.display = 'none';
    }

  } catch (error) {
    console.error('Filter error:', error);
    // Hide Load More button on network errors
    document.getElementById('load-more-btn').style.display = 'none';
  } finally {
    this.setLoadingState(false);
  }
}


    // Load More Posts (AJAX Pagination)
    async loadMorePosts() {
        if (this.isLoading) return;
        
        this.currentPage++;
        
        try {
            this.setLoadingState(true);
            
            const response = await fetch(`/api/posts?page=${this.currentPage}&per_page=6`);
            const data = await response.json();
            
            if (data.success && data.posts.length > 0) {
                this.displayPosts(data.posts, false); // Append to existing posts
                this.updateLoadMoreButton(data.has_next);
                this.showToast(`Loaded ${data.posts.length} more posts`, 'info');
            } else {
                this.hideLoadMoreButton();
                this.showToast('No more posts to load', 'info');
            }
        } catch (error) {
            console.error('Load more error:', error);
            this.showToast('Failed to load more posts', 'error');
        } finally {
            this.setLoadingState(false);
        }
    }

    displayPosts(posts, replace = false) {
        const container = document.getElementById('posts-container');
        if (!container) return;
        
        if (replace) {
            container.innerHTML = '';
        }
        
        if (posts.length === 0 && replace) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="bi bi-search display-1 text-muted"></i>
                    <h4 class="text-muted mt-3">No posts found</h4>
                    <p class="text-muted">Try adjusting your filters.</p>
                </div>
            `;
            return;
        }
        
        posts.forEach(post => {
            const postElement = this.createPostCard(post);
            container.insertAdjacentHTML('beforeend', postElement);
        });
        
        // Add animation to new posts
        const newCards = container.querySelectorAll('.post-card:not(.animated)');
        newCards.forEach((card, index) => {
            card.classList.add('animated');
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    createPostCard(post) {
        const tagsHtml = post.tags.slice(0, 3).map(tag => 
            `<span class="badge bg-light text-dark me-1">${tag}</span>`
        ).join('');
        
        const featuredBadge = post.featured ? 
            '<span class="badge bg-warning text-dark">Featured</span>' : '';
        
        return `
            <div class="col-lg-4 col-md-6 mb-4 post-card" style="opacity: 0; transform: translateY(20px);">
                <div class="card h-100 blog-card">
                    <img src="https://via.placeholder.com/400x200/007bff/ffffff?text=${encodeURIComponent(post.category)}" 
                         class="card-img-top" alt="${post.title}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="badge bg-primary">${post.category}</span>
                            ${featuredBadge}
                        </div>
                        <h5 class="card-title">${post.title}</h5>
                        <p class="card-text">${post.excerpt}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="bi bi-person"></i> ${post.author}
                            </small>
                            <small class="text-muted">${post.read_time}</small>
                        </div>
                    </div>
                    <div class="card-footer bg-transparent">
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="tag-list">${tagsHtml}</div>
                            <a href="${post.url}" class="btn btn-outline-primary btn-sm">
                                Read More
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Comment System
    async submitComment(e) {
        e.preventDefault();
        
        const form = e.target;
        const content = document.getElementById('comment-content')?.value.trim();
        const postId = form.dataset.postId;
        
        if (!content) {
            this.showToast('Please enter a comment', 'warning');
            return;
        }
        
        try {
            this.setButtonLoading(form.querySelector('button[type="submit"]'), true);
            
            const response = await this.fetchWithCSRF('/api/comments', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    post_id: postId,
                    content: content
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addCommentToList(data.comment);
                form.reset();
                this.showToast('Comment posted successfully!', 'success');
            } else {
                this.showToast('Failed to post comment', 'error');
            }
        } catch (error) {
            console.error('Comment error:', error);
            this.showToast('Failed to post comment', 'error');
        } finally {
            this.setButtonLoading(form.querySelector('button[type="submit"]'), false);
        }
    }

    addCommentToList(comment) {
        const commentsList = document.getElementById('comments-list');
        if (!commentsList) return;
        
        const commentHtml = `
            <div class="comment mb-3 pb-3 border-bottom">
                <div class="d-flex">
                    <div class="me-3">
                        <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" 
                             style="width: 40px; height: 40px;">
                            ${comment.author[0].toUpperCase()}
                        </div>
                    </div>
                    <div>
                        <h6 class="mb-1">${comment.author}</h6>
                        <p class="mb-2">${comment.content}</p>
                        <small class="text-muted">${comment.date}</small>
                    </div>
                </div>
            </div>
        `;
        
        commentsList.insertAdjacentHTML('afterbegin', commentHtml);
        
        // Update comment count
        const countElement = document.querySelector('.card-header h5');
        if (countElement) {
            const currentCount = parseInt(countElement.textContent.match(/\d+/)[0]);
            countElement.innerHTML = `<i class="bi bi-chat-dots"></i> Comments (${currentCount + 1})`;
        }
    }

    // Form Enhancements
    enhanceForms() {
        // Auto-resize textareas
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
        });
        
        // Character counters
        document.querySelectorAll('[maxlength]').forEach(input => {
            const maxLength = parseInt(input.getAttribute('maxlength'));
            if (maxLength > 50) {
                this.addCharacterCounter(input, maxLength);
            }
        });
        
        // Form submission loading states
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn && !e.defaultPrevented) {
                    this.setButtonLoading(submitBtn, true);
                    
                    // Reset after 3 seconds as fallback
                    setTimeout(() => {
                        this.setButtonLoading(submitBtn, false);
                    }, 3000);
                }
            });
        });
    }

    addCharacterCounter(input, maxLength) {
        const counter = document.createElement('div');
        counter.className = 'form-text';
        input.parentNode.insertBefore(counter, input.nextSibling);
        
        const updateCounter = () => {
            const remaining = maxLength - input.value.length;
            counter.textContent = `${remaining} characters remaining`;
            
            // Color coding
            counter.className = 'form-text';
            if (remaining < 50) counter.className += ' text-warning';
            if (remaining < 10) counter.className += ' text-danger';
        };
        
        input.addEventListener('input', updateCounter);
        updateCounter(); // Initial count
    }

    // AJAX Setup with CSRF Protection
    setupAjax() {
        // Add CSRF token to all AJAX requests
        const token = document.querySelector('meta[name=csrf-token]');
        if (token) {
            this.csrfToken = token.getAttribute('content');
        }
    }

    async fetchWithCSRF(url, options = {}) {
        const headers = {
            ...options.headers,
        };
        
        if (this.csrfToken) {
            headers['X-CSRFToken'] = this.csrfToken;
        }
        
        return fetch(url, {
            ...options,
            headers,
            credentials: 'same-origin'
        });
    }

    // Animation Setup
    setupAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);
        
        // Observe all cards
        document.querySelectorAll('.card').forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(card);
        });
    }

    // Utility Methods
    setLoadingState(isLoading) {
        this.isLoading = isLoading;
        const loadMoreBtn = document.getElementById('load-more-btn');
        
        if (loadMoreBtn) {
            const spinner = loadMoreBtn.querySelector('.spinner-border');
            loadMoreBtn.disabled = isLoading;
            
            if (spinner) {
                spinner.classList.toggle('d-none', !isLoading);
            }
        }
    }

    setButtonLoading(button, isLoading) {
        if (!button) return;
        
        if (isLoading) {
            button.dataset.originalText = button.textContent;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
            button.disabled = true;
        } else {
            button.textContent = button.dataset.originalText || 'Submit';
            button.disabled = false;
        }
    }

    updateLoadMoreButton(hasNext) {
        const loadMoreBtn = document.getElementById('load-more-btn');
        if (loadMoreBtn) {
            loadMoreBtn.style.display = hasNext ? 'block' : 'none';
        }
    }

    hideLoadMoreButton() {
        const loadMoreBtn = document.getElementById('load-more-btn');
        if (loadMoreBtn) {
            loadMoreBtn.style.display = 'none';
        }
    }

    // Toast Notifications
    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '1050';
            document.body.appendChild(toastContainer);
        }
        
        const toastId = 'toast-' + Date.now();
        const iconMap = {
            success: 'bi-check-circle-fill text-success',
            error: 'bi-exclamation-circle-fill text-danger',
            warning: 'bi-exclamation-triangle-fill text-warning',
            info: 'bi-info-circle-fill text-info'
        };
        
        const toastHtml = `
            <div class="toast" id="${toastId}" role="alert">
                <div class="toast-header">
                    <i class="bi ${iconMap[type]} me-2"></i>
                    <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">${message}</div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        // Show toast using Bootstrap
        const toastElement = document.getElementById(toastId);
        if (window.bootstrap) {
            const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
            toast.show();
            
            // Remove toast element after it's hidden
            toastElement.addEventListener('hidden.bs.toast', () => {
                toastElement.remove();
            });
        }
    }

    // Social Sharing
    sharePost(platform, url, title, text) {
        const shareUrls = {
            twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`,
            facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
            linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`
        };
        
        const shareUrl = shareUrls[platform];
        if (shareUrl) {
            window.open(shareUrl, '_blank', 'width=600,height=400');
            this.showToast(`Sharing on ${platform}`, 'info');
        }
    }

    // Keyboard Shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for search focus
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.getElementById('search-input');
                if (searchInput) {
                    searchInput.focus();
                    this.showToast('Search focused (Ctrl+K)', 'info');
                }
            }
            
            // Ctrl/Cmd + T for theme toggle
            if ((e.ctrlKey || e.metaKey) && e.key === 't') {
                e.preventDefault();
                this.toggleTheme();
            }
            
            // ESC to close modals
            if (e.key === 'Escape') {
                const modals = document.querySelectorAll('.modal.show');
                modals.forEach(modal => {
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    if (modalInstance) modalInstance.hide();
                });
            }
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DOM loaded, initializing Flask Blog Application...');
    
    // Create global instance
    window.flaskBlogApp = new FlaskBlogApp();
    window.flaskBlogApp.init();
    
    // Setup keyboard shortcuts
    window.flaskBlogApp.setupKeyboardShortcuts();
    
    console.log('✅ Flask Blog Application fully loaded and ready!');
    console.log('💡 Features available:');
    console.log('   • Theme switching (Ctrl+T)');
    console.log('   • Search functionality (Ctrl+K)');
    console.log('   • AJAX post filtering and pagination');
    console.log('   • Real-time comment system');
    console.log('   • Toast notifications');
    console.log('   • Keyboard shortcuts');
    console.log('   • Responsive design with animations');
});

// Global utility functions for template usage
window.BlogUtils = {
    // Format date
    formatDate: (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    
    // Truncate text
    truncateText: (text, maxLength) => {
        if (text.length <= maxLength) return text;
        return text.substr(0, maxLength) + '...';
    },
    
    // Show toast (shorthand)
    showToast: (message, type = 'info') => {
        if (window.flaskBlogApp) {
            window.flaskBlogApp.showToast(message, type);
        }
    },
    
    // Share post (shorthand)
    sharePost: (platform) => {
        const url = window.location.href;
        const title = document.title;
        const text = document.querySelector('meta[name="description"]')?.content || '';
        
        if (window.flaskBlogApp) {
            window.flaskBlogApp.sharePost(platform, url, title, text);
        }
    }
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlaskBlogApp;
}