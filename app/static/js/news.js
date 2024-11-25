document.addEventListener('DOMContentLoaded', () => {
    // Initialize variables
    let currentPage = 1;
    let currentSport = 'all';
    let currentSearch = '';
    let isLoading = false;
    let hasMorePages = true;

    // Get DOM elements
    const newsGrid = document.getElementById('news-grid');
    const loadMoreBtn = document.getElementById('load-more-btn');
    const searchInput = document.getElementById('news-search');
    const searchBtn = document.getElementById('search-btn');
    const sportFilters = document.querySelectorAll('.sport-filter');
    const loadingSpinner = document.getElementById('loading-spinner');

    // Initialize infinite scroll
    initInfiniteScroll();

    // Initialize search
    initSearch();

    // Initialize sport filters
    initSportFilters();

    function initInfiniteScroll() {
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', loadMoreNews);

            // Infinite scroll
            window.addEventListener('scroll', () => {
                if (isLoading || !hasMorePages) return;

                const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
                if (scrollTop + clientHeight >= scrollHeight - 100) {
                    loadMoreNews();
                }
            });
        }
    }

    function initSearch() {
        let searchTimeout;

        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                currentSearch = e.target.value;
                resetAndSearch();
            }, 500);
        });

        searchBtn.addEventListener('click', () => {
            currentSearch = searchInput.value;
            resetAndSearch();
        });
    }

    function initSportFilters() {
        sportFilters.forEach(filter => {
            filter.addEventListener('click', () => {
                // Update active state
                sportFilters.forEach(f => f.classList.remove('active'));
                filter.classList.add('active');

                // Update current sport and reset search
                currentSport = filter.dataset.sport;
                resetAndSearch();
            });
        });
    }

    async function loadMoreNews() {
        if (isLoading || !hasMorePages) return;

        isLoading = true;
        showLoading(true);

        try {
            const params = new URLSearchParams({
                page: currentPage + 1,
                sport: currentSport,
                search: currentSearch
            });

            const response = await fetch(`${API_URL}?${params}`);
            const data = await response.json();

            if (data.items.length > 0) {
                appendNewsItems(data.items);
                currentPage++;
                hasMorePages = currentPage < data.total_pages;

                if (!hasMorePages && loadMoreBtn) {
                    loadMoreBtn.style.display = 'none';
                }
            } else {
                hasMorePages = false;
                if (loadMoreBtn) {
                    loadMoreBtn.style.display = 'none';
                }
            }
        } catch (error) {
            console.error('Error loading news:', error);
            showError('Failed to load news. Please try again later.');
        } finally {
            isLoading = false;
            showLoading(false);
        }
    }

    function resetAndSearch() {
        currentPage = 1;
        hasMorePages = true;
        newsGrid.innerHTML = '';
        showLoading(true);

        // Add skeleton loading cards
        for (let i = 0; i < 6; i++) {
            newsGrid.appendChild(createSkeletonCard());
        }

        loadMoreNews().then(() => {
            // Remove skeleton cards
            const skeletons = newsGrid.querySelectorAll('.skeleton');
            skeletons.forEach(skeleton => skeleton.remove());
        });
    }

    function appendNewsItems(items) {
        items.forEach(item => {
            const article = createNewsCard(item);
            newsGrid.appendChild(article);
        });
    }

    function createNewsCard(item) {
        const article = document.createElement('article');
        article.className = 'news-card';
        article.innerHTML = `
            <div class="news-image">
                <img src="${item.image_url}" alt="${item.title}">
                <div class="news-category">${item.sport}</div>
            </div>
            <div class="news-content">
                <h3>${item.title}</h3>
                <p>${item.summary}</p>
                <div class="news-meta">
                    <span class="news-date">${item.date}</span>
                    <span class="news-source">${item.source}</span>
                </div>
                <a href="#" class="read-more">Read More</a>
            </div>
        `;
        return article;
    }

    function createSkeletonCard() {
        const article = document.createElement('article');
        article.className = 'news-card skeleton';
        article.innerHTML = `
            <div class="news-image"></div>
            <div class="news-content">
                <h3></h3>
                <p></p>
            </div>
        `;
        return article;
    }

    function showLoading(show) {
        if (loadingSpinner) {
            loadingSpinner.style.display = show ? 'block' : 'none';
        }
    }

    function showError(message) {
        // Create error message element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;

        // Insert error message after the news grid
        newsGrid.parentNode.insertBefore(errorDiv, newsGrid.nextSibling);

        // Remove error message after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
});
