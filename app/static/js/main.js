// Main JavaScript file for Sports Analytics Platform

// Constants
const MATCH_STATUS = {
    SCHEDULED: 'scheduled',
    LIVE: 'live',
    FINISHED: 'finished',
    POSTPONED: 'postponed',
    CANCELLED: 'cancelled',
    SUSPENDED: 'suspended',
    INTERRUPTED: 'interrupted'
};

const STATUS_CLASSES = {
    [MATCH_STATUS.LIVE]: 'bg-danger',
    [MATCH_STATUS.SCHEDULED]: 'bg-primary',
    [MATCH_STATUS.FINISHED]: 'bg-success',
    [MATCH_STATUS.POSTPONED]: 'bg-warning',
    [MATCH_STATUS.CANCELLED]: 'bg-dark',
    [MATCH_STATUS.SUSPENDED]: 'bg-warning',
    [MATCH_STATUS.INTERRUPTED]: 'bg-warning'
};

const STATUS_DISPLAY = {
    [MATCH_STATUS.LIVE]: 'LIVE',
    [MATCH_STATUS.SCHEDULED]: 'Scheduled',
    [MATCH_STATUS.FINISHED]: 'Finished',
    [MATCH_STATUS.POSTPONED]: 'Postponed',
    [MATCH_STATUS.CANCELLED]: 'Cancelled',
    [MATCH_STATUS.SUSPENDED]: 'Suspended',
    [MATCH_STATUS.INTERRUPTED]: 'Interrupted'
};

// Utility Functions
const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
        const options = { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZoneName: 'short'
        };
        return new Date(dateString).toLocaleDateString('en-US', options);
    } catch (error) {
        console.error('Error formatting date:', error);
        return dateString;
    }
};

const formatNumber = (number) => {
    if (number === null || number === undefined) return '0';
    try {
        return new Intl.NumberFormat('en-US', {
            maximumFractionDigits: 1
        }).format(number);
    } catch (error) {
        console.error('Error formatting number:', error);
        return '0';
    }
};

// Live Score Updates
const updateLiveScores = () => {
    fetch('/api/live-matches')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success' && Array.isArray(data.matches)) {
                const updatedMatches = new Set();
                
                data.matches.forEach(match => {
                    if (!match || !match.id) return;
                    
                    const matchElement = document.querySelector(`#match-${match.id}`);
                    if (!matchElement) return;
                    
                    updatedMatches.add(match.id);
                    updateMatchElement(matchElement, match);
                });
                
                // Update status of matches not in the response
                document.querySelectorAll('.match-card').forEach(element => {
                    const matchId = element.id.replace('match-', '');
                    if (!updatedMatches.has(parseInt(matchId))) {
                        const statusElement = element.querySelector('.match-status');
                        if (statusElement) {
                            updateMatchStatus(statusElement, MATCH_STATUS.FINISHED);
                        }
                    }
                });
            } else {
                console.warn('Invalid data format received from server:', data);
            }
        })
        .catch(error => {
            console.error('Error updating live scores:', error);
            showNotification('Unable to update live scores. Will retry shortly.', 'warning');
        });
};

const updateMatchElement = (element, match) => {
    try {
        // Update score
        const scoreElement = element.querySelector('.match-score');
        if (scoreElement) {
            const newScore = `${match.home_score ?? 0} - ${match.away_score ?? 0}`;
            if (scoreElement.textContent !== newScore) {
                scoreElement.textContent = newScore;
                element.classList.add('score-updated');
                setTimeout(() => element.classList.remove('score-updated'), 1000);
            }
        }
        
        // Update status
        const statusElement = element.querySelector('.match-status');
        if (statusElement) {
            updateMatchStatus(statusElement, match.status);
        }
        
        // Update time
        const timeElement = element.querySelector('.match-time');
        if (timeElement && match.start_time) {
            timeElement.textContent = formatDate(match.start_time);
        }
        
        // Update team names if provided
        if (match.home_team) {
            const homeTeamElement = element.querySelector('.home-team');
            if (homeTeamElement) homeTeamElement.textContent = match.home_team;
        }
        if (match.away_team) {
            const awayTeamElement = element.querySelector('.away-team');
            if (awayTeamElement) awayTeamElement.textContent = match.away_team;
        }
        
    } catch (error) {
        console.error('Error updating match element:', error);
    }
};

const updateMatchStatus = (statusElement, status) => {
    const normalizedStatus = status?.toLowerCase() ?? MATCH_STATUS.SCHEDULED;
    statusElement.textContent = STATUS_DISPLAY[normalizedStatus] ?? 'Unknown';
    statusElement.className = `badge match-status ${STATUS_CLASSES[normalizedStatus] ?? 'bg-secondary'}`;
};

// Initialize live score updates if there are live matches
const initializeLiveScores = () => {
    const matchElements = document.querySelectorAll('.match-card');
    if (matchElements.length > 0) {
        updateLiveScores(); // Initial update
        const updateInterval = setInterval(updateLiveScores, 30000); // Update every 30 seconds
        
        // Cleanup on page leave
        window.addEventListener('beforeunload', () => {
            clearInterval(updateInterval);
        });
    }
};

// Form Validation
const validateForm = (form) => {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('is-invalid');
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
};

// Form Submission Handler
const initializeFormHandlers = () => {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
                const firstInvalid = form.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
                showNotification('Please fill in all required fields.', 'warning');
            }
        });
    });
};

// Initialize Charts
const initializeCharts = () => {
    const predictionChart = document.getElementById('predictionChart');
    if (predictionChart) {
        new Chart(predictionChart, {
            type: 'doughnut',
            data: {
                labels: ['Correct', 'Incorrect'],
                datasets: [{
                    data: [
                        predictionChart.dataset.correct || 0,
                        predictionChart.dataset.incorrect || 0
                    ],
                    backgroundColor: ['#28a745', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
};

// Initialize tooltips and popovers
const initializeBootstrapComponents = () => {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
};

// Notification System
const showNotification = (message, type = 'info') => {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.notification-container') || document.body;
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
};

// Dynamic Content Loading
const loadMoreContent = (url, container, button) => {
    const page = parseInt(button.dataset.page) || 1;
    
    // Show loading state
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    
    fetch(`${url}?page=${page + 1}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.html) {
                container.insertAdjacentHTML('beforeend', data.html);
                button.dataset.page = page + 1;
                
                if (!data.has_more) {
                    button.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Error loading more content:', error);
            showNotification('Error loading more content. Please try again.', 'danger');
        })
        .finally(() => {
            // Reset button state
            button.disabled = false;
            button.innerHTML = 'Load More';
        });
};

// Initialize all components when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeBootstrapComponents();
    initializeCharts();
    initializeLiveScores();
    initializeFormHandlers();
    
    // Setup infinite scroll buttons
    document.querySelectorAll('.load-more-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const container = document.querySelector(button.dataset.container);
            if (container) {
                loadMoreContent(button.dataset.url, container, button);
            }
        });
    });
});

// Export functions for use in other scripts
window.sportsAnalytics = {
    formatDate,
    formatNumber,
    showNotification,
    loadMoreContent,
    updateLiveScores,
    MATCH_STATUS,
    STATUS_DISPLAY
};
