from app import create_app, db
from app.models import Sport, Team, Match, User, League
from datetime import datetime, timedelta
import random

def init_sample_data():
    app = create_app()
    with app.app_context():
        # Clear existing data
        Match.query.delete()
        Team.query.delete()
        League.query.delete()
        Sport.query.delete()
        db.session.commit()

        # Create sports with proper icons
        sports = [
            Sport(name='Football', icon='/static/images/sports/football.png'),
            Sport(name='Basketball', icon='/static/images/sports/basketball.png'),
            Sport(name='Baseball', icon='/static/images/sports/baseball.png'),
            Sport(name='Hockey', icon='/static/images/sports/hockey.png')
        ]
        for sport in sports:
            db.session.add(sport)
        db.session.commit()

        # Create leagues with logos
        football = Sport.query.filter_by(name='Football').first()
        basketball = Sport.query.filter_by(name='Basketball').first()

        football_leagues = [
            League(name='Premier League', sport_id=football.id, country='England', 
                  logo_url='/static/images/leagues/premier-league.png'),
            League(name='La Liga', sport_id=football.id, country='Spain',
                  logo_url='/static/images/leagues/la-liga.png'),
            League(name='Bundesliga', sport_id=football.id, country='Germany',
                  logo_url='/static/images/leagues/bundesliga.png'),
            League(name='Serie A', sport_id=football.id, country='Italy',
                  logo_url='/static/images/leagues/serie-a.png')
        ]

        basketball_leagues = [
            League(name='NBA', sport_id=basketball.id, country='USA',
                  logo_url='/static/images/leagues/nba.png'),
            League(name='EuroLeague', sport_id=basketball.id, country='Europe',
                  logo_url='/static/images/leagues/euroleague.png')
        ]

        for league in football_leagues + basketball_leagues:
            db.session.add(league)
        db.session.commit()

        # Create football teams with logos
        premier_league = League.query.filter_by(name='Premier League').first()
        la_liga = League.query.filter_by(name='La Liga').first()
        bundesliga = League.query.filter_by(name='Bundesliga').first()
        serie_a = League.query.filter_by(name='Serie A').first()

        football_teams = {
            premier_league: [
                ('Manchester United', '/static/images/teams/manchester-united.png'),
                ('Liverpool', '/static/images/teams/liverpool.png'),
                ('Chelsea', '/static/images/teams/chelsea.png'),
                ('Arsenal', '/static/images/teams/arsenal.png'),
                ('Manchester City', '/static/images/teams/manchester-city.png'),
                ('Tottenham', '/static/images/teams/tottenham.png')
            ],
            la_liga: [
                ('Real Madrid', '/static/images/teams/real-madrid.png'),
                ('Barcelona', '/static/images/teams/barcelona.png'),
                ('Atletico Madrid', '/static/images/teams/atletico-madrid.png')
            ],
            bundesliga: [
                ('Bayern Munich', '/static/images/teams/bayern-munich.png'),
                ('Borussia Dortmund', '/static/images/teams/borussia-dortmund.png'),
                ('RB Leipzig', '/static/images/teams/rb-leipzig.png')
            ],
            serie_a: [
                ('Juventus', '/static/images/teams/juventus.png'),
                ('AC Milan', '/static/images/teams/ac-milan.png'),
                ('Inter Milan', '/static/images/teams/inter-milan.png')
            ]
        }
        
        # Create basketball teams with logos
        nba = League.query.filter_by(name='NBA').first()
        euroleague = League.query.filter_by(name='EuroLeague').first()

        basketball_teams = {
            nba: [
                ('LA Lakers', '/static/images/teams/la-lakers.png'),
                ('Golden State Warriors', '/static/images/teams/golden-state-warriors.png'),
                ('Chicago Bulls', '/static/images/teams/chicago-bulls.png'),
                ('Boston Celtics', '/static/images/teams/boston-celtics.png'),
                ('Miami Heat', '/static/images/teams/miami-heat.png'),
                ('Brooklyn Nets', '/static/images/teams/brooklyn-nets.png'),
                ('Milwaukee Bucks', '/static/images/teams/milwaukee-bucks.png'),
                ('Phoenix Suns', '/static/images/teams/phoenix-suns.png')
            ],
            euroleague: [
                ('Real Madrid Baloncesto', '/static/images/teams/real-madrid-basketball.png'),
                ('Barcelona Basquet', '/static/images/teams/barcelona-basketball.png'),
                ('CSKA Moscow', '/static/images/teams/cska-moscow.png'),
                ('Olympiacos', '/static/images/teams/olympiacos.png')
            ]
        }

        # Add all teams to database
        for league, teams in football_teams.items():
            for team_name, logo_url in teams:
                team = Team(
                    name=team_name,
                    sport_id=football.id,
                    league_id=league.id,
                    logo_url=logo_url
                )
                db.session.add(team)

        for league, teams in basketball_teams.items():
            for team_name, logo_url in teams:
                team = Team(
                    name=team_name,
                    sport_id=basketball.id,
                    league_id=league.id,
                    logo_url=logo_url
                )
                db.session.add(team)
        
        db.session.commit()

        # Create matches
        now = datetime.utcnow()
        for league in League.query.all():
            teams = list(league.teams)
            for i in range(len(teams)):
                for j in range(i + 1, len(teams)):
                    # Create past match
                    past_match = Match(
                        home_team_id=teams[i].id,
                        away_team_id=teams[j].id,
                        sport_id=league.sport_id,
                        league_id=league.id,
                        start_time=now - timedelta(days=random.randint(1, 30)),
                        status='completed',
                        home_score=random.randint(0, 5),
                        away_score=random.randint(0, 5)
                    )
                    if past_match.home_score > past_match.away_score:
                        past_match.winner_id = teams[i].id
                    elif past_match.away_score > past_match.home_score:
                        past_match.winner_id = teams[j].id
                    
                    # Create upcoming match
                    future_match = Match(
                        home_team_id=teams[j].id,
                        away_team_id=teams[i].id,
                        sport_id=league.sport_id,
                        league_id=league.id,
                        start_time=now + timedelta(days=random.randint(1, 30)),
                        status='scheduled'
                    )
                    
                    db.session.add(past_match)
                    db.session.add(future_match)
                    
                    # Create some live matches
                    if random.random() < 0.2:  # 20% chance for a live match
                        live_match = Match(
                            home_team_id=teams[i].id,
                            away_team_id=teams[j].id,
                            sport_id=league.sport_id,
                            league_id=league.id,
                            start_time=now - timedelta(minutes=random.randint(1, 45)),
                            status='live',
                            home_score=random.randint(0, 3),
                            away_score=random.randint(0, 3)
                        )
                        db.session.add(live_match)
        
        db.session.commit()

if __name__ == '__main__':
    init_sample_data()
