<<<<<<< HEAD
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

    jobsToRender.forEach(job => {
        const jobCard = createJobCard(job);
        jobsGrid.appendChild(jobCard);
    });

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

    card.innerHTML = `
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
    `;

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

    modalBody.innerHTML = `
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
    `;

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

=======
function escapeHTML(e){if(!e)return"";const t={"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"};return String(e).replace(/[&<>"']/g,function(e){return t[e]})}function sanitizeURL(e){if(!e)return"#";try{const t=new URL(e,window.location.href);if("http:"===t.protocol||"https:"===t.protocol)return t.href}catch(t){if(e.startsWith("/")||e.startsWith("./")||e.startsWith("../"))return escapeHTML(e)}return"#"}let jobsData=[],filteredJobs=[],currentPage=1;const jobsPerPage=12;let isLoading=!1;const jobsGrid=document.getElementById("jobsGrid"),loadingSpinner=document.getElementById("loadingSpinner"),loadMoreBtn=document.getElementById("loadMoreBtn"),jobSearch=document.getElementById("jobSearch"),categoryFilter=document.getElementById("categoryFilter"),sortFilter=document.getElementById("sortFilter"),searchBtn=document.getElementById("searchBtn"),themeToggle=document.getElementById("themeToggle"),telegramBtn=document.getElementById("telegramBtn"),footerTelegramBtn=document.getElementById("footerTelegramBtn"),mobileMenuToggle=document.getElementById("mobileMenuToggle"),jobModal=document.getElementById("jobModal"),modalClose=document.getElementById("modalClose"),modalClose2=document.getElementById("modalClose2");function initializeApp(){setupEventListeners(),loadTheme(),loadJobs(),animateCounters(),setupIntersectionObserver()}function setupEventListeners(){searchBtn.addEventListener("click",handleSearch),jobSearch.addEventListener("keypress",function(e){"Enter"===e.key&&handleSearch()}),categoryFilter.addEventListener("change",handleFilter),sortFilter.addEventListener("change",handleSort),loadMoreBtn.addEventListener("click",loadMoreJobs),themeToggle.addEventListener("click",toggleTheme),telegramBtn&&telegramBtn.addEventListener("click",openTelegramChannel),footerTelegramBtn&&footerTelegramBtn.addEventListener("click",openTelegramChannel),mobileMenuToggle&&mobileMenuToggle.addEventListener("click",toggleMobileMenu),modalClose&&modalClose.addEventListener("click",closeModal),modalClose2&&modalClose2.addEventListener("click",closeModal),jobModal.addEventListener("click",function(e){e.target===jobModal&&closeModal()}),document.querySelectorAll(".category-card").forEach(e=>{e.addEventListener("click",function(){filterByCategory(this.dataset.category)})}),document.addEventListener("keydown",handleKeyboardNavigation)}async function loadJobs(){try{showLoading(!0);const e=await fetch("jobs/job_manifest.json");if(e.ok){const t=await e.json();jobsData=t.jobs||[]}else jobsData=generateSampleJobs();filteredJobs=[...jobsData],renderJobs(),updateJobCounts()}catch(e){console.error("Error loading jobs:",e),jobsData=generateSampleJobs(),filteredJobs=[...jobsData],renderJobs(),updateJobCounts()}finally{showLoading(!1)}}function generateSampleJobs(){return[{id:"sample1",title:"SBI Clerk Recruitment 2024",source:"State Bank of India",category:"Banking",description:"State Bank of India invites applications for the post of Junior Associate (Customer Support & Sales) in Clerical Cadre. This is a great opportunity for candidates looking to start their career in the banking sector.",url:"https://sbi.co.in/careers",important_dates:{last_date:"15-02-2024",exam_date:"10-03-2024"},skills:["Banking","Customer Service","Computer Skills"],pdf_link:null},{id:"sample2",title:"SSC CGL 2024 Notification",source:"Staff Selection Commission",category:"SSC",description:"Staff Selection Commission has released notification for Combined Graduate Level Examination 2024. Various posts are available across different ministries and departments.",url:"https://ssc.nic.in",important_dates:{last_date:"20-02-2024",exam_date:"15-04-2024"},skills:["General Knowledge","Mathematics","English","Reasoning"],pdf_link:null},{id:"sample3",title:"Railway Group D Recruitment",source:"Indian Railways",category:"Railway",description:"Railway Recruitment Board invites applications for Group D posts including Track Maintainer, Helper, Assistant Pointsman, and other technical posts.",url:"https://indianrailways.gov.in",important_dates:{last_date:"25-02-2024"},skills:["Technical Skills","Physical Fitness"],pdf_link:null},{id:"sample4",title:"UPSC Civil Services Preliminary Exam 2024",source:"Union Public Service Commission",category:"UPSC",description:"UPSC has announced the Civil Services Preliminary Examination 2024 for recruitment to various Group A and Group B services.",url:"https://upsc.gov.in",important_dates:{last_date:"28-02-2024",exam_date:"26-05-2024"},skills:["General Studies","Current Affairs","Optional Subject"],pdf_link:null},{id:"sample5",title:"Delhi Police Constable Recruitment",source:"Delhi Police",category:"Police",description:"Delhi Police invites applications for the post of Constable (Executive) Male and Female. Physical and written tests will be conducted.",url:"https://delhipolice.nic.in",important_dates:{last_date:"18-02-2024"},skills:["Physical Fitness","General Knowledge","Hindi","English"],pdf_link:null},{id:"sample6",title:"Indian Army Agniveer Recruitment",source:"Indian Army",category:"Defence",description:"Indian Army is recruiting Agniveers for various technical and non-technical posts. This is under the Agnipath scheme.",url:"https://joinindianarmy.nic.in",important_dates:{last_date:"22-02-2024"},skills:["Physical Fitness","Technical Skills","Discipline"],pdf_link:null}]}function renderJobs(){if(!jobsGrid)return;const e=12*(currentPage-1),t=e+12,n=filteredJobs.slice(0,t);if(1===currentPage&&(jobsGrid.innerHTML=""),0===n.length)return jobsGrid.innerHTML='<div class="no-jobs"><h3>No jobs found</h3><p>Try adjusting your search criteria.</p></div>',void(loadMoreBtn.style.display="none");n.slice(e).forEach(e=>{const t=createJobCard(e);jobsGrid.appendChild(t)}),t>=filteredJobs.length?loadMoreBtn.style.display="none":loadMoreBtn.style.display="block";jobsGrid.querySelectorAll(".job-card:not(.animated)").forEach((e,t)=>{e.classList.add("animated"),setTimeout(()=>{e.classList.add("slide-up")},100*t)})}function createJobCard(e){const t=document.createElement("div");t.className="job-card",t.setAttribute("data-job-id",e.id);const n=e.important_dates?.last_date||e.important_dates?.found_date||"Not specified",o=e.skills||[];return t.innerHTML=`\n        <div class="job-header">\n            <div>\n                <h3 class="job-title">${escapeHTML(e.title)}</h3>\n                <p class="job-source">${escapeHTML(e.source)}</p>\n            </div>\n            <span class="job-category">${escapeHTML(e.category)}</span>\n        </div>\n        <p class="job-description">${escapeHTML(e.description)}</p>\n        ${o.length>0?`\n            <div class="job-skills">\n                ${o.map(e=>`<span class="skill-tag">${escapeHTML(e)}</span>`).join("")}\n            </div>\n        `:""}\n        <div class="job-meta">\n            <span class="job-date">Last Date: ${escapeHTML(n)}</span>\n        </div>\n    `,t.addEventListener("click",()=>openJobModal(e)),t}function openJobModal(e){const t=document.getElementById("modalTitle"),n=document.getElementById("modalBody"),o=document.getElementById("modalApplyBtn");if(!t||!n||!o)return;t.textContent=e.title,o.href=sanitizeURL(e.url);const a=e.important_dates?.last_date||e.important_dates?.found_date||"Not specified",i=e.important_dates?.exam_date||"Not specified",r=e.skills||[];n.innerHTML=`\n        <div class="modal-job-details">\n            <div class="modal-section">\n                <h4>Job Details</h4>\n                <p><strong>Source:</strong> ${escapeHTML(e.source)}</p>\n                <p><strong>Category:</strong> ${escapeHTML(e.category)}</p>\n                <p><strong>Last Date to Apply:</strong> ${escapeHTML(a)}</p>\n                ${"Not specified"!==i?`<p><strong>Exam Date:</strong> ${escapeHTML(i)}</p>`:""}\n            </div>\n            \n            <div class="modal-section">\n                <h4>Description</h4>\n                <p>${escapeHTML(e.description)}</p>\n            </div>\n            \n            ${r.length>0?`\n                <div class="modal-section">\n                    <h4>Required Skills</h4>\n                    <div class="job-skills">\n                        ${r.map(e=>`<span class="skill-tag">${escapeHTML(e)}</span>`).join("")}\n                    </div>\n                </div>\n            `:""}\n            \n            ${e.pdf_link?`\n                <div class="modal-section">\n                    <h4>Additional Information</h4>\n                    <p><a href="${sanitizeURL(e.pdf_link)}" target="_blank" class="pdf-link">Download Official Notification (PDF)</a></p>\n                </div>\n            `:""}\n        </div>\n    `,jobModal.classList.add("active"),document.body.style.overflow="hidden"}function closeModal(){jobModal.classList.remove("active"),document.body.style.overflow="auto"}function handleSearch(){const e=jobSearch.value.toLowerCase().trim();filteredJobs=""===e?[...jobsData]:jobsData.filter(t=>t.title.toLowerCase().includes(e)||t.description.toLowerCase().includes(e)||t.source.toLowerCase().includes(e)||t.category.toLowerCase().includes(e)||t.skills&&t.skills.some(t=>t.toLowerCase().includes(e))),currentPage=1,renderJobs()}function handleFilter(){const e=categoryFilter.value;filteredJobs=""===e?[...jobsData]:jobsData.filter(t=>t.category===e),currentPage=1,renderJobs()}function filterByCategory(e){categoryFilter.value=e,handleFilter(),document.getElementById("jobs").scrollIntoView({behavior:"smooth"})}function handleSort(){switch(sortFilter.value){case"latest":filteredJobs.sort((e,t)=>t.id.localeCompare(e.id));break;case"deadline":filteredJobs.sort((e,t)=>{const n=e.important_dates?.last_date||e.important_dates?.found_date||"31-12-2099",o=t.important_dates?.last_date||t.important_dates?.found_date||"31-12-2099";return new Date(n.split("-").reverse().join("-"))-new Date(o.split("-").reverse().join("-"))});break;case"category":filteredJobs.sort((e,t)=>e.category.localeCompare(t.category))}currentPage=1,renderJobs()}function loadMoreJobs(){isLoading||(isLoading=!0,loadMoreBtn.textContent="Loading...",setTimeout(()=>{currentPage++,renderJobs(),isLoading=!1,loadMoreBtn.textContent="Load More Jobs"},500))}function showLoading(e){loadingSpinner&&(loadingSpinner.style.display=e?"block":"none")}function updateJobCounts(){const e={};jobsData.forEach(t=>{e[t.category]=(e[t.category]||0)+1}),document.querySelectorAll(".category-card").forEach(t=>{const n=t.dataset.category,o=t.querySelector(".category-count");o&&e[n]&&(o.textContent=`${e[n]}+ Jobs`)})}function animateCounters(){document.querySelectorAll(".stat-number").forEach(e=>{const t=parseInt(e.dataset.target),n=t/125;let o=0;const a=setInterval(()=>{o+=n,o>=t&&(o=t,clearInterval(a)),e.textContent=Math.floor(o).toLocaleString()},16)})}function setupIntersectionObserver(){const e=new IntersectionObserver(e=>{e.forEach(e=>{e.isIntersecting&&e.target.classList.add("fade-in")})},{threshold:.1,rootMargin:"0px 0px -50px 0px"});document.querySelectorAll(".section-title, .feature-card, .category-card").forEach(t=>{e.observe(t)})}function loadTheme(){const e=localStorage.getItem("theme")||"light";document.documentElement.setAttribute("data-theme",e),updateThemeIcon(e)}function toggleTheme(){const e="dark"===document.documentElement.getAttribute("data-theme")?"light":"dark";document.documentElement.setAttribute("data-theme",e),localStorage.setItem("theme",e),updateThemeIcon(e)}function updateThemeIcon(e){const t=document.querySelector(".theme-icon");t&&(t.textContent="dark"===e?"☀️":"🌙")}function openTelegramChannel(){window.open("https://t.me/sarkarisarthi","_blank")}function toggleMobileMenu(){const e=document.querySelector(".nav-menu");e&&e.classList.toggle("active")}function handleKeyboardNavigation(e){"Escape"===e.key&&jobModal.classList.contains("active")&&closeModal(),(e.ctrlKey||e.metaKey)&&"k"===e.key&&(e.preventDefault(),jobSearch.focus())}function formatDate(e){if(!e)return"Not specified";try{const t=e.split("-");if(3===t.length){return new Date(t[2],t[1]-1,t[0]).toLocaleDateString("en-IN",{day:"numeric",month:"long",year:"numeric"})}}catch(e){console.error("Error formatting date:",e)}return e}function debounce(e,t){let n;return function(...o){clearTimeout(n),n=setTimeout(()=>{clearTimeout(n),e(...o)},t)}}document.addEventListener("DOMContentLoaded",function(){initializeApp()});const debouncedSearch=debounce(handleSearch,300);jobSearch&&jobSearch.addEventListener("input",debouncedSearch),"serviceWorker"in navigator&&window.addEventListener("load",()=>{navigator.serviceWorker.register("/sw.js").then(e=>{console.log("SW registered: ",e)}).catch(e=>{console.log("SW registration failed: ",e)})}),"undefined"!=typeof module&&module.exports&&(module.exports={handleSearch:handleSearch,handleFilter:handleFilter,handleSort:handleSort,formatDate:formatDate,generateSampleJobs:generateSampleJobs}),document.addEventListener("contextmenu",function(e){e.preventDefault()}),document.addEventListener("keydown",function(e){return"F12"===e.key||123===e.keyCode?(e.preventDefault(),!1):(!e.ctrlKey&&!e.metaKey||!e.shiftKey||"I"!==e.key&&"i"!==e.key)&&(!e.ctrlKey&&!e.metaKey||!e.shiftKey||"J"!==e.key&&"j"!==e.key)&&(!e.ctrlKey&&!e.metaKey||"U"!==e.key&&"u"!==e.key)&&(!e.ctrlKey&&!e.metaKey||"S"!==e.key&&"s"!==e.key)&&(!e.ctrlKey&&!e.metaKey||"C"!==e.key&&"c"!==e.key)?void 0:(e.preventDefault(),!1)}),document.addEventListener("dragstart",function(e){e.preventDefault()}),document.addEventListener("selectstart",function(e){e.preventDefault()}),setInterval(function(){(function(){return!1}).constructor("debugger")()},1e3),document.addEventListener("DOMContentLoaded",()=>{document.querySelectorAll("#premiumBtn, #premiumFooterBtn, .premium-btn-footer, .premium-btn").forEach(e=>{e&&e.addEventListener("click",e=>{e.preventDefault(),alert("Premium Membership portal is securely loading..."),window.location.href="#premium"})});document.querySelectorAll("#donateBtn, .donate-btn").forEach(e=>{e&&e.addEventListener("click",e=>{e.preventDefault(),alert("Redirecting to secure payment gateway for your coffee support..."),window.location.href="#donate"})})});
>>>>>>> b8f1564 (Save my changes before merge)
