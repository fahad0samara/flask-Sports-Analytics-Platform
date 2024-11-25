import requests
import logging
from datetime import datetime, timedelta
from app.models import Match, Team, Sport, PlayerStatistics
from app import db

logger = logging.getLogger(__name__)

class LiveMatchTracker:
    def __init__(self):
        self.api_key = None  # Set this from environment variable
        self.base_url = "https://api.sportsdataapi.com/v1"
        self.sport_api_mappings = {
            'football': 'soccer',
            'basketball': 'basketball',
            'cricket': 'cricket'
        }

    def update_live_matches(self):
        """Update all currently live matches"""
        try:
            # Get all matches that are currently live
            live_matches = Match.query.filter_by(status='live').all()
            
            for match in live_matches:
                self._update_match_data(match)
                
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating live matches: {str(e)}")
            return False
    
    def _update_match_data(self, match):
        """Update data for a single match"""
        try:
            sport_api = self.sport_api_mappings.get(match.sport.name.lower())
            if not sport_api:
                logger.warning(f"No API mapping for sport: {match.sport.name}")
                return
            
            # Get match data from API
            response = self._fetch_match_data(sport_api, match.id)
            if not response:
                return
            
            # Update match score
            match.home_score = response['home_score']
            match.away_score = response['away_score']
            
            # Update match status if needed
            if response['status'] == 'completed':
                match.status = 'completed'
                match.winner_id = (
                    match.home_team_id if match.home_score > match.away_score
                    else match.away_team_id if match.away_score > match.home_score
                    else None
                )
            
            # Update player statistics
            self._update_player_stats(match, response.get('player_stats', []))
            
        except Exception as e:
            logger.error(f"Error updating match {match.id}: {str(e)}")
    
    def _fetch_match_data(self, sport, match_id):
        """Fetch match data from the sports data API"""
        try:
            if not self.api_key:
                logger.error("No API key configured")
                return None
            
            url = f"{self.base_url}/{sport}/matches/{match_id}/live"
            headers = {'apikey': self.api_key}
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code}")
                return None
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching match data: {str(e)}")
            return None
    
    def _update_player_stats(self, match, player_stats):
        """Update player statistics for a match"""
        try:
            for stat in player_stats:
                player_stat = PlayerStatistics.query.filter_by(
                    match_id=match.id,
                    player_id=stat['player_id']
                ).first()
                
                if not player_stat:
                    continue
                
                # Update statistics based on sport
                if match.sport.name.lower() == 'football':
                    self._update_football_stats(player_stat, stat)
                elif match.sport.name.lower() == 'basketball':
                    self._update_basketball_stats(player_stat, stat)
                elif match.sport.name.lower() == 'cricket':
                    self._update_cricket_stats(player_stat, stat)
                
        except Exception as e:
            logger.error(f"Error updating player stats: {str(e)}")
    
    def _update_football_stats(self, player_stat, stat_data):
        """Update football-specific player statistics"""
        player_stat.minutes_played = stat_data.get('minutes_played', 0)
        player_stat.goals = stat_data.get('goals', 0)
        player_stat.assists = stat_data.get('assists', 0)
        player_stat.shots = stat_data.get('shots', 0)
        player_stat.shots_on_target = stat_data.get('shots_on_target', 0)
        player_stat.passes = stat_data.get('passes', 0)
        player_stat.pass_accuracy = stat_data.get('pass_accuracy', 0)
        player_stat.tackles = stat_data.get('tackles', 0)
        player_stat.interceptions = stat_data.get('interceptions', 0)
        player_stat.fouls = stat_data.get('fouls', 0)
        player_stat.yellow_cards = stat_data.get('yellow_cards', 0)
        player_stat.red_cards = stat_data.get('red_cards', 0)
    
    def _update_basketball_stats(self, player_stat, stat_data):
        """Update basketball-specific player statistics"""
        player_stat.minutes_played = stat_data.get('minutes_played', 0)
        player_stat.points = stat_data.get('points', 0)
        player_stat.rebounds = stat_data.get('rebounds', 0)
        player_stat.assists = stat_data.get('assists', 0)
        player_stat.steals = stat_data.get('steals', 0)
        player_stat.blocks = stat_data.get('blocks', 0)
        player_stat.turnovers = stat_data.get('turnovers', 0)
        player_stat.fouls = stat_data.get('fouls', 0)
        player_stat.field_goals_made = stat_data.get('field_goals_made', 0)
        player_stat.field_goals_attempted = stat_data.get('field_goals_attempted', 0)
        player_stat.three_pointers_made = stat_data.get('three_pointers_made', 0)
        player_stat.three_pointers_attempted = stat_data.get('three_pointers_attempted', 0)
        player_stat.free_throws_made = stat_data.get('free_throws_made', 0)
        player_stat.free_throws_attempted = stat_data.get('free_throws_attempted', 0)
    
    def _update_cricket_stats(self, player_stat, stat_data):
        """Update cricket-specific player statistics"""
        player_stat.runs = stat_data.get('runs', 0)
        player_stat.balls_faced = stat_data.get('balls_faced', 0)
        player_stat.fours = stat_data.get('fours', 0)
        player_stat.sixes = stat_data.get('sixes', 0)
        player_stat.strike_rate = stat_data.get('strike_rate', 0)
        player_stat.overs_bowled = stat_data.get('overs_bowled', 0)
        player_stat.maidens = stat_data.get('maidens', 0)
        player_stat.wickets = stat_data.get('wickets', 0)
        player_stat.runs_conceded = stat_data.get('runs_conceded', 0)
        player_stat.economy_rate = stat_data.get('economy_rate', 0)
        player_stat.catches = stat_data.get('catches', 0)
        player_stat.stumpings = stat_data.get('stumpings', 0)
        player_stat.run_outs = stat_data.get('run_outs', 0)
