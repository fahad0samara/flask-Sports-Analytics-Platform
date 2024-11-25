// Match Detail Advanced Features

class MatchDetailManager {
    constructor() {
        this.matchId = document.querySelector('meta[name="match-id"]').content;
        this.setupEventListeners();
        this.initializeComponents();
    }

    setupEventListeners() {
        // Real-time updates
        if (document.querySelector('.match-status-live')) {
            this.startLiveUpdates();
        }

        // Initialize interactive components
        document.querySelectorAll('[data-toggle="tooltip"]').forEach(el => {
            new bootstrap.Tooltip(el);
        });
    }

    initializeComponents() {
        this.initializeTimeline();
        this.initializeHeatmap();
        this.initializePlayerCards();
        this.initializeHeadToHead();
        this.initializeAdvancedStats();
    }

    // Real-time Updates
    startLiveUpdates() {
        this.updateInterval = setInterval(() => this.fetchMatchUpdates(), 30000);
    }

    async fetchMatchUpdates() {
        try {
            const response = await fetch(`/api/matches/${this.matchId}/live`);
            const data = await response.json();
            this.updateMatchData(data);
        } catch (error) {
            console.error('Error fetching match updates:', error);
        }
    }

    updateMatchData(data) {
        // Update score
        document.querySelector('.home-score').textContent = data.home_score;
        document.querySelector('.away-score').textContent = data.away_score;
        
        // Update match time
        document.querySelector('.match-time').textContent = data.match_time;
        
        // Update statistics
        this.updateStatistics(data.statistics);
        
        // Update timeline
        this.updateTimeline(data.events);
    }

    // Match Timeline
    initializeTimeline() {
        this.timeline = document.getElementById('match-timeline');
        if (!this.timeline) return;

        this.timelineChart = new Chart(this.timeline.getContext('2d'), {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Match Events',
                    data: []
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        min: 0,
                        max: 90,
                        title: {
                            display: true,
                            text: 'Match Time (minutes)'
                        }
                    },
                    y: {
                        type: 'category',
                        labels: ['Goal', 'Yellow Card', 'Red Card', 'Substitution']
                    }
                }
            }
        });
    }

    updateTimeline(events) {
        if (!this.timelineChart) return;

        const timelineData = events.map(event => ({
            x: event.minute,
            y: event.type,
            team: event.team,
            player: event.player
        }));

        this.timelineChart.data.datasets[0].data = timelineData;
        this.timelineChart.update();
    }

    // Heat Map
    initializeHeatmap() {
        const heatmapContainer = document.getElementById('match-heatmap');
        if (!heatmapContainer) return;

        this.heatmap = h337.create({
            container: heatmapContainer,
            radius: 40,
            maxOpacity: 0.6,
            minOpacity: 0,
            blur: 0.75
        });

        this.updateHeatmap();
    }

    async updateHeatmap() {
        try {
            const response = await fetch(`/api/matches/${this.matchId}/heatmap`);
            const data = await response.json();
            
            this.heatmap.setData({
                max: data.max,
                data: data.points
            });
        } catch (error) {
            console.error('Error updating heatmap:', error);
        }
    }

    // Player Performance Cards
    initializePlayerCards() {
        document.querySelectorAll('.player-card').forEach(card => {
            card.addEventListener('click', () => this.showPlayerDetails(card.dataset.playerId));
        });
    }

    async showPlayerDetails(playerId) {
        try {
            const response = await fetch(`/api/players/${playerId}/stats`);
            const data = await response.json();
            
            const modal = new bootstrap.Modal(document.getElementById('player-modal'));
            this.updatePlayerModal(data);
            modal.show();
        } catch (error) {
            console.error('Error fetching player details:', error);
        }
    }

    updatePlayerModal(data) {
        const modal = document.getElementById('player-modal');
        modal.querySelector('.player-name').textContent = data.name;
        modal.querySelector('.player-position').textContent = data.position;
        
        // Update player statistics
        this.updatePlayerStats(data.statistics);
        
        // Update performance chart
        this.updatePlayerPerformanceChart(data.performance);
    }

    // Head to Head Comparison
    initializeHeadToHead() {
        const h2hContainer = document.getElementById('head-to-head');
        if (!h2hContainer) return;

        this.loadHeadToHeadData();
    }

    async loadHeadToHeadData() {
        try {
            const response = await fetch(`/api/matches/${this.matchId}/head-to-head`);
            const data = await response.json();
            
            this.updateHeadToHeadStats(data);
            this.createHeadToHeadChart(data.history);
        } catch (error) {
            console.error('Error loading head to head data:', error);
        }
    }

    // Advanced Statistics
    initializeAdvancedStats() {
        const statsContainer = document.getElementById('advanced-stats');
        if (!statsContainer) return;

        this.loadAdvancedStats();
    }

    async loadAdvancedStats() {
        try {
            const response = await fetch(`/api/matches/${this.matchId}/advanced-stats`);
            const data = await response.json();
            
            this.updateAdvancedStats(data);
            this.createAdvancedStatsCharts(data);
        } catch (error) {
            console.error('Error loading advanced statistics:', error);
        }
    }

    updateAdvancedStats(data) {
        // Update possession stats
        this.updatePossessionMap(data.possession);
        
        // Update pass accuracy
        this.updatePassingStats(data.passing);
        
        // Update shot analysis
        this.updateShotAnalysis(data.shots);
    }

    createAdvancedStatsCharts(data) {
        // Create radar chart for team comparison
        this.createTeamComparisonChart(data.teamComparison);
        
        // Create shot map
        this.createShotMap(data.shots);
        
        // Create passing network
        this.createPassingNetwork(data.passing);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MatchDetailManager();
});
