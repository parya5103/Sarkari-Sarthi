// SarkariSarthi 2.0 - Main JavaScript File

/**
 * Escapes HTML characters in a string to prevent XSS.
 * @param {string} str - The string to escape.
 * @returns {string} The escaped string.
 */
function escapeHTML(str) {
    if (!str) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(str).replace(/[&<>"']/g, function(m) { return map[m]; });
}

/**
 * Sanitizes URLs to ensure they only use http/https protocols.
 * @param {string} url - The URL to sanitize.
 * @returns {string} The sanitized URL.
 */
function sanitizeURL(url) {
    if (!url) return '#';
    try {
        const parsed = new URL(url, window.location.href);
        if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
            return parsed.href;
        }
    } catch (e) {
        // Return original if valid relative path
        if (url.startsWith('/') || url.startsWith('./') || url.startsWith('../')) {
            return escapeHTML(url);
        }
    }
    return '#';
}

/**
 * Sanitizes HTML string using DOMParser to prevent XSS.
 * @param {string} htmlString - The HTML string to sanitize.
 * @returns {string} The sanitized HTML string.
 */
function sanitizeHTML(htmlString) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, 'text/html');

    const allowedTags = ['div', 'span', 'p', 'h3', 'h4', 'a', 'strong', 'em', 'br', 'ul', 'li'];
    const allowedAttributes = ['class', 'href', 'target', 'data-job-id', 'id'];

    function clean(node) {
        if (node.nodeType === Node.ELEMENT_NODE) {
            const tagName = node.tagName.toLowerCase();
            if (!allowedTags.includes(tagName)) {
                // Remove the node completely to prevent script execution
                node.parentNode.removeChild(node);
                return;
            }

            // Clean attributes
            const attrs = node.attributes;
            for (let i = attrs.length - 1; i >= 0; i--) {
                const attr = attrs[i];
                if (!allowedAttributes.includes(attr.name.toLowerCase())) {
                    node.removeAttribute(attr.name);
                } else if (attr.name.toLowerCase() === 'href') {
                    // Use the existing sanitizeURL for links
                    node.setAttribute('href', sanitizeURL(attr.value));
                }
            }

            // Recursively clean children
            const children = Array.from(node.childNodes);
            children.forEach(clean);
        }
    }

    const children = Array.from(doc.body.childNodes);
    children.forEach(clean);

    return doc.body.innerHTML;
}

// Global variables
let jobsData = [];
let filteredJobs = [];
let currentPage = 1;
const jobsPerPage = 12;
let isLoading = false;

// DOM Elements
const jobsGrid = document.getElementById('jobsGrid');
const loadingSpinner = document.getElementById('loadingSpinner');
const loadMoreBtn = document.getElementById('loadMoreBtn');
const jobSearch = document.getElementById('jobSearch');
const categoryFilter = document.getElementById('categoryFilter');
const sortFilter = document.getElementById('sortFilter');
const searchBtn = document.getElementById('searchBtn');
const themeToggle = document.getElementById('themeToggle');
const telegramBtn = document.getElementById('telegramBtn');
const footerTelegramBtn = document.getElementById('footerTelegramBtn');
const whatsappBtn = document.getElementById('whatsappBtn');
const footerWhatsappBtn = document.getElementById('footerWhatsappBtn');
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const jobModal = document.getElementById('jobModal');
const modalClose = document.getElementById('modalClose');
const modalClose2 = document.getElementById('modalClose2');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    setupEventListeners();
    loadTheme();
    loadJobs();
    animateCounters();
    setupIntersectionObserver();
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Search functionality
    searchBtn.addEventListener('click', handleSearch);
    jobSearch.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
    
    // Filter functionality
    categoryFilter.addEventListener('change', handleFilter);
    sortFilter.addEventListener('change', handleSort);
    
    // Load more functionality
    loadMoreBtn.addEventListener('click', loadMoreJobs);
    
    // Theme toggle
    themeToggle.addEventListener('click', toggleTheme);
    
    // Telegram buttons
    if (telegramBtn) {
        telegramBtn.addEventListener('click', openTelegramChannel);
    }
    if (footerTelegramBtn) {
        footerTelegramBtn.addEventListener('click', openTelegramChannel);
    }
    
    // WhatsApp buttons
    if (whatsappBtn) {
        whatsappBtn.addEventListener('click', openWhatsappChannel);
    }
    if (footerWhatsappBtn) {
        footerWhatsappBtn.addEventListener('click', openWhatsappChannel);
    }

    // Mobile menu toggle
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', toggleMobileMenu);
    }
    
    // Modal functionality
    if (modalClose) {
        modalClose.addEventListener('click', closeModal);
    }
    if (modalClose2) {
        modalClose2.addEventListener('click', closeModal);
    }
    
    // Close modal when clicking outside
    jobModal.addEventListener('click', function(e) {
        if (e.target === jobModal) {
            closeModal();
        }
    });
    
    // Category card clicks
    document.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('click', function() {
            const category = this.dataset.category;
            filterByCategory(category);
        });
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', handleKeyboardNavigation);
}

