from app import create_app, db
from app.models import User, Sport, Team, Match, Prediction, Player, PlayerStatistics, News, League, Analysis
from datetime import datetime, timedelta

def init_db():
    app = create_app()
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create initial sports
        sports = [
            Sport(name='Football', icon='fa-football-ball'),
            Sport(name='Basketball', icon='fa-basketball-ball'),
            Sport(name='Baseball', icon='fa-baseball-ball'),
            Sport(name='Hockey', icon='fa-hockey-puck')
        ]
        
        for sport in sports:
            db.session.add(sport)
        
        try:
            db.session.commit()
            print("Sports added successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding sports: {str(e)}")
            return

        # Create some leagues
        leagues = [
            League(name='Premier League', sport_id=1, country='England'),
            League(name='La Liga', sport_id=1, country='Spain'),
            League(name='NBA', sport_id=2, country='USA'),
            League(name='MLB', sport_id=3, country='USA'),
            League(name='NHL', sport_id=4, country='USA')
        ]
        
        for league in leagues:
            db.session.add(league)
        
        try:
            db.session.commit()
            print("Leagues added successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding leagues: {str(e)}")
            return

        # Create some teams
        teams = [
            # Football teams
            Team(name='Manchester United', sport_id=1, league_id=1),
            Team(name='Liverpool', sport_id=1, league_id=1),
            Team(name='Barcelona', sport_id=1, league_id=2),
            Team(name='Real Madrid', sport_id=1, league_id=2),
            # Basketball teams
            Team(name='LA Lakers', sport_id=2, league_id=3),
            Team(name='Golden State Warriors', sport_id=2, league_id=3),
            # Baseball teams
            Team(name='New York Yankees', sport_id=3, league_id=4),
            Team(name='Boston Red Sox', sport_id=3, league_id=4),
            # Hockey teams
            Team(name='Toronto Maple Leafs', sport_id=4, league_id=5),
            Team(name='Montreal Canadiens', sport_id=4, league_id=5)
        ]
        
        for team in teams:
            db.session.add(team)
        
        try:
            db.session.commit()
            print("Teams added successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding teams: {str(e)}")
            return

        # Create some matches
        now = datetime.utcnow()
        matches = [
            # Football matches
            Match(
                home_team_id=1, away_team_id=2,
                sport_id=1, league_id=1,
                start_time=now + timedelta(days=1),
                status='scheduled'
            ),
            Match(
                home_team_id=3, away_team_id=4,
                sport_id=1, league_id=2,
                start_time=now + timedelta(hours=2),
                status='scheduled'
            ),
            # Basketball matches
            Match(
                home_team_id=5, away_team_id=6,
                sport_id=2, league_id=3,
                start_time=now + timedelta(hours=4),
                status='scheduled'
            ),
            # Baseball matches
            Match(
                home_team_id=7, away_team_id=8,
                sport_id=3, league_id=4,
                start_time=now + timedelta(minutes=30),
                status='live',
                home_score=3,
                away_score=2
            ),
            # Hockey matches
            Match(
                home_team_id=9, away_team_id=10,
                sport_id=4, league_id=5,
                start_time=now - timedelta(hours=1),
                status='live',
                home_score=2,
                away_score=2
            )
        ]
        
        for match in matches:
            db.session.add(match)
        
        try:
            db.session.commit()
            print("Matches added successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding matches: {str(e)}")
            return

        # Add sample news articles
        print("Adding sample news articles...")
        news_articles = [
            News(
                title="Liverpool Dominates Premier League Match",
                content="Liverpool secured a convincing victory in their latest Premier League match, showcasing their attacking prowess and defensive stability.",
                sport_id=1,  # Football
                image_url="https://picsum.photos/800/400?random=1",
                created_at=datetime.utcnow() - timedelta(days=1)
            ),
            News(
                title="NBA Finals Update: Warriors vs Celtics",
                content="The Golden State Warriors and Boston Celtics delivered an epic performance in Game 5 of the NBA Finals, with both teams showing exceptional skill and determination.",
                sport_id=2,  # Basketball
                image_url="https://picsum.photos/800/400?random=2",
                created_at=datetime.utcnow() - timedelta(days=2)
            ),
            News(
                title="Tennis Grand Slam: Djokovic Advances to Finals",
                content="Novak Djokovic demonstrated his exceptional form as he advanced to the finals, defeating his opponent in a thrilling five-set match.",
                sport_id=3,  # Tennis
                image_url="https://picsum.photos/800/400?random=3",
                created_at=datetime.utcnow() - timedelta(days=3)
            ),
            News(
                title="Formula 1: Exciting Race at Monaco Grand Prix",
                content="The Monaco Grand Prix delivered another spectacular show with intense battles throughout the race, showcasing the best of Formula 1 racing.",
                sport_id=4,  # Racing
                image_url="https://picsum.photos/800/400?random=4",
                created_at=datetime.utcnow() - timedelta(hours=12)
            ),
            News(
                title="Champions League: Real Madrid's Victory",
                content="Real Madrid secured their spot in the next round of the Champions League with an impressive performance against their opponents.",
                sport_id=1,  # Football
                image_url="https://picsum.photos/800/400?random=5",
                created_at=datetime.utcnow() - timedelta(days=4)
            )
        ]
        
        for article in news_articles:
            db.session.add(article)
        
        try:
            db.session.commit()
            print("News articles added successfully!")
        except Exception as e:
            print(f"Error adding news articles: {e}")
            db.session.rollback()

        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
