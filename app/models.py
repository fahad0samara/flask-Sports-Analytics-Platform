from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import func, case
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    avatar_url = db.Column(db.String(200))
    
    # Relationships
    predictions = db.relationship('Prediction', back_populates='user', lazy='dynamic',
                                cascade='all, delete-orphan')
    analyses = db.relationship('Analysis', back_populates='user', lazy='dynamic',
                             cascade='all, delete-orphan')
    favorite_teams = db.relationship('Team', secondary='user_favorite_teams',
                                   back_populates='fans', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_statistics(self):
        """Get comprehensive user statistics"""
        try:
            # Basic prediction stats
            total_predictions = self.predictions.count()
            correct_predictions = self.predictions.filter_by(is_correct=True).count()
            accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
            
            # Current streak
            predictions_ordered = self.predictions.order_by(Prediction.created_at.desc()).limit(10).all()
            current_streak = 0
            for pred in predictions_ordered:
                if pred.is_correct:
                    current_streak += 1
                else:
                    break
            
            # Sport-specific stats
            sport_stats = db.session.query(
                Sport.name,
                func.count(Prediction.id).label('total'),
                func.sum(case([(Prediction.is_correct == True, 1)], else_=0)).label('correct')
            ).join(Match).join(Sport)\
             .filter(Prediction.user_id == self.id)\
             .group_by(Sport.name)\
             .all()
            
            # Format sport stats
            sport_stats = [{
                'name': name,
                'total': total,
                'correct': correct,
                'accuracy': (correct / total * 100) if total > 0 else 0
            } for name, total, correct in sport_stats]
            
            # Analysis stats
            total_analyses = self.analyses.count()
            total_likes = db.session.query(func.sum(Analysis.likes))\
                .filter(Analysis.user_id == self.id)\
                .scalar() or 0
            
            return {
                'total_predictions': total_predictions,
                'correct_predictions': correct_predictions,
                'accuracy': accuracy,
                'current_streak': current_streak,
                'sport_stats': sport_stats,
                'total_analyses': total_analyses,
                'total_likes': total_likes
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error getting user statistics: {str(e)}")
            return {
                'total_predictions': 0,
                'correct_predictions': 0,
                'accuracy': 0,
                'current_streak': 0,
                'sport_stats': [],
                'total_analyses': 0,
                'total_likes': 0
            }
    
    def __repr__(self):
        return f'<User {self.username}>'

class Sport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    icon = db.Column(db.String(64))  # FontAwesome icon name
    teams = db.relationship('Team', back_populates='sport', lazy='dynamic')
    leagues = db.relationship('League', back_populates='sport')
    news_items = db.relationship('News', back_populates='sport_ref', lazy='dynamic')
    matches = db.relationship('Match', back_populates='sport', lazy='dynamic')

    def __repr__(self):
        return f'<Sport {self.name}>'

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey('sport.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), nullable=False)
    players = db.relationship('Player', back_populates='team', lazy='dynamic')
    logo_url = db.Column(db.String(200))  # URL to team logo
    sport = db.relationship('Sport', back_populates='teams')
    league = db.relationship('League', back_populates='teams')
    home_matches = db.relationship('Match', back_populates='home_team', foreign_keys='Match.home_team_id', lazy='dynamic')
    away_matches = db.relationship('Match', back_populates='away_team', foreign_keys='Match.away_team_id', lazy='dynamic')
    won_matches = db.relationship('Match', back_populates='winner', foreign_keys='Match.winner_id', lazy='dynamic')
    fans = db.relationship('User', secondary='user_favorite_teams',
                          back_populates='favorite_teams', lazy='dynamic')

    def __repr__(self):
        return f'<Team {self.name}>'

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    statistics = db.relationship('PlayerStatistics', back_populates='player', lazy='dynamic')
    team = db.relationship('Team', back_populates='players')

class Match(db.Model):
    """Match model representing a sports match"""
    
    # Status constants
    STATUS_SCHEDULED = 'scheduled'
    STATUS_LIVE = 'live'
    STATUS_FINISHED = 'finished'
    STATUS_POSTPONED = 'postponed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_SUSPENDED = 'suspended'
    STATUS_INTERRUPTED = 'interrupted'
    
    VALID_STATUSES = [
        STATUS_SCHEDULED,
        STATUS_LIVE,
        STATUS_FINISHED,
        STATUS_POSTPONED,
        STATUS_CANCELLED,
        STATUS_SUSPENDED,
        STATUS_INTERRUPTED
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='CASCADE'), nullable=False, index=True)
    away_team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='CASCADE'), nullable=False, index=True)
    sport_id = db.Column(db.Integer, db.ForeignKey('sport.id', ondelete='CASCADE'), nullable=False, index=True)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id', ondelete='CASCADE'), nullable=False, index=True)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(20), default=STATUS_SCHEDULED, index=True)
    home_score = db.Column(db.Integer, default=0)
    away_score = db.Column(db.Integer, default=0)
    winner_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='SET NULL'))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    predictions = db.relationship('Prediction', back_populates='match', lazy='dynamic',
                                cascade='all, delete-orphan')
    home_team = db.relationship('Team', back_populates='home_matches', foreign_keys=[home_team_id])
    away_team = db.relationship('Team', back_populates='away_matches', foreign_keys=[away_team_id])
    sport = db.relationship('Sport', back_populates='matches', foreign_keys=[sport_id])
    league = db.relationship('League', back_populates='matches', foreign_keys=[league_id])
    winner = db.relationship('Team', back_populates='won_matches', foreign_keys=[winner_id])
    player_statistics = db.relationship('PlayerStatistics', back_populates='match', lazy='dynamic',
                                      cascade='all, delete-orphan')
    analyses = db.relationship('Analysis', back_populates='match', lazy='dynamic',
                             cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super(Match, self).__init__(*args, **kwargs)
        self.validate_status()
        self.validate_teams()
    
    def validate_status(self):
        """Validate match status"""
        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid match status: {self.status}")
    
    def validate_teams(self):
        """Validate that home and away teams are different"""
        if self.home_team_id == self.away_team_id:
            raise ValueError("Home and away teams cannot be the same")
    
    def update_score(self, home_score, away_score):
        """Update match score with validation"""
        if not isinstance(home_score, int) or not isinstance(away_score, int):
            raise ValueError("Scores must be integers")
        if home_score < 0 or away_score < 0:
            raise ValueError("Scores cannot be negative")
        
        self.home_score = home_score
        self.away_score = away_score
        self.last_updated = datetime.utcnow()
        
        # Update winner if match is finished
        if self.status == self.STATUS_FINISHED:
            if home_score > away_score:
                self.winner_id = self.home_team_id
            elif away_score > home_score:
                self.winner_id = self.away_team_id
            else:
                self.winner_id = None

    def get_time_status(self):
        """Get a human-readable time status"""
        if self.status == self.STATUS_LIVE:
            minutes = int((datetime.utcnow() - self.start_time).total_seconds() / 60)
            return f"{minutes}'"
        elif self.status == self.STATUS_FINISHED:
            return "Finished"
        elif self.status == self.STATUS_SCHEDULED:
            if self.start_time.date() == datetime.utcnow().date():
                return self.start_time.strftime('%H:%M')
            return self.start_time.strftime('%d %b, %H:%M')
        return self.status.capitalize()

    def to_dict(self):
        """Convert match to dictionary"""
        return {
            'id': self.id,
            'home_team': self.home_team.name,
            'away_team': self.away_team.name,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'status': self.status,
            'start_time': self.start_time.isoformat(),
            'sport': self.sport.name,
            'league': self.league.name
        }
    
    def get_winner(self):
        """Get the winning team of the match"""
        if self.status != self.STATUS_FINISHED:
            return None
        if self.home_score > self.away_score:
            return self.home_team
        elif self.away_score > self.home_score:
            return self.away_team
        return None
    
    def get_score_display(self):
        """Get a formatted score string"""
        return f"{self.home_score} - {self.away_score}"
    
    def get_prediction_stats(self):
        """Get prediction statistics for this match"""
        total = self.predictions.count()
        if total == 0:
            return {'total': 0, 'home': 0, 'away': 0, 'home_percentage': 0, 'away_percentage': 0}
        
        home_predictions = self.predictions.filter_by(predicted_winner_id=self.home_team_id).count()
        away_predictions = total - home_predictions
        
        return {
            'total': total,
            'home': home_predictions,
            'away': away_predictions,
            'home_percentage': round((home_predictions / total) * 100, 1),
            'away_percentage': round((away_predictions / total) * 100, 1)
        }
    
    def get_match_stats(self):
        """Get detailed match statistics"""
        return {
            'id': self.id,
            'home_team': self.home_team.name,
            'away_team': self.away_team.name,
            'sport': self.sport.name,
            'league': self.league.name,
            'start_time': self.start_time.isoformat(),
            'status': self.status,
            'score': self.get_score_display(),
            'winner': self.get_winner().name if self.get_winner() else None,
            'predictions': self.get_prediction_stats(),
            'last_updated': self.last_updated.isoformat()
        }
    
    def __repr__(self):
        return f'<Match {self.home_team.name} vs {self.away_team.name}>'

class League(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey('sport.id'), nullable=False)
    country = db.Column(db.String(64), nullable=False)
    logo_url = db.Column(db.String(200))  # URL to league logo
    teams = db.relationship('Team', back_populates='league', lazy='dynamic')
    matches = db.relationship('Match', back_populates='league', lazy='dynamic')
    sport = db.relationship('Sport', back_populates='leagues')

    def __repr__(self):
        return f'<League {self.name}>'

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    predicted_winner_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', back_populates='predictions')
    match = db.relationship('Match', back_populates='predictions')
    predicted_winner = db.relationship('Team', foreign_keys=[predicted_winner_id])

class PlayerStatistics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    rebounds = db.Column(db.Integer, default=0)
    steals = db.Column(db.Integer, default=0)
    blocks = db.Column(db.Integer, default=0)
    turnovers = db.Column(db.Integer, default=0)
    minutes_played = db.Column(db.Integer, default=0)
    field_goals_made = db.Column(db.Integer, default=0)
    field_goals_attempted = db.Column(db.Integer, default=0)
    three_pointers_made = db.Column(db.Integer, default=0)
    three_pointers_attempted = db.Column(db.Integer, default=0)
    free_throws_made = db.Column(db.Integer, default=0)
    free_throws_attempted = db.Column(db.Integer, default=0)
    match = db.relationship('Match', back_populates='player_statistics')
    player = db.relationship('Player', back_populates='statistics')

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', back_populates='analyses')
    match = db.relationship('Match', back_populates='analyses')

    def __repr__(self):
        return f'<Analysis {self.id} by User {self.user_id} for Match {self.match_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'match_id': self.match_id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'likes': self.likes
        }

class News(db.Model):
    """News article model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    source = db.Column(db.String(100))
    source_url = db.Column(db.String(500))
    sport_id = db.Column(db.Integer, db.ForeignKey('sport.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    
    sport_ref = db.relationship('Sport', back_populates='news_items')

    def __repr__(self):
        return f'<News {self.id}: {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'image_url': self.image_url,
            'source': self.source,
            'source_url': self.source_url,
            'sport_id': self.sport_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'views': self.views,
            'likes': self.likes,
            'sport': self.sport_ref.name if self.sport_ref else None
        }

# Add user_favorite_teams association table
user_favorite_teams = db.Table('user_favorite_teams',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True)
)
