import numpy as np
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MatchPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.features = [
            'home_team_form',
            'away_team_form',
            'home_team_goals_scored',
            'away_team_goals_scored',
            'home_team_goals_conceded',
            'away_team_goals_conceded',
            'home_advantage'
        ]
    
    def train(self, matches):
        """Train the prediction model using historical match data"""
        try:
            X = []  # Features
            y = []  # Target (1: home win, 0: draw, -1: away win)
            
            for match in matches:
                if match.status != 'completed':
                    continue
                
                # Get team stats from the last 5 matches before this match
                home_stats = self._get_team_stats(match.home_team, match.start_time)
                away_stats = self._get_team_stats(match.away_team, match.start_time)
                
                # Create feature vector
                features = [
                    home_stats['form'],
                    away_stats['form'],
                    home_stats['goals_scored'],
                    away_stats['goals_scored'],
                    home_stats['goals_conceded'],
                    away_stats['goals_conceded'],
                    1.0  # Home advantage
                ]
                
                X.append(features)
                
                # Determine match result
                if match.home_score > match.away_score:
                    result = 1  # Home win
                elif match.home_score < match.away_score:
                    result = -1  # Away win
                else:
                    result = 0  # Draw
                
                y.append(result)
            
            if X and y:
                X = np.array(X)
                y = np.array(y)
                self.model.fit(X, y)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return False
    
    def predict(self, match):
        """Predict the outcome of a match"""
        try:
            # Get team stats
            home_stats = self._get_team_stats(match.home_team)
            away_stats = self._get_team_stats(match.away_team)
            
            # Create feature vector
            features = [
                home_stats['form'],
                away_stats['form'],
                home_stats['goals_scored'],
                away_stats['goals_scored'],
                home_stats['goals_conceded'],
                away_stats['goals_conceded'],
                1.0  # Home advantage
            ]
            
            # Make prediction
            features = np.array(features).reshape(1, -1)
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            
            return {
                'prediction': prediction,  # 1: home win, 0: draw, -1: away win
                'home_win_prob': probabilities[2],
                'draw_prob': probabilities[1],
                'away_win_prob': probabilities[0],
                'confidence': max(probabilities)
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return None
    
    def _get_team_stats(self, team, before_date=None):
        """Calculate team statistics from recent matches"""
        try:
            if before_date is None:
                before_date = datetime.utcnow()
            
            # Get last 5 matches before the given date
            matches = team.home_matches.filter(
                Match.start_time < before_date
            ).order_by(Match.start_time.desc()).limit(5).all()
            
            matches.extend(
                team.away_matches.filter(
                    Match.start_time < before_date
                ).order_by(Match.start_time.desc()).limit(5).all()
            )
            
            matches.sort(key=lambda x: x.start_time, reverse=True)
            matches = matches[:5]
            
            if not matches:
                return {
                    'form': 0.5,
                    'goals_scored': 0,
                    'goals_conceded': 0
                }
            
            # Calculate stats
            form = 0
            goals_scored = 0
            goals_conceded = 0
            
            for match in matches:
                if match.home_team_id == team.id:
                    goals_scored += match.home_score
                    goals_conceded += match.away_score
                    if match.home_score > match.away_score:
                        form += 1.0
                    elif match.home_score == match.away_score:
                        form += 0.5
                else:
                    goals_scored += match.away_score
                    goals_conceded += match.home_score
                    if match.away_score > match.home_score:
                        form += 1.0
                    elif match.home_score == match.away_score:
                        form += 0.5
            
            num_matches = len(matches)
            return {
                'form': form / num_matches,
                'goals_scored': goals_scored / num_matches,
                'goals_conceded': goals_conceded / num_matches
            }
            
        except Exception as e:
            logger.error(f"Error calculating team stats: {str(e)}")
            return {
                'form': 0.5,
                'goals_scored': 0,
                'goals_conceded': 0
            }
