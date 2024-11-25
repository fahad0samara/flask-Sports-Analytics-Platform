"""Helper functions for the sports analytics platform"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import func
from app.models import Match, Team, Sport, Prediction, User, League

def get_featured_matches(limit: int = 6) -> List[Match]:
    """Get featured matches (live and upcoming)"""
    now = datetime.utcnow()
    return Match.query.filter(
        Match.start_time >= now - timedelta(hours=2),
        Match.status.in_(['scheduled', 'live'])
    ).order_by(Match.start_time).limit(limit).all()

def get_recent_predictions(limit: int = 5) -> List[Dict]:
    """Get recent predictions with match details"""
    predictions = Prediction.query.order_by(
        Prediction.created_at.desc()
    ).limit(limit).all()
    
    return [{
        'id': pred.id,
        'match': pred.match,
        'predicted_winner': pred.predicted_winner,
        'confidence': pred.confidence,
        'is_correct': pred.is_correct,
        'created_at': pred.created_at
    } for pred in predictions]

def get_trending_news(limit: int = 5) -> List[Dict]:
    """Get trending sports news"""
    from app.utils.api_integrations import SportsDataAggregator
    aggregator = SportsDataAggregator()
    return aggregator.get_sports_news(limit=limit)

def get_top_leagues(limit: int = 5) -> List[Dict]:
    """Get top leagues with match counts"""
    return League.query.join(Match).group_by(League.id).order_by(
        func.count(Match.id).desc()
    ).limit(limit).all()

def get_latest_news(limit: int = 5) -> List[Dict]:
    """Get latest sports news from all providers"""
    from app.utils.api_integrations import SportsDataAggregator
    aggregator = SportsDataAggregator()
    return aggregator.get_sports_news(limit=limit)
