import os
import requests
from datetime import datetime
import logging
from typing import Dict, List, Optional
from flask import current_app

logger = logging.getLogger(__name__)

class SportsDataProvider:
    """Base class for sports data providers"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = ""
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request to API endpoint"""
        try:
            headers = {'apikey': self.api_key}
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            return None

class ApiFootball(SportsDataProvider):
    """API-Football integration (api-football.com)"""
    def __init__(self):
        super().__init__(current_app.config.get('API_FOOTBALL_KEY'))
        self.base_url = "https://api-football-v1.p.rapidapi.com/v3"
        self.headers = {
            'x-rapidapi-host': 'api-football-v1.p.rapidapi.com',
            'x-rapidapi-key': self.api_key
        }
    
    def get_live_matches(self) -> List[Dict]:
        """Get all live football matches"""
        try:
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={'live': 'all'}
            )
            response.raise_for_status()
            data = response.json()
            
            matches = []
            for match in data.get('response', []):
                matches.append({
                    'home_team': match['teams']['home']['name'],
                    'away_team': match['teams']['away']['name'],
                    'home_score': match['goals']['home'],
                    'away_score': match['goals']['away'],
                    'status': match['fixture']['status']['short'],
                    'league': match['league']['name'],
                    'time': match['fixture']['status']['elapsed']
                })
            return matches
        except Exception as e:
            logger.error(f"Failed to get live matches: {str(e)}")
            return []

class TheSportsDB(SportsDataProvider):
    """TheSportsDB integration (thesportsdb.com)"""
    def __init__(self):
        super().__init__(current_app.config.get('SPORTS_DB_KEY'))
        self.base_url = "https://www.thesportsdb.com/api/v1/json/3"
    
    def get_live_scores(self) -> List[Dict]:
        """Get live scores across multiple sports"""
        try:
            response = requests.get(f"{self.base_url}/livescore.php")
            response.raise_for_status()
            data = response.json()
            
            scores = []
            for event in data.get('events', []):
                scores.append({
                    'sport': event['strSport'],
                    'home_team': event['strHomeTeam'],
                    'away_team': event['strAwayTeam'],
                    'home_score': event['intHomeScore'],
                    'away_score': event['intAwayScore'],
                    'status': event['strStatus'],
                    'league': event['strLeague'],
                    'time': event['strTime']
                })
            return scores
        except Exception as e:
            logger.error(f"Failed to get live scores: {str(e)}")
            return []
    
    def search_teams(self, team_name: str) -> List[Dict]:
        """Search for teams across all sports"""
        try:
            response = requests.get(
                f"{self.base_url}/searchteams.php",
                params={'t': team_name}
            )
            response.raise_for_status()
            return response.json().get('teams', [])
        except Exception as e:
            logger.error(f"Failed to search teams: {str(e)}")
            return []

class ESPN(SportsDataProvider):
    """ESPN API integration"""
    def __init__(self):
        super().__init__(current_app.config.get('ESPN_API_KEY'))
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports"
    
    def get_scores(self, sport: str, league: str) -> List[Dict]:
        """Get scores for a specific sport and league"""
        try:
            response = requests.get(
                f"{self.base_url}/{sport}/{league}/scoreboard"
            )
            response.raise_for_status()
            return response.json().get('events', [])
        except Exception as e:
            logger.error(f"Failed to get scores: {str(e)}")
            return []
    
    def get_news(self, sport: str = None) -> List[Dict]:
        """Get latest news for a specific sport"""
        try:
            url = f"{self.base_url}/{sport}/news" if sport else f"{self.base_url}/news"
            response = requests.get(url)
            response.raise_for_status()
            return response.json().get('articles', [])
        except Exception as e:
            logger.error(f"Failed to get news: {str(e)}")
            return []

class SportsDataAggregator:
    """Aggregates data from multiple sports data providers"""
    def __init__(self):
        self.api_football = ApiFootball()
        self.sports_db = TheSportsDB()
        self.espn = ESPN()
    
    def get_all_live_scores(self) -> List[Dict]:
        """Get live scores from all providers"""
        scores = []
        scores.extend(self.api_football.get_live_matches())
        scores.extend(self.sports_db.get_live_scores())
        return scores
    
    def get_team_data(self, team_name: str) -> Dict:
        """Get comprehensive team data"""
        return self.sports_db.search_teams(team_name)
    
    def get_sports_news(self, limit: int = 5) -> List[Dict]:
        """Get sports news from all providers"""
        all_news = []
        
        # Get news from ESPN
        espn_news = self.espn.get_news()
        for article in espn_news:
            all_news.append({
                'title': article.get('headline'),
                'content': article.get('description'),
                'date': datetime.strptime(article.get('published'), "%Y-%m-%dT%H:%M:%SZ"),
                'source': 'ESPN',
                'category': article.get('category', {}).get('name', 'Sports'),
                'image_url': article.get('images', [{}])[0].get('url') if article.get('images') else None
            })
        
        # Sort by date and limit
        all_news.sort(key=lambda x: x['date'], reverse=True)
        return all_news[:limit]
