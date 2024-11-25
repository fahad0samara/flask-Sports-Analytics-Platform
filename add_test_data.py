from app import create_app, db
from app.models import Sport, Team, Match
from datetime import datetime

def add_test_data():
    app = create_app()
    with app.app_context():
        # Get or create Football sport
        sport = Sport.query.filter_by(name='Football').first()
        if not sport:
            sport = Sport(name='Football')
            db.session.add(sport)
            db.session.commit()
        
        # Create teams
        team1 = Team(name='Arsenal', sport=sport)
        team2 = Team(name='Chelsea', sport=sport)
        db.session.add(team1)
        db.session.add(team2)
        db.session.commit()
        
        # Create live match
        match = Match(
            home_team=team1,
            away_team=team2,
            sport=sport,
            status='live',
            home_score=2,
            away_score=1,
            start_time=datetime.utcnow()
        )
        db.session.add(match)
        db.session.commit()
        
        print("Test data added successfully!")

if __name__ == '__main__':
    add_test_data()
