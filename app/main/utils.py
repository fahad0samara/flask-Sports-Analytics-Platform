"""Utility functions for the main blueprint."""
from datetime import datetime, timedelta
import random

def calculate_match_predictions(match):
    """Calculate predictions for a match based on team performance."""
    # This is a placeholder implementation
    # In a real application, this would use machine learning models
    # trained on historical match data
    
    # Generate random probabilities for demo
    home_prob = random.uniform(0.3, 0.7)
    away_prob = 1 - home_prob
    
    # Calculate other predictions
    total_goals = random.randint(1, 5)
    possession_home = random.randint(40, 60)
    shots = random.randint(15, 25)
    
    return {
        'home_win_probability': round(home_prob * 100),
        'away_win_probability': round(away_prob * 100),
        'total_goals_prediction': total_goals,
        'possession_home': possession_home,
        'shots_prediction': shots
    }

def prediction_confidence(match):
    """Determine the confidence level of match predictions."""
    # This is a placeholder implementation
    # In a real application, this would be based on:
    # - Amount and quality of historical data
    # - Model confidence scores
    # - Recent form of teams
    # - Head-to-head history
    # - etc.
    
    # For demo purposes, base confidence on match proximity
    days_until_match = (match.start_time - datetime.utcnow()).days
    
    if days_until_match <= 3:
        return 'high'
    elif days_until_match <= 7:
        return 'medium'
    else:
        return 'low'

def calculate_team_form(team, num_matches=5):
    """Calculate team's recent form based on last N matches."""
    # This would typically analyze recent match results
    # and return a form rating (e.g., 1-10)
    return random.randint(5, 10)  # Placeholder implementation

def calculate_head_to_head(team1, team2):
    """Calculate head-to-head statistics between two teams."""
    # This would analyze historical matches between the teams
    # and return relevant statistics
    return {
        'total_matches': random.randint(5, 15),
        'team1_wins': random.randint(2, 8),
        'team2_wins': random.randint(2, 8),
        'draws': random.randint(1, 5)
    }

def calculate_league_position_trend(team):
    """Calculate team's league position trend over time."""
    # This would analyze how the team's league position
    # has changed over recent weeks/months
    return random.choice(['rising', 'falling', 'stable'])

def get_injury_report(team):
    """Get current injury report for a team."""
    # This would typically fetch current injury data
    # from a reliable sports data provider
    return {
        'total_injuries': random.randint(0, 4),
        'key_players_injured': random.randint(0, 2)
    }

def calculate_goal_statistics(team):
    """Calculate detailed goal statistics for a team."""
    return {
        'goals_scored': random.randint(20, 50),
        'goals_conceded': random.randint(15, 40),
        'clean_sheets': random.randint(5, 15),
        'failed_to_score': random.randint(2, 8)
    }

def get_weather_impact(match):
    """Assess potential weather impact on the match."""
    # This would typically fetch weather forecast data
    # and assess its potential impact on the game
    conditions = ['clear', 'rain', 'wind', 'snow']
    return {
        'condition': random.choice(conditions),
        'impact_level': random.choice(['low', 'medium', 'high'])
    }

def calculate_fatigue_factor(team):
    """Calculate team fatigue based on recent schedule."""
    # This would analyze:
    # - Days since last match
    # - Number of matches in recent period
    # - Travel distance
    return random.choice(['low', 'medium', 'high'])

def get_referee_statistics(referee):
    """Get referee statistics and tendencies."""
    return {
        'matches_officiated': random.randint(50, 200),
        'avg_yellow_cards': round(random.uniform(2.0, 4.0), 1),
        'avg_red_cards': round(random.uniform(0.1, 0.3), 2),
        'avg_penalties': round(random.uniform(0.2, 0.4), 2)
    }
