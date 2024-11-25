document.addEventListener('DOMContentLoaded', () => {
    // Initialize live matches slider
    initLiveMatchesSlider();
    
    // Initialize statistics counter animation
    initStatCounters();
    
    // Initialize smooth scrolling
    initSmoothScroll();
    
    // Initialize feature card animations
    initFeatureCards();
});

function initLiveMatchesSlider() {
    const slider = document.querySelector('.live-matches-slider');
    if (!slider) return;

    let isDown = false;
    let startX;
    let scrollLeft;

    slider.addEventListener('mousedown', (e) => {
        isDown = true;
        slider.classList.add('active');
        startX = e.pageX - slider.offsetLeft;
        scrollLeft = slider.scrollLeft;
    });

    slider.addEventListener('mouseleave', () => {
        isDown = false;
        slider.classList.remove('active');
    });

    slider.addEventListener('mouseup', () => {
        isDown = false;
        slider.classList.remove('active');
    });

    slider.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - slider.offsetLeft;
        const walk = (x - startX) * 2;
        slider.scrollLeft = scrollLeft - walk;
    });

    // Auto scroll
    let scrollDirection = 1;
    const autoScroll = () => {
        if (!slider.matches(':hover')) {
            slider.scrollLeft += scrollDirection;
            if (slider.scrollLeft >= slider.scrollWidth - slider.clientWidth) {
                scrollDirection = -1;
            } else if (slider.scrollLeft <= 0) {
                scrollDirection = 1;
            }
        }
    };
    setInterval(autoScroll, 50);
}

function initStatCounters() {
    const stats = document.querySelectorAll('.stat-card h3');
    
    const observerCallback = (entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const value = parseInt(target.textContent);
                animateValue(target, 0, value, 2000);
                observer.unobserve(target);
            }
        });
    };

    const observer = new IntersectionObserver(observerCallback, {
        threshold: 0.5
    });

    stats.forEach(stat => {
        const value = stat.textContent;
        stat.textContent = '0';
        observer.observe(stat);
    });
}

function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const animate = () => {
        current += increment;
        element.textContent = Math.floor(current) + (element.textContent.includes('%') ? '%' : '+');
        
        if (current < end) {
            requestAnimationFrame(animate);
        } else {
            element.textContent = end + (element.textContent.includes('%') ? '%' : '+');
        }
    };
    
    animate();
}

function initSmoothScroll() {
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
}

function initFeatureCards() {
    const cards = document.querySelectorAll('.feature-card');
    
    const observerCallback = (entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    };

    const observer = new IntersectionObserver(observerCallback, {
        threshold: 0.1,
        rootMargin: '50px'
    });

    cards.forEach(card => {
        observer.observe(card);
    });
}

// Live match updates via WebSocket
if (typeof io !== 'undefined') {
    const socket = io();

    socket.on('connect', () => {
        console.log('Connected to WebSocket server');
    });

    socket.on('live_match_update', (data) => {
        updateMatchCard(data);
    });
}

function updateMatchCard(matchData) {
    const card = document.querySelector(`[data-match-id="${matchData.match_id}"]`);
    if (!card) return;

    const homeScore = card.querySelector('.home-score');
    const awayScore = card.querySelector('.away-score');
    const matchTime = card.querySelector('.match-time');

    if (homeScore) homeScore.textContent = matchData.home_score;
    if (awayScore) awayScore.textContent = matchData.away_score;
    if (matchTime) matchTime.textContent = `${matchData.current_time}'`;

    // Add update animation
    card.classList.add('update-flash');
    setTimeout(() => card.classList.remove('update-flash'), 1000);
}