/**
 * Load jobs data (simulated for now)
 */
async function loadJobs() {
    try {
        showLoading(true);
        
        // Try to load from job manifest first
        const response = await fetch('jobs/job_manifest.json');
        if (response.ok) {
            const manifest = await response.json();
            jobsData = manifest.jobs || [];
        } else {
            // Fallback to sample data if manifest doesn't exist
            jobsData = generateSampleJobs();
        }
        
        filteredJobs = [...jobsData];
        renderJobs();
        updateJobCounts();
        
    } catch (error) {
        console.error('Error loading jobs:', error);
        // Use sample data as fallback
        jobsData = generateSampleJobs();
        filteredJobs = [...jobsData];
        renderJobs();
        updateJobCounts();
    } finally {
        showLoading(false);
    }
}

/**
 * Generate sample jobs for demonstration
 */
function generateSampleJobs() {
    const sampleJobs = [
        {
            id: 'sample1',
            title: 'SBI Clerk Recruitment 2024',
            source: 'State Bank of India',
            category: 'Banking',
            description: 'State Bank of India invites applications for the post of Junior Associate (Customer Support & Sales) in Clerical Cadre. This is a great opportunity for candidates looking to start their career in the banking sector.',
            url: 'https://sbi.co.in/careers',
            important_dates: {
                last_date: '15-02-2024',
                exam_date: '10-03-2024'
            },
            skills: ['Banking', 'Customer Service', 'Computer Skills'],
            pdf_link: null
        },
        {
            id: 'sample2',
            title: 'SSC CGL 2024 Notification',
            source: 'Staff Selection Commission',
            category: 'SSC',
            description: 'Staff Selection Commission has released notification for Combined Graduate Level Examination 2024. Various posts are available across different ministries and departments.',
            url: 'https://ssc.nic.in',
            important_dates: {
                last_date: '20-02-2024',
                exam_date: '15-04-2024'
            },
            skills: ['General Knowledge', 'Mathematics', 'English', 'Reasoning'],
            pdf_link: null
        },
        {
            id: 'sample3',
            title: 'Railway Group D Recruitment',
            source: 'Indian Railways',
            category: 'Railway',
            description: 'Railway Recruitment Board invites applications for Group D posts including Track Maintainer, Helper, Assistant Pointsman, and other technical posts.',
            url: 'https://indianrailways.gov.in',
            important_dates: {
                last_date: '25-02-2024'
            },
            skills: ['Technical Skills', 'Physical Fitness'],
            pdf_link: null
        },
        {
            id: 'sample4',
            title: 'UPSC Civil Services Preliminary Exam 2024',
            source: 'Union Public Service Commission',
            category: 'UPSC',
            description: 'UPSC has announced the Civil Services Preliminary Examination 2024 for recruitment to various Group A and Group B services.',
            url: 'https://upsc.gov.in',
            important_dates: {
                last_date: '28-02-2024',
                exam_date: '26-05-2024'
            },
            skills: ['General Studies', 'Current Affairs', 'Optional Subject'],
            pdf_link: null
        },
        {
            id: 'sample5',
            title: 'Delhi Police Constable Recruitment',
            source: 'Delhi Police',
            category: 'Police',
            description: 'Delhi Police invites applications for the post of Constable (Executive) Male and Female. Physical and written tests will be conducted.',
            url: 'https://delhipolice.nic.in',
            important_dates: {
                last_date: '18-02-2024'
            },
            skills: ['Physical Fitness', 'General Knowledge', 'Hindi', 'English'],
            pdf_link: null
        },
        {
            id: 'sample6',
            title: 'Indian Army Agniveer Recruitment',
            source: 'Indian Army',
            category: 'Defence',
            description: 'Indian Army is recruiting Agniveers for various technical and non-technical posts. This is under the Agnipath scheme.',
            url: 'https://joinindianarmy.nic.in',
            important_dates: {
                last_date: '22-02-2024'
            },
            skills: ['Physical Fitness', 'Technical Skills', 'Discipline'],
            pdf_link: null
        }
    ];
    
    return sampleJobs;
}

