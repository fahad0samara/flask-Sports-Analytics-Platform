// Initialize Socket.IO connection
const socket = io();

// Store subscribed matches
let subscribedMatches = new Set();

// Connect handler
socket.on('connect', () => {
    console.log('Connected to WebSocket server');
    // Resubscribe to matches after reconnection
    subscribedMatches.forEach(matchId => {
        subscribeToMatch(matchId);
    });
});

// Subscribe to match updates
function subscribeToMatch(matchId) {
    socket.emit('subscribe', { match_id: matchId });
    subscribedMatches.add(matchId);
}

// Unsubscribe from match updates
function unsubscribeFromMatch(matchId) {
    socket.emit('unsubscribe', { match_id: matchId });
    subscribedMatches.delete(matchId);
}

// Handle initial match data
socket.on('match_data', (data) => {
    updateMatchDisplay(data);
    updateEventTimeline(data.events);
});

// Handle match updates
socket.on('match_update', (update) => {
    if (update.type === 'score') {
        updateScore(update.data);
    } else if (update.type === 'status') {
        updateMatchStatus(update.data);
    } else if (update.type === 'time') {
        updateMatchTime(update.data);
    }
});

// Handle new match events
socket.on('match_event', (event) => {
    addEventToTimeline(event);
});

function updateMatchDisplay(matchData) {
    const matchElement = document.getElementById(`match-${matchData.match_id}`);
    if (matchElement) {
        // Update scores
        matchElement.querySelector('.home-score').textContent = matchData.home_score;
        matchElement.querySelector('.away-score').textContent = matchData.away_score;
        
        // Update status and time
        matchElement.querySelector('.match-status').textContent = matchData.status;
        matchElement.querySelector('.match-time').textContent = matchData.time;
    }
}

function updateScore(scoreData) {
    const matchElement = document.getElementById(`match-${scoreData.match_id}`);
    if (matchElement) {
        matchElement.querySelector('.home-score').textContent = scoreData.home_score;
        matchElement.querySelector('.away-score').textContent = scoreData.away_score;
        
        // Add score update animation
        const scoreDisplay = matchElement.querySelector('.score-display');
        scoreDisplay.classList.add('score-updated');
        setTimeout(() => {
            scoreDisplay.classList.remove('score-updated');
        }, 1000);
    }
}

function updateMatchStatus(statusData) {
    const matchElement = document.getElementById(`match-${statusData.match_id}`);
    if (matchElement) {
        const statusElement = matchElement.querySelector('.match-status');
        statusElement.textContent = statusData.status;
        
        // Add status update animation
        statusElement.classList.add('status-updated');
        setTimeout(() => {
            statusElement.classList.remove('status-updated');
        }, 1000);
    }
}

function updateMatchTime(timeData) {
    const matchElement = document.getElementById(`match-${timeData.match_id}`);
    if (matchElement) {
        matchElement.querySelector('.match-time').textContent = timeData.time;
    }
}

function updateEventTimeline(events) {
    const timelineElement = document.getElementById(`timeline-${events[0].match_id}`);
    if (timelineElement) {
        timelineElement.innerHTML = ''; // Clear existing events
        events.forEach(event => {
            addEventToTimeline(event);
        });
    }
}

function addEventToTimeline(event) {
    const timelineElement = document.getElementById(`timeline-${event.match_id}`);
    if (timelineElement) {
        const eventElement = document.createElement('div');
        eventElement.className = `match-event ${event.type.toLowerCase()}`;
        eventElement.innerHTML = `
            <span class="event-time">${event.time}'</span>
            <span class="event-icon">${getEventIcon(event.type)}</span>
            <span class="event-description">${event.description}</span>
        `;
        
        // Add event with animation
        eventElement.style.opacity = '0';
        timelineElement.insertBefore(eventElement, timelineElement.firstChild);
        setTimeout(() => {
            eventElement.style.opacity = '1';
        }, 100);
    }
}

function getEventIcon(eventType) {
    const icons = {
        'GOAL': '⚽',
        'YELLOW_CARD': '🟨',
        'RED_CARD': '🟥',
        'SUBSTITUTION': '🔄',
        'PENALTY': '⚽',
        'ASSIST': '👟'
    };
    return icons[eventType] || '📝';
}

// Initialize matches on page load
document.addEventListener('DOMContentLoaded', () => {
    const matches = document.querySelectorAll('[data-match-id]');
    matches.forEach(match => {
        const matchId = match.dataset.matchId;
        if (match.dataset.status === 'live') {
            subscribeToMatch(matchId);
        }
    });
});
