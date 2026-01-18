/**
 * LocalMind Website JavaScript
 * Svetozar Technologies
 */

document.addEventListener('DOMContentLoaded', function() {
    // Note: i18n is initialized automatically by i18n.js
    // No need to initialize here as i18n.js handles everything

    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            this.classList.toggle('active');
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;

            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                const navbarHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navbarHeight;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                if (navLinks) {
                    navLinks.classList.remove('active');
                }
                if (mobileMenuBtn) {
                    mobileMenuBtn.classList.remove('active');
                }
            }
        });
    });

    // Navbar background on scroll
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe feature cards and download cards for animations
    document.querySelectorAll('.feature-card, .download-card, .step').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });

    // Add animation class styles
    const style = document.createElement('style');
    style.textContent = `
        .animate-in {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }

        .nav-links.active {
            display: flex;
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            flex-direction: column;
            background: rgba(10, 10, 10, 0.98);
            padding: 24px;
            gap: 16px;
            border-bottom: 1px solid var(--color-border);
        }

        .mobile-menu-btn.active span:nth-child(1) {
            transform: rotate(45deg) translate(6px, 6px);
        }

        .mobile-menu-btn.active span:nth-child(2) {
            opacity: 0;
        }

        .mobile-menu-btn.active span:nth-child(3) {
            transform: rotate(-45deg) translate(6px, -6px);
        }

        .navbar.scrolled {
            background: rgba(10, 10, 10, 0.95);
        }
    `;
    document.head.appendChild(style);

    // Track download clicks (for analytics)
    document.querySelectorAll('.download-card').forEach(card => {
        card.addEventListener('click', function() {
            const platform = this.querySelector('h3').textContent;
            console.log('Download clicked:', platform);
            // Add your analytics tracking here
            // e.g., gtag('event', 'download', { platform: platform });
        });
    });

    // ================================================
    // Email Capture Modal Logic
    // ================================================
    
    const modal = document.getElementById('emailCaptureModal');
    const modalClose = document.querySelector('.modal-close');
    const emailForm = document.getElementById('emailCaptureForm');
    const skipBtn = document.getElementById('skipBtn');
    const successState = document.getElementById('successState');
    let downloadUrl = '';
    
    // Track event with Plausible Analytics
    function trackEvent(eventName, props = {}) {
        if (window.plausible) {
            window.plausible(eventName, { props });
        }
        console.log('Event tracked:', eventName, props);
    }
    
    // Open modal function
    function openModal(url) {
        downloadUrl = url;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scroll
        trackEvent('Modal Viewed');
    }
    
    // Close modal function
    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = ''; // Restore scroll
        
        // Reset form after a delay
        setTimeout(() => {
            emailForm.reset();
            emailForm.style.display = 'block';
            successState.style.display = 'none';
        }, 300);
    }
    
    // Download function
    function triggerDownload() {
        if (downloadUrl) {
            window.location.href = downloadUrl;
            trackEvent('Download Started', { url: downloadUrl });
        }
    }
    
    // Handle download button clicks
    const macOSDownloadBtn = document.getElementById('macOSDownloadBtn');
    const heroDownloadBtn = document.getElementById('heroDownloadBtn');
    const ctaDownloadBtn = document.getElementById('ctaDownloadBtn');
    
    if (macOSDownloadBtn) {
        macOSDownloadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('data-download-url');
            openModal(url);
        });
    }
    
    // Hero and CTA buttons scroll to download section
    // They will trigger modal once user clicks the actual download card
    
    // Close modal on X button click
    if (modalClose) {
        modalClose.addEventListener('click', closeModal);
    }
    
    // Close modal on overlay click
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
                trackEvent('Modal Closed', { method: 'overlay' });
            }
        });
    }
    
    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
            trackEvent('Modal Closed', { method: 'escape' });
        }
    });
    
    // Handle form submission
    if (emailForm) {
        emailForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(emailForm);
            const email = formData.get('email');
            const name = formData.get('name');
            const featureSRT = formData.get('feature_srt');
            const featureRealtime = formData.get('feature_realtime');
            const featureAPI = formData.get('feature_api');
            
            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert('Please enter a valid email address.');
                return;
            }
            
            // Disable submit button
            const submitBtn = emailForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';
            
            try {
                // Submit to Formspree
                const response = await fetch(emailForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'Accept': 'application/json'
                    }
                });
                
                if (response.ok) {
                    // Show success state
                    emailForm.style.display = 'none';
                    successState.style.display = 'block';
                    
                    // Update download link in success state
                    const downloadLink = successState.querySelector('.btn-download-final');
                    if (downloadLink && downloadUrl) {
                        downloadLink.href = downloadUrl;
                    }
                    
                    // Track successful email capture
                    trackEvent('Email Captured', {
                        has_name: !!name,
                        feature_srt: featureSRT === 'yes',
                        feature_realtime: featureRealtime === 'yes',
                        feature_api: featureAPI === 'yes'
                    });
                    
                    // Auto-trigger download after 2 seconds
                    setTimeout(() => {
                        triggerDownload();
                    }, 2000);
                } else {
                    const data = await response.json();
                    throw new Error(data.error || 'Submission failed');
                }
            } catch (error) {
                console.error('Form submission error:', error);
                alert('Something went wrong. Please try again or click "Skip" to download directly.');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }
    
    // Handle skip button
    if (skipBtn) {
        skipBtn.addEventListener('click', function() {
            trackEvent('Email Skipped');
            triggerDownload();
            closeModal();
        });
    }
    
    // ================================================
    // FAQ Accordion
    // ================================================
    
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        question.addEventListener('click', function() {
            const isActive = item.classList.contains('active');
            
            // Close all other FAQs
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                }
            });
            
            // Toggle current FAQ
            if (isActive) {
                item.classList.remove('active');
            } else {
                item.classList.add('active');
                trackEvent('FAQ Opened', { question: question.textContent.trim() });
            }
        });
    });
    
    // ================================================
    // GitHub Stars Counter (Optional)
    // ================================================
    
    async function fetchGitHubStars() {
        try {
            const response = await fetch('https://api.github.com/repos/KaivalyaDeepTeam/localmind');
            const data = await response.json();
            const starsElement = document.getElementById('githubStars');
            
            if (starsElement && data.stargazers_count !== undefined) {
                const stars = data.stargazers_count;
                starsElement.textContent = stars > 0 ? `${stars}+` : 'Star us!';
            }
        } catch (error) {
            console.log('Could not fetch GitHub stars:', error);
        }
    }
    
    // Fetch stars on page load (optional, commented out to avoid rate limiting)
    // fetchGitHubStars();
    
    // ================================================
    // Update Animations for New Sections
    // ================================================
    
    // Observe new elements for scroll animations
    document.querySelectorAll('.use-case-card, .testimonial-card, .faq-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });
});