/**
 * Render jobs on the page
 */
function renderJobs() {
    if (!jobsGrid) return;
    
    const startIndex = (currentPage - 1) * jobsPerPage;
    const endIndex = startIndex + jobsPerPage;
    const jobsToShow = filteredJobs.slice(0, endIndex);
    
    if (currentPage === 1) {
        jobsGrid.innerHTML = '';
    }
    
    if (jobsToShow.length === 0) {
        jobsGrid.innerHTML = '<div class="no-jobs"><h3>No jobs found</h3><p>Try adjusting your search criteria.</p></div>';
        loadMoreBtn.style.display = 'none';
        return;
    }
    
    const jobsToRender = jobsToShow.slice(startIndex);
    
    // Optimization: Batch DOM insertions using DocumentFragment to prevent layout thrashing
    // Reduces render time by avoiding multiple reflows/repaints inside the loop
    const fragment = document.createDocumentFragment();
    jobsToRender.forEach(job => {
        const jobCard = createJobCard(job);
        fragment.appendChild(jobCard);
    });
    jobsGrid.appendChild(fragment);
    
    // Show/hide load more button
    if (endIndex >= filteredJobs.length) {
        loadMoreBtn.style.display = 'none';
    } else {
        loadMoreBtn.style.display = 'block';
    }
    
    // Add animation to new cards
    const newCards = jobsGrid.querySelectorAll('.job-card:not(.animated)');
    newCards.forEach((card, index) => {
        card.classList.add('animated');
        setTimeout(() => {
            card.classList.add('slide-up');
        }, index * 100);
    });
}

/**
 * Create a job card element
 */
function createJobCard(job) {
    const card = document.createElement('div');
    card.className = 'job-card';
    card.setAttribute('data-job-id', job.id);
    
    const lastDate = job.important_dates?.last_date || job.important_dates?.found_date || 'Not specified';
    const skills = job.skills || [];
    
    card.innerHTML = sanitizeHTML(`
        <div class="job-header">
            <div>
                <h3 class="job-title">${escapeHTML(job.title)}</h3>
                <p class="job-source">${escapeHTML(job.source)}</p>
            </div>
            <span class="job-category">${escapeHTML(job.category)}</span>
        </div>
        <p class="job-description">${escapeHTML(job.description)}</p>
        ${skills.length > 0 ? `
            <div class="job-skills">
                ${skills.map(skill => `<span class="skill-tag">${escapeHTML(skill)}</span>`).join('')}
            </div>
        ` : ''}
        <div class="job-meta">
            <span class="job-date">Last Date: ${escapeHTML(lastDate)}</span>
        </div>
    `);
    
    // Add click event to open modal
    card.addEventListener('click', () => openJobModal(job));
    
    return card;
}

