from datetime import datetime
from sqlalchemy import or_, func
from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import User, Sport, League, Team, Match, News, Analysis
from app.main.utils import (
    calculate_match_predictions,
    prediction_confidence,
    calculate_team_form,
    calculate_head_to_head,
    calculate_league_position_trend,
    get_injury_report,
    calculate_goal_statistics
)

@bp.route('/')
def landing():
    """Landing page with live matches and platform statistics"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Get platform statistics
    total_matches = Match.query.count()
    total_users = User.query.count()
    total_predictions = Analysis.query.count()
    
    # Get featured matches and news
    featured_matches = Match.query.filter_by(status='live').order_by(Match.start_time.desc()).limit(6).all()
    latest_news = News.query.order_by(News.created_at.desc()).limit(5).all()
    trending_news = News.query.order_by(News.views.desc()).limit(5).all()
    top_leagues = League.query.order_by(League.name).limit(5).all()
    
    return render_template('main/landing.html',
        total_matches=total_matches,
        total_users=total_users,
        total_predictions=total_predictions,
        featured_matches=featured_matches,
        latest_news=latest_news,
        trending_news=trending_news,
        top_leagues=top_leagues,
        now=datetime.utcnow()
    )

@bp.route('/index')
@login_required
def index():
    """Dashboard for authenticated users"""
    now = datetime.utcnow()
    
    # Get live matches
    live_matches = Match.query.filter(
        Match.status == 'live'
    ).order_by(Match.start_time.desc()).limit(6).all()
    
    # Get upcoming matches
    upcoming_matches = Match.query.filter(
        Match.status == 'scheduled',
        Match.start_time > now
    ).order_by(Match.start_time).limit(6).all()
    
    # Get user's recent predictions
    predictions = Analysis.query.filter_by(
        user_id=current_user.id
    ).order_by(Analysis.created_at.desc()).limit(6).all()
    
    # Calculate prediction statistics
    total_predictions = Analysis.query.filter_by(
        user_id=current_user.id
    ).count()
    
    correct_predictions = Analysis.query.filter_by(
        user_id=current_user.id,
        is_correct=True
    ).count()
    
    prediction_accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
    
    return render_template('main/index.html',
        live_matches=live_matches,
        upcoming_matches=upcoming_matches,
        predictions=predictions,
        total_predictions=total_predictions,
        correct_predictions=correct_predictions,
        prediction_accuracy=prediction_accuracy,
        now=datetime.utcnow
    )

@bp.route('/match/<int:match_id>')
@login_required
def match_detail(match_id):
    """Display detailed information about a specific match"""
    match = Match.query.get_or_404(match_id)
    form = None
    if match.status == 'scheduled' and not current_user.has_predicted(match):
        from flask_wtf import FlaskForm
        from wtforms import RadioField, IntegerField
        from wtforms.validators import DataRequired, NumberRange
        
        class PredictionForm(FlaskForm):
            winner_id = RadioField('Winner', coerce=int, validators=[DataRequired()])
            confidence = IntegerField('Confidence', validators=[
                DataRequired(),
                NumberRange(min=0, max=100, message='Confidence must be between 0 and 100')
            ])
        
        form = PredictionForm()
        form.winner_id.choices = [
            (match.home_team.id, match.home_team.name),
            (match.away_team.id, match.away_team.name)
        ]
    
    return render_template('main/match_detail.html',
                         match=match,
                         current_time=datetime.utcnow(),
                         form=form)

@bp.route('/matches')
@login_required
def matches():
    # Get filter parameters
    sport_id = request.args.get('sport', type=int)
    status = request.args.get('status', '')
    date_filter = request.args.get('date', '')

    # Base query
    query = Match.query

    # Apply sport filter
    if sport_id:
        query = query.filter(Match.sport_id == sport_id)

    # Apply status filter
    if status:
        query = query.filter(Match.status == status)

    # Apply date filter
    today = datetime.utcnow().date()
    if date_filter == 'today':
        query = query.filter(
            func.date(Match.start_time) == today
        )
    elif date_filter == 'tomorrow':
        tomorrow = today + datetime.timedelta(days=1)
        query = query.filter(
            func.date(Match.start_time) == tomorrow
        )
    elif date_filter == 'week':
        week_end = today + datetime.timedelta(days=7)
        query = query.filter(
            func.date(Match.start_time).between(today, week_end)
        )

    # Order matches by start time
    query = query.order_by(Match.start_time)

    # Execute query
    matches = query.all()

    # Get all sports for filter dropdown
    sports = Sport.query.order_by(Sport.name).all()

    return render_template('main/matches.html',
                         matches=matches,
                         sports=sports,
                         selected_sport=sport_id,
                         selected_status=status,
                         selected_date=date_filter)

@bp.route('/profile')
@login_required
def profile():
    """User profile page showing predictions and analyses"""
    try:
        print("\n=== Starting Profile Route Debug ===")
        print(f"Is user authenticated? {current_user.is_authenticated}")
        
        # Test if we can access current_user attributes
        try:
            print("\nUser Details:")
            print(f"User ID: {current_user.id}")
            print(f"Username: {current_user.username}")
            print(f"Email: {current_user.email}")
            print(f"Last seen: {current_user.last_seen}")
            print(f"Created at: {current_user.created_at}")
            print(f"Is active: {current_user.is_active}")
        except Exception as e:
            print(f"\nERROR accessing user attributes: {str(e)}")
            print("Traceback:")
            import traceback
            print(traceback.format_exc())
            return "Error accessing user data", 500

        # Test database connection and user retrieval
        try:
            print("\nTesting Database Connection:")
            user_from_db = User.query.get(current_user.id)
            print(f"Found user in database: {user_from_db is not None}")
            if user_from_db:
                print(f"DB User ID: {user_from_db.id}")
                print(f"DB Username: {user_from_db.username}")
                print(f"DB Email: {user_from_db.email}")
        except Exception as e:
            print(f"\nERROR with database: {str(e)}")
            print("Traceback:")
            import traceback
            print(traceback.format_exc())
            return "Database connection error", 500

        print("\n=== Profile Route Debug End ===\n")

        # Proceed with minimal template rendering
        try:
            stats = {
                'total_predictions': 0,
                'correct_predictions': 0,
                'accuracy': 0,
                'current_streak': 0,
                'sport_stats': []
            }
            return render_template('main/profile.html',
                                user=current_user,
                                predictions=[],
                                analyses=[],
                                stats=stats,
                                now=datetime.utcnow())
        except Exception as e:
            print(f"\nERROR rendering template: {str(e)}")
            print("Traceback:")
            import traceback
            print(traceback.format_exc())
            return "Template rendering error", 500

    except Exception as e:
        print(f"\nUNHANDLED ERROR in profile route: {str(e)}")
        print("Traceback:")
        import traceback
        print(traceback.format_exc())
        return "Internal server error", 500

@bp.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    """Handle profile updates"""
    try:
        about_me = request.form.get('about')
        if about_me is not None:
            current_user.about_me = about_me
            db.session.commit()
            flash('Your profile has been updated.', 'success')
        else:
            flash('No changes were provided.', 'warning')
        return redirect(url_for('main.profile'))
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error in edit_profile route: {str(e)}")
        db.session.rollback()
        flash("An error occurred while updating your profile. Please try again later.", "error")
        return redirect(url_for('main.profile'))
    except Exception as e:
        current_app.logger.error(f"Unexpected error in edit_profile route: {str(e)}")
        flash("An unexpected error occurred. Please try again later.", "error")
        return redirect(url_for('main.profile'))

@bp.route('/analysis')
@login_required
def analysis():
    try:
        # Get recent completed matches
        recent_matches = db.session.query(Match)\
            .filter(Match.status != 'scheduled')\
            .order_by(Match.date.desc())\
            .limit(10)\
            .all()
        
        # Get user's analyses if authenticated
        user_analyses = None
        if current_user.is_authenticated:
            user_analyses = db.session.query(Analysis)\
                .join(Match)\
                .filter(Analysis.user_id == current_user.id)\
                .order_by(Analysis.created_at.desc())\
                .all()
        
        return render_template('main/analysis.html',
                             recent_matches=recent_matches,
                             user_analyses=user_analyses)
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error in analysis route: {str(e)}")
        db.session.rollback()
        flash("An error occurred while loading the analysis page. Please try again later.", "error")
        return render_template('error.html', 
                             error_message="Database error occurred. Please try again later."), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error in analysis route: {str(e)}")
        flash("An unexpected error occurred. Please try again later.", "error")
        return render_template('error.html', 
                             error_message="An unexpected error occurred. Please try again later."), 500

@bp.route('/head-to-head')
@login_required
def head_to_head():
    sports = Sport.query.all()
    return render_template('main/head_to_head.html', sports=sports)

@bp.route('/api/teams/<int:sport_id>')
@login_required
def get_teams(sport_id):
    teams = Team.query.filter_by(sport_id=sport_id).all()
    return jsonify([{
        'id': team.id,
        'name': team.name
    } for team in teams])

@bp.route('/api/head-to-head', methods=['POST'])
@login_required
def get_head_to_head():
    sport_id = request.form.get('sport', type=int)
    team1_id = request.form.get('team1_id', type=int)
    team2_id = request.form.get('team2_id', type=int)
    
    # Get head to head matches
    matches = Match.query.filter(
        Match.sport_id == sport_id,
        ((Match.home_team_id == team1_id) & (Match.away_team_id == team2_id)) |
        ((Match.home_team_id == team2_id) & (Match.away_team_id == team1_id))
    ).all()
    
    # Calculate head to head record
    team1_wins = 0
    team2_wins = 0
    draws = 0
    
    for match in matches:
        if match.home_score > match.away_score:
            if match.home_team_id == team1_id:
                team1_wins += 1
            else:
                team2_wins += 1
        elif match.home_score < match.away_score:
            if match.away_team_id == team1_id:
                team1_wins += 1
            else:
                team2_wins += 1
        else:
            draws += 1
    
    # Get team stats
    team1 = Team.query.get(team1_id)
    team2 = Team.query.get(team2_id)
    
    team1_stats = calculate_team_stats(team1)
    team2_stats = calculate_team_stats(team2)
    
    # Get form data
    team1_form = get_team_form(team1)
    team2_form = get_team_form(team2)
    
    # Get key players
    team1_players = get_key_players(team1)
    team2_players = get_key_players(team2)
    
    # Calculate win probability
    prediction = predict_match_outcome(team1, team2)
    
    return jsonify({
        'head_to_head': {
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'draws': draws
        },
        'stats': {
            'metrics': ['Attack', 'Defense', 'Possession', 'Form', 'Home Advantage'],
            'team1_values': team1_stats,
            'team2_values': team2_stats
        },
        'form': {
            'dates': [match['date'] for match in team1_form],
            'team1_form': [match['rating'] for match in team1_form],
            'team2_form': [match['rating'] for match in team2_form]
        },
        'team1_players': team1_players,
        'team2_players': team2_players,
        'prediction': prediction
    })

@bp.route('/news')
@login_required
def news():
    """News listing page with filters and pagination"""
    page = request.args.get('page', 1, type=int)
    sport = request.args.get('sport')
    search = request.args.get('search')
    
    # Get paginated news
    query = News.query.order_by(News.created_at.desc())
    
    # Apply filters
    if sport:
        query = query.filter(News.sport_id == sport)
    if search:
        query = query.filter(
            or_(
                News.title.ilike(f'%{search}%'),
                News.content.ilike(f'%{search}%')
            )
        )
    
    # Paginate results
    news_items = query.paginate(
        page=page,
        per_page=current_app.config.get('NEWS_PER_PAGE', 12),
        error_out=False
    )
    
    # Get all sports for filter
    sports = Sport.query.all()
    
    return render_template('main/news.html',
                         news_items=news_items,
                         sports=sports,
                         selected_sport=sport,
                         search=search)

@bp.route('/api/news')
def api_news():
    page = request.args.get('page', 1, type=int)
    sport = request.args.get('sport', 'all')
    search = request.args.get('search', '')
    
    news_items = get_paginated_news(page, sport, search)
    return jsonify({
        'items': news_items.items,
        'current_page': news_items.page,
        'total_pages': news_items.pages,
        'total_items': news_items.total
    })

@bp.route('/more')
def more():
    sports = [
        {
            'name': 'Football',
            'icon_class': 'fas fa-futbol',
            'description': 'Premier League, La Liga, Champions League, and more',
            'leagues': ['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1'],
            'teams': 98,
            'accuracy': 76.5,
            'predictions': 1240
        },
        {
            'name': 'Basketball',
            'icon_class': 'fas fa-basketball-ball',
            'description': 'NBA, EuroLeague, and international competitions',
            'leagues': ['NBA', 'EuroLeague', 'ACB', 'NBL'],
            'teams': 62,
            'accuracy': 72.8,
            'predictions': 980
        },
        {
            'name': 'Tennis',
            'icon_class': 'fas fa-table-tennis',
            'description': 'Grand Slams, ATP, WTA tournaments',
            'tournaments': ['Australian Open', 'French Open', 'Wimbledon', 'US Open'],
            'players': 150,
            'accuracy': 71.2,
            'predictions': 645
        },
        {
            'name': 'Cricket',
            'icon_class': 'fas fa-cricket',
            'description': 'International matches, IPL, and major leagues',
            'competitions': ['IPL', 'Big Bash', 'World Cup', 'The Ashes'],
            'teams': 45,
            'accuracy': 73.5,
            'predictions': 420
        }
    ]
    
    stats = {
        'predictions': 3285,
        'accuracy': 74.5,
        'users': 12500,
        'matches': 1850,
        'monthly_growth': 15.8,
        'daily_predictions': 125
    }
    
    faqs = [
        {
            'question': 'How accurate are your predictions?',
            'answer': 'Our machine learning models achieve an average accuracy rate above industry standards, leveraging advanced machine learning algorithms and comprehensive historical data.'
        },
        {
            'question': 'What data sources do you use?',
            'answer': 'We aggregate data from multiple reliable sources including official league statistics, historical match data, player performance metrics, and real-time updates.'
        },
        {
            'question': 'How often are predictions updated?',
            'answer': 'Our predictions are updated in real-time as new data becomes available, ensuring you always have the most current insights.'
        },
        {
            'question': 'Is historical data available?',
            'answer': 'Yes, users can access historical predictions, match outcomes, and analysis to track performance and identify trends.'
        },
        {
            'question': 'What sports do you cover?',
            'answer': 'We currently cover major sports including football, basketball, baseball, and soccer, with plans to expand to more sports based on user demand.'
        },
        {
            'question': 'How do you calculate prediction confidence?',
            'answer': 'Our AI models analyze multiple factors including team form, head-to-head records, player statistics, and historical data to generate confidence scores.'
        }
    ]
    
    features = [
        {
            'title': 'ML-Powered Predictions',
            'description': 'Advanced algorithms analyze vast amounts of data to provide accurate predictions',
            'icon_class': 'fas fa-brain',
            'stats': {
                'accuracy': '75-80%',
                'data_points': '1M+',
                'update_frequency': 'Real-time'
            }
        },
        {
            'title': 'Live Match Tracking',
            'description': 'Real-time updates and statistics for ongoing matches',
            'icon_class': 'fas fa-chart-line',
            'stats': {
                'delay': '<1s',
                'matches_tracked': '1000+',
                'data_types': '50+'
            }
        },
        {
            'title': 'Historical Analysis',
            'description': 'Comprehensive historical data and trend analysis',
            'icon_class': 'fas fa-history',
            'stats': {
                'years_covered': '10+',
                'matches_analyzed': '100K+',
                'trends_tracked': '200+'
            }
        },
        {
            'title': 'Community Insights',
            'description': 'Share and discuss predictions with other users',
            'icon_class': 'fas fa-users',
            'stats': {
                'active_users': '12.5K+',
                'daily_discussions': '500+',
                'user_rating': '4.8/5'
            }
        }
    ]
    
    return render_template('main/more.html',
                         sports=sports,
                         stats=stats,
                         faqs=faqs,
                         features=features)

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # In a real application, you would handle the form submission here
        # For example, sending an email or storing in database
        return jsonify({'success': True})
    
    featured_faqs = [
        {
            'question': 'How accurate are your predictions?',
            'answer': 'Our AI-powered predictions have shown consistent accuracy rates above industry standards, leveraging advanced machine learning algorithms and comprehensive historical data.'
        },
        {
            'question': 'What sports do you cover?',
            'answer': 'We cover major sports including football, basketball, baseball, and soccer, with plans to expand to more sports based on user demand.'
        },
        {
            'question': 'How often are predictions updated?',
            'answer': 'Our predictions are updated in real-time as new data becomes available, ensuring you always have the most current insights.'
        }
    ]
    
    return render_template('main/contact.html', form=form, featured_faqs=featured_faqs)

@bp.route('/api/live-matches', methods=['GET'])
def live_matches():
    """Get all currently live matches with latest scores"""
    try:
        # Get matches that are either live or recently finished
        cutoff_time = datetime.utcnow() - datetime.timedelta(hours=2)
        matches = Match.query.filter(
            db.or_(
                Match.status == Match.STATUS_LIVE,
                db.and_(
                    Match.status == Match.STATUS_FINISHED,
                    Match.last_updated >= cutoff_time
                )
            )
        ).order_by(Match.start_time.desc()).all()
        
        matches_data = []
        for match in matches:
            try:
                match_data = {
                    'id': match.id,
                    'home_team': match.home_team.name,
                    'away_team': match.away_team.name,
                    'home_score': match.home_score,
                    'away_score': match.away_score,
                    'sport': match.sport.name,
                    'league': match.league.name,
                    'start_time': match.start_time.isoformat(),
                    'status': match.status,
                    'last_updated': match.last_updated.isoformat()
                }
                matches_data.append(match_data)
            except Exception as e:
                current_app.logger.error(f"Error processing match {match.id}: {str(e)}")
                continue
        
        return jsonify({
            'status': 'success',
            'matches': matches_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching live matches: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch live matches',
            'error': str(e)
        }), 500

@bp.route('/api/match/<int:match_id>/stats', methods=['GET'])
def match_stats(match_id):
    """Get detailed statistics for a specific match"""
    try:
        match = Match.query.get_or_404(match_id)
        
        # Get basic match info
        match_data = match.get_match_stats()
        
        # Get player statistics if available
        player_stats = []
        if match.player_statistics.count() > 0:
            for stat in match.player_statistics:
                player_stats.append({
                    'player_name': stat.player.name,
                    'team': stat.player.team.name,
                    'points': stat.points,
                    'assists': stat.assists,
                    'rebounds': stat.rebounds,
                    'steals': stat.steals,
                    'blocks': stat.blocks,
                    'turnovers': stat.turnovers,
                    'minutes_played': stat.minutes_played,
                    'field_goals': f"{stat.field_goals_made}/{stat.field_goals_attempted}",
                    'three_pointers': f"{stat.three_pointers_made}/{stat.three_pointers_attempted}",
                    'free_throws': f"{stat.free_throws_made}/{stat.free_throws_attempted}"
                })
        
        # Get recent head-to-head matches
        head_to_head = Match.query.filter(
            db.or_(
                db.and_(
                    Match.home_team_id == match.home_team_id,
                    Match.away_team_id == match.away_team_id
                ),
                db.and_(
                    Match.home_team_id == match.away_team_id,
                    Match.away_team_id == match.home_team_id
                )
            ),
            Match.status == Match.STATUS_FINISHED,
            Match.id != match_id
        ).order_by(Match.start_time.desc()).limit(5).all()
        
        h2h_data = []
        for h2h_match in head_to_head:
            h2h_data.append({
                'id': h2h_match.id,
                'date': h2h_match.start_time.isoformat(),
                'home_team': h2h_match.home_team.name,
                'away_team': h2h_match.away_team.name,
                'home_score': h2h_match.home_score,
                'away_score': h2h_match.away_score,
                'winner': h2h_match.get_winner().name if h2h_match.get_winner() else None
            })
        
        # Get team form (last 5 matches for each team)
        def get_team_form(team_id):
            recent_matches = Match.query.filter(
                db.or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id
                ),
                Match.status == Match.STATUS_FINISHED,
                Match.id != match_id
            ).order_by(Match.start_time.desc()).limit(5).all()
            
            form_data = []
            for form_match in recent_matches:
                is_home = form_match.home_team_id == team_id
                opponent = form_match.away_team.name if is_home else form_match.home_team.name
                team_score = form_match.home_score if is_home else form_match.away_score
                opponent_score = form_match.away_score if is_home else form_match.home_score
                
                form_data.append({
                    'id': form_match.id,
                    'date': form_match.start_time.isoformat(),
                    'opponent': opponent,
                    'score': f"{team_score}-{opponent_score}",
                    'result': 'W' if form_match.get_winner() and form_match.get_winner().id == team_id else 'L'
                })
            return form_data
        
        # Combine all statistics
        stats = {
            'match': match_data,
            'player_statistics': player_stats,
            'head_to_head': h2h_data,
            'home_team_form': get_team_form(match.home_team_id),
            'away_team_form': get_team_form(match.away_team_id)
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching match stats for match {match_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch match statistics',
            'error': str(e)
        }), 500

@bp.route('/api/scores/live', methods=['GET'])
def get_live_scores():
    """Get live scores from all integrated sports APIs"""
    try:
        aggregator = SportsDataAggregator()
        scores = aggregator.get_all_live_scores()
        return jsonify({
            'status': 'success',
            'data': scores
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching live scores: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch live scores'
        }), 500

@bp.route('/api/team/<string:team_name>', methods=['GET'])
def get_team_info(team_name):
    """Get comprehensive team information"""
    try:
        aggregator = SportsDataAggregator()
        team_data = aggregator.get_team_data(team_name)
        return jsonify({
            'status': 'success',
            'data': team_data
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching team info: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch team information'
        }), 500

@bp.route('/api/news/sports', methods=['GET'])
def get_sports_news():
    """Get latest sports news"""
    try:
        aggregator = SportsDataAggregator()
        news = aggregator.get_sports_news()
        return jsonify({
            'status': 'success',
            'data': news
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching sports news: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch sports news'
        }), 500

@bp.route('/sport/<int:sport_id>')
@login_required
def sport(sport_id):
    """Display detailed information about a specific sport and its leagues"""
    sport = Sport.query.get_or_404(sport_id)
    leagues = sport.leagues
    
    # Prepare league data with matches
    leagues_data = []
    for league in leagues:
        live_matches = league.matches.filter_by(status='live').all()
        upcoming_matches = league.matches.filter_by(status='scheduled')\
            .order_by(Match.start_time.asc())\
            .limit(5).all()
        completed_matches = league.matches.filter_by(status='completed')\
            .order_by(Match.start_time.desc())\
            .limit(5).all()
            
        leagues_data.append({
            'league': league,
            'live_matches': live_matches,
            'upcoming_matches': upcoming_matches,
            'completed_matches': completed_matches
        })
    
    return render_template('main/sport.html',
                         sport=sport,
                         leagues_data=leagues_data,
                         current_time=datetime.utcnow())

@bp.route('/create_analysis/<int:match_id>', methods=['POST'])
@login_required
def create_analysis(match_id):
    try:
        match = Match.query.get_or_404(match_id)
        content = request.form.get('content')
        
        if not content:
            flash('Analysis content is required.', 'error')
            return redirect(url_for('main.analysis'))
            
        analysis = Analysis(
            user_id=current_user.id,
            match_id=match_id,
            content=content
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        flash('Your analysis has been added successfully!', 'success')
        return redirect(url_for('main.analysis'))
        
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error in create_analysis route: {str(e)}")
        db.session.rollback()
        flash('An error occurred while saving your analysis.', 'error')
        return redirect(url_for('main.analysis'))

@bp.route('/predictions')
@login_required
def predictions():
    sport_id = request.args.get('sport', type=int)
    league_id = request.args.get('league', type=int)
    confidence = request.args.get('confidence')
    
    query = Match.query.filter(Match.start_time > datetime.utcnow())
    
    if sport_id:
        query = query.filter(Match.sport_id == sport_id)
    if league_id:
        query = query.filter(Match.league_id == league_id)
        
    matches = query.order_by(Match.start_time).all()
    
    # Calculate predictions for each match
    for match in matches:
        predictions = calculate_match_predictions(match)
        match.home_win_probability = predictions['home_win_probability']
        match.away_win_probability = predictions['away_win_probability']
        match.total_goals_prediction = predictions['total_goals_prediction']
        match.possession_home = predictions['possession_home']
        match.shots_prediction = predictions['shots_prediction']
    
    # Filter by confidence if specified
    if confidence:
        matches = [m for m in matches if prediction_confidence(m) == confidence]
    
    return render_template('main/predictions.html',
                         matches=matches,
                         sports=Sport.query.all(),
                         leagues=League.query.all(),
                         selected_sport=sport_id,
                         selected_league=league_id,
                         selected_confidence=confidence)

@bp.route('/team-stats')
@login_required
def team_stats():
    sport_id = request.args.get('sport', type=int)
    league_id = request.args.get('league', type=int)
    team_id = request.args.get('team', type=int)
    
    # Build team query based on filters
    team_query = Team.query
    if sport_id:
        team_query = team_query.join(League).filter(League.sport_id == sport_id)
    if league_id:
        team_query = team_query.filter(Team.league_id == league_id)
    
    # Get selected team if specified
    selected_team = None
    if team_id:
        selected_team = Team.query.get_or_404(team_id)
        
        # Calculate team statistics
        matches = Match.query.filter(
            or_(Match.home_team_id == team_id, Match.away_team_id == team_id)
        ).order_by(Match.start_time.desc()).all()
        
        # Add basic statistics
        selected_team.matches_played = len(matches)
        selected_team.wins = sum(1 for m in matches if 
            (m.home_team_id == team_id and m.home_score > m.away_score) or
            (m.away_team_id == team_id and m.away_score > m.home_score))
        selected_team.draws = sum(1 for m in matches if m.home_score == m.away_score)
        selected_team.losses = selected_team.matches_played - selected_team.wins - selected_team.draws
        
        # Calculate percentages and advanced stats
        selected_team.win_rate = round((selected_team.wins / selected_team.matches_played) * 100 if selected_team.matches_played > 0 else 0)
        selected_team.form = calculate_team_form(selected_team)
        selected_team.position_trend = calculate_league_position_trend(selected_team)
        selected_team.injuries = get_injury_report(selected_team)
        
        # Get goal statistics
        goal_stats = calculate_goal_statistics(selected_team)
        selected_team.goals_scored = goal_stats['goals_scored']
        selected_team.goals_conceded = goal_stats['goals_conceded']
        selected_team.clean_sheets = goal_stats['clean_sheets']
        selected_team.failed_to_score = goal_stats['failed_to_score']
        
        # Calculate goal scoring rate for progress bar
        max_goals = 60  # Arbitrary maximum for progress bar
        selected_team.goals_percentage = min(round((goal_stats['goals_scored'] / max_goals) * 100), 100)
        selected_team.clean_sheet_percentage = round((goal_stats['clean_sheets'] / selected_team.matches_played) * 100 if selected_team.matches_played > 0 else 0)
        
        # Get recent matches
        selected_team.recent_matches = []
        for match in matches[:5]:  # Last 5 matches
            result = {}
            if match.home_team_id == team_id:
                result['opponent'] = match.away_team.name
                result['score'] = f"{match.home_score}-{match.away_score}"
                if match.home_score > match.away_score:
                    result['result'] = 'WIN'
                elif match.home_score < match.away_score:
                    result['result'] = 'LOSS'
                else:
                    result['result'] = 'DRAW'
            else:
                result['opponent'] = match.home_team.name
                result['score'] = f"{match.away_score}-{match.home_score}"
                if match.away_score > match.home_score:
                    result['result'] = 'WIN'
                elif match.away_score < match.home_score:
                    result['result'] = 'LOSS'
                else:
                    result['result'] = 'DRAW'
            result['date'] = match.start_time
            selected_team.recent_matches.append(result)
    
    return render_template('main/team_stats.html',
                         sports=Sport.query.all(),
                         leagues=League.query.all(),
                         teams=team_query.all(),
                         team=selected_team,
                         selected_sport=sport_id,
                         selected_league=league_id,
                         selected_team=team_id)

@bp.context_processor
def utility_processor():
    """Add utility functions and variables to template context"""
    def format_date(date):
        if date:
            return date.strftime('%Y-%m-%d %H:%M')
        return ''
    
    # Get all sports for navigation
    sports = Sport.query.all()
    
    return dict(
        format_date=format_date,
        sports=sports
    )

def get_paginated_news(page=1, sport=None, search=None):
    """Helper function to get paginated news items with filters"""
    per_page = 10
    query = News.query

    if sport:
        query = query.filter(News.sport_id == sport)
    
    if search:
        search = f"%{search}%"
        query = query.filter(
            or_(
                News.title.ilike(search),
                News.content.ilike(search)
            )
        )
    
    return query.order_by(News.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
