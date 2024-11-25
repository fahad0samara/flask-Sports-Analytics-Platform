from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class StatsCalculator:
    @staticmethod
    def calculate_team_stats(team, date_from=None, date_to=None):
        """Calculate comprehensive team statistics"""
        try:
            if date_to is None:
                date_to = datetime.utcnow()
            if date_from is None:
                date_from = date_to - timedelta(days=365)  # Last year
                
            # Get matches within date range
            matches = team.home_matches.filter(
                Match.start_time.between(date_from, date_to)
            ).all()
            
            matches.extend(
                team.away_matches.filter(
                    Match.start_time.between(date_from, date_to)
                ).all()
            )
            
            if not matches:
                return {
                    'matches_played': 0,
                    'wins': 0,
                    'draws': 0,
                    'losses': 0,
                    'goals_scored': 0,
                    'goals_conceded': 0,
                    'clean_sheets': 0,
                    'win_rate': 0,
                    'goals_per_game': 0,
                    'conceded_per_game': 0,
                    'points': 0,
                    'form': []
                }
            
            stats = {
                'matches_played': len(matches),
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_scored': 0,
                'goals_conceded': 0,
                'clean_sheets': 0,
                'form': []  # Last 5 matches
            }
            
            # Calculate stats
            for match in matches:
                if match.home_team_id == team.id:
                    stats['goals_scored'] += match.home_score
                    stats['goals_conceded'] += match.away_score
                    
                    if match.away_score == 0:
                        stats['clean_sheets'] += 1
                        
                    if match.home_score > match.away_score:
                        stats['wins'] += 1
                        stats['form'].append('W')
                    elif match.home_score == match.away_score:
                        stats['draws'] += 1
                        stats['form'].append('D')
                    else:
                        stats['losses'] += 1
                        stats['form'].append('L')
                else:
                    stats['goals_scored'] += match.away_score
                    stats['goals_conceded'] += match.home_score
                    
                    if match.home_score == 0:
                        stats['clean_sheets'] += 1
                        
                    if match.away_score > match.home_score:
                        stats['wins'] += 1
                        stats['form'].append('W')
                    elif match.home_score == match.away_score:
                        stats['draws'] += 1
                        stats['form'].append('D')
                    else:
                        stats['losses'] += 1
                        stats['form'].append('L')
            
            # Calculate derived stats
            stats['win_rate'] = (stats['wins'] / stats['matches_played']) * 100
            stats['goals_per_game'] = stats['goals_scored'] / stats['matches_played']
            stats['conceded_per_game'] = stats['goals_conceded'] / stats['matches_played']
            stats['points'] = (stats['wins'] * 3) + stats['draws']
            
            # Keep only last 5 matches for form
            stats['form'] = stats['form'][-5:]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating team stats: {str(e)}")
            return None
    
    @staticmethod
    def calculate_player_stats(player, date_from=None, date_to=None):
        """Calculate comprehensive player statistics"""
        try:
            if date_to is None:
                date_to = datetime.utcnow()
            if date_from is None:
                date_from = date_to - timedelta(days=365)  # Last year
                
            # Get player statistics within date range
            stats_records = player.statistics.filter(
                PlayerStatistics.match.has(
                    Match.start_time.between(date_from, date_to)
                )
            ).all()
            
            if not stats_records:
                return {
                    'matches_played': 0,
                    'minutes_played': 0,
                    'goals': 0,
                    'assists': 0,
                    'shots': 0,
                    'shots_on_target': 0,
                    'passes': 0,
                    'pass_accuracy': 0,
                    'tackles': 0,
                    'interceptions': 0,
                    'fouls': 0,
                    'yellow_cards': 0,
                    'red_cards': 0,
                    'goals_per_90': 0,
                    'assists_per_90': 0,
                    'shot_accuracy': 0
                }
            
            # Aggregate stats
            stats = defaultdict(int)
            for record in stats_records:
                stats['matches_played'] += 1
                stats['minutes_played'] += record.minutes_played
                stats['goals'] += record.goals
                stats['assists'] += record.assists
                stats['shots'] += record.shots
                stats['shots_on_target'] += record.shots_on_target
                stats['passes'] += record.passes
                stats['pass_accuracy'] += record.pass_accuracy
                stats['tackles'] += record.tackles
                stats['interceptions'] += record.interceptions
                stats['fouls'] += record.fouls
                stats['yellow_cards'] += record.yellow_cards
                stats['red_cards'] += record.red_cards
            
            # Calculate averages and derived stats
            stats['pass_accuracy'] = stats['pass_accuracy'] / stats['matches_played']
            stats['goals_per_90'] = (stats['goals'] / stats['minutes_played']) * 90
            stats['assists_per_90'] = (stats['assists'] / stats['minutes_played']) * 90
            
            if stats['shots'] > 0:
                stats['shot_accuracy'] = (stats['shots_on_target'] / stats['shots']) * 100
            else:
                stats['shot_accuracy'] = 0
            
            return dict(stats)
            
        except Exception as e:
            logger.error(f"Error calculating player stats: {str(e)}")
            return None
    
    @staticmethod
    def calculate_head_to_head(team1, team2, limit=10):
        """Calculate head-to-head statistics between two teams"""
        try:
            # Get matches between the two teams
            matches = Match.query.filter(
                ((Match.home_team_id == team1.id) & (Match.away_team_id == team2.id)) |
                ((Match.home_team_id == team2.id) & (Match.away_team_id == team1.id))
            ).order_by(Match.start_time.desc()).limit(limit).all()
            
            if not matches:
                return {
                    'matches_played': 0,
                    'team1_wins': 0,
                    'team2_wins': 0,
                    'draws': 0,
                    'team1_goals': 0,
                    'team2_goals': 0,
                    'recent_matches': []
                }
            
            stats = {
                'matches_played': len(matches),
                'team1_wins': 0,
                'team2_wins': 0,
                'draws': 0,
                'team1_goals': 0,
                'team2_goals': 0,
                'recent_matches': []
            }
            
            for match in matches:
                if match.home_team_id == team1.id:
                    stats['team1_goals'] += match.home_score
                    stats['team2_goals'] += match.away_score
                    
                    if match.home_score > match.away_score:
                        stats['team1_wins'] += 1
                    elif match.home_score < match.away_score:
                        stats['team2_wins'] += 1
                    else:
                        stats['draws'] += 1
                else:
                    stats['team1_goals'] += match.away_score
                    stats['team2_goals'] += match.home_score
                    
                    if match.away_score > match.home_score:
                        stats['team1_wins'] += 1
                    elif match.away_score < match.home_score:
                        stats['team2_wins'] += 1
                    else:
                        stats['draws'] += 1
                
                # Add to recent matches
                stats['recent_matches'].append({
                    'date': match.start_time,
                    'home_team': match.home_team.name,
                    'away_team': match.away_team.name,
                    'score': f"{match.home_score}-{match.away_score}"
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating head-to-head stats: {str(e)}")
            return None
