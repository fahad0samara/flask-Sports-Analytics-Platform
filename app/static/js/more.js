document.addEventListener('DOMContentLoaded', () => {
    // Initialize Intersection Observer for animations
    initIntersectionObserver();

    // Initialize FAQ accordions
    initFAQAccordions();

    // Initialize statistics counter
    initStatisticsCounter();
});

function initIntersectionObserver() {
    const options = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target); // Only animate once
            }
        });
    }, options);

    // Observe all animated elements
    const elements = document.querySelectorAll('.feature-card, .step, .sport-card, .stat-card, .faq-item');
    elements.forEach(element => observer.observe(element));
}

function initFAQAccordions() {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');
            
            // Close all other FAQs
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                }
            });

            // Toggle current FAQ
            item.classList.toggle('active');

            // Animate icon rotation
            const icon = question.querySelector('i');
            icon.style.transform = isActive ? 'rotate(0deg)' : 'rotate(180deg)';
        });
    });
}

function initStatisticsCounter() {
    const stats = document.querySelectorAll('.stat-number');
    
    stats.forEach(stat => {
        const targetValue = parseInt(stat.dataset.value);
        animateValue(stat, 0, targetValue, 2000);
    });
}

function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = end > start ? 1 : -1;
    const stepTime = Math.abs(Math.floor(duration / range));
    const isDecimal = String(end).includes('.');
    const decimals = isDecimal ? String(end).split('.')[1].length : 0;
    
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        
        // Format the number based on whether it's a decimal
        const formattedValue = isDecimal ? 
            current.toFixed(decimals) : 
            current;
        
        // Add percentage symbol if needed
        const displayValue = element.classList.contains('percentage') ? 
            `${formattedValue}%` : 
            formattedValue;
        
        element.textContent = displayValue;
        
        if (current === end) {
            clearInterval(timer);
        }
    }, stepTime);
}

// Add smooth scrolling for anchor links
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