/**
 * Open job detail modal
 */
function openJobModal(job) {
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    const modalApplyBtn = document.getElementById('modalApplyBtn');
    
    if (!modalTitle || !modalBody || !modalApplyBtn) return;
    
    modalTitle.textContent = job.title;
    modalApplyBtn.href = sanitizeURL(job.url);
    
    const lastDate = job.important_dates?.last_date || job.important_dates?.found_date || 'Not specified';
    const examDate = job.important_dates?.exam_date || 'Not specified';
    const skills = job.skills || [];
    
    modalBody.innerHTML = sanitizeHTML(`
        <div class="modal-job-details">
            <div class="modal-section">
                <h4>Job Details</h4>
                <p><strong>Source:</strong> ${escapeHTML(job.source)}</p>
                <p><strong>Category:</strong> ${escapeHTML(job.category)}</p>
                <p><strong>Last Date to Apply:</strong> ${escapeHTML(lastDate)}</p>
                ${examDate !== 'Not specified' ? `<p><strong>Exam Date:</strong> ${escapeHTML(examDate)}</p>` : ''}
            </div>
            
            <div class="modal-section">
                <h4>Description</h4>
                <p>${escapeHTML(job.description)}</p>
            </div>
            
            ${skills.length > 0 ? `
                <div class="modal-section">
                    <h4>Required Skills</h4>
                    <div class="job-skills">
                        ${skills.map(skill => `<span class="skill-tag">${escapeHTML(skill)}</span>`).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${job.pdf_link ? `
                <div class="modal-section">
                    <h4>Additional Information</h4>
                    <p><a href="${sanitizeURL(job.pdf_link)}" target="_blank" class="pdf-link">Download Official Notification (PDF)</a></p>
                </div>
            ` : ''}
        </div>
    `);
    
    jobModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

/**
 * Close job modal
 */
function closeModal() {
    jobModal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

/**
 * Handle search functionality
 */
function handleSearch() {
    const searchTerm = jobSearch.value.toLowerCase().trim();
    
    if (searchTerm === '') {
        filteredJobs = [...jobsData];
    } else {
        filteredJobs = jobsData.filter(job => 
            job.title.toLowerCase().includes(searchTerm) ||
            job.description.toLowerCase().includes(searchTerm) ||
            job.source.toLowerCase().includes(searchTerm) ||
            job.category.toLowerCase().includes(searchTerm) ||
            (job.skills && job.skills.some(skill => skill.toLowerCase().includes(searchTerm)))
        );
    }
    
    currentPage = 1;
    renderJobs();
}

/**
 * Handle category filter
 */
function handleFilter() {
    const selectedCategory = categoryFilter.value;
    
    if (selectedCategory === '') {
        filteredJobs = [...jobsData];
    } else {
        filteredJobs = jobsData.filter(job => job.category === selectedCategory);
    }
    
    currentPage = 1;
    renderJobs();
}

/**
 * Filter by category (from category cards)
 */
function filterByCategory(category) {
    categoryFilter.value = category;
    handleFilter();
    
    // Scroll to jobs section
    document.getElementById('jobs').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Handle sorting
 */
function handleSort() {
    const sortBy = sortFilter.value;
    
    switch (sortBy) {
        case 'latest':
            // Sort by most recent (assuming newer jobs have higher IDs)
            filteredJobs.sort((a, b) => b.id.localeCompare(a.id));
            break;
        case 'deadline':
            // Sort by deadline (jobs with earlier deadlines first)
            filteredJobs.sort((a, b) => {
                const dateA = a.important_dates?.last_date || a.important_dates?.found_date || '31-12-2099';
                const dateB = b.important_dates?.last_date || b.important_dates?.found_date || '31-12-2099';
                return new Date(dateA.split('-').reverse().join('-')) - new Date(dateB.split('-').reverse().join('-'));
            });
            break;
        case 'category':
            // Sort alphabetically by category
            filteredJobs.sort((a, b) => a.category.localeCompare(b.category));
            break;
    }
    
    currentPage = 1;
    renderJobs();
}

/**
 * Load more jobs
 */
function loadMoreJobs() {
    if (isLoading) return;
    
    isLoading = true;
    loadMoreBtn.textContent = 'Loading...';
    
    setTimeout(() => {
        currentPage++;
        renderJobs();
        isLoading = false;
        loadMoreBtn.textContent = 'Load More Jobs';
    }, 500);
}

/**
 * Show/hide loading spinner
 */
function showLoading(show) {
    if (loadingSpinner) {
        loadingSpinner.style.display = show ? 'block' : 'none';
    }
}

/**
 * Update job counts in category cards
 */
function updateJobCounts() {
    const categoryCounts = {};
    
    jobsData.forEach(job => {
        categoryCounts[job.category] = (categoryCounts[job.category] || 0) + 1;
    });
    
    document.querySelectorAll('.category-card').forEach(card => {
        const category = card.dataset.category;
        const countElement = card.querySelector('.category-count');
        if (countElement && categoryCounts[category]) {
            countElement.textContent = `${categoryCounts[category]}+ Jobs`;
        }
    });
}

/**
 * Animate counters in hero section
 */
function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    counters.forEach(counter => {
        const target = parseInt(counter.dataset.target);
        const duration = 2000; // 2 seconds
        const step = target / (duration / 16); // 60 FPS
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            counter.textContent = Math.floor(current).toLocaleString();
        }, 16);
    });
}

/**
 * Setup intersection observer for animations
 */
function setupIntersectionObserver() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe sections for animation
    document.querySelectorAll('.section-title, .feature-card, .category-card').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Theme management
 */
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

/**
 * Open Telegram channel
 */
function openTelegramChannel() {
    // Replace with actual Telegram channel link
    window.open('https://t.me/sarkarisarthi', '_blank');
}

/**
 * Open WhatsApp channel
 */
function openWhatsappChannel() {
    // Replace with actual WhatsApp invite link
    window.open('https://chat.whatsapp.com/your-invite-link', '_blank');
}

/**
 * Toggle mobile menu
 */
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        navMenu.classList.toggle('active');
    }
}

/**
 * Handle keyboard navigation
 */
function handleKeyboardNavigation(e) {
    // Close modal with Escape key
    if (e.key === 'Escape' && jobModal.classList.contains('active')) {
        closeModal();
    }
    
    // Search with Ctrl+K or Cmd+K
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        jobSearch.focus();
    }
}

/**
 * Security utility: Escape HTML to prevent XSS
 */
function escapeHTML(str) {
    if (!str) return '';
    return str.toString()
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

/**
 * Security utility: Sanitize URLs to prevent javascript: and other dangerous protocols
 */
function sanitizeURL(url) {
    if (!url) return '#';
    const sanitized = url.trim();
    // Only allow http, https, and relative paths
    if (sanitized.toLowerCase().startsWith('javascript:') ||
        sanitized.toLowerCase().startsWith('data:') ||
        sanitized.toLowerCase().startsWith('vbscript:')) {
        return '#';
    }
    return sanitized;
}

/**
 * Utility function to format dates
 */
function formatDate(dateString) {
    if (!dateString) return 'Not specified';
    
    try {
        const parts = dateString.split('-');
        if (parts.length === 3) {
            const date = new Date(parts[2], parts[1] - 1, parts[0]);
            return date.toLocaleDateString('en-IN', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
            });
        }
    } catch (error) {
        console.error('Error formatting date:', error);
    }
    
    return dateString;
}

/**
 * Utility function to debounce search
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add debounced search
const debouncedSearch = debounce(handleSearch, 300);
if (jobSearch) {
    jobSearch.addEventListener('input', debouncedSearch);
}

// Service Worker registration for PWA (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        handleSearch,
        handleFilter,
        handleSort,
        formatDate,
        generateSampleJobs
    };
}

