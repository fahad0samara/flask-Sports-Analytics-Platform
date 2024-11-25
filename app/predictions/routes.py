from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from app import db
from app.predictions import bp
from app.models import Match, Team, Sport, Prediction, User

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    upcoming_matches = Match.query.filter(
        Match.start_time > datetime.utcnow()
    ).order_by(Match.start_time.asc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('predictions/index.html',
                         title='Upcoming Matches',
                         matches=upcoming_matches)

@bp.route('/predict/<int:match_id>', methods=['POST'])
@login_required
def make_prediction(match_id):
    match = Match.query.get_or_404(match_id)
    
    # Check if match is still open for predictions
    if match.status != 'scheduled':
        flash('This match is no longer open for predictions.', 'error')
        return redirect(url_for('main.match_detail', match_id=match_id))
    
    # Check if user has already predicted
    if current_user.has_predicted(match):
        flash('You have already made a prediction for this match.', 'error')
        return redirect(url_for('main.match_detail', match_id=match_id))
    
    winner_id = request.form.get('winner_id', type=int)
    confidence = request.form.get('confidence', type=int)
    
    if not winner_id or not confidence:
        flash('Please provide both a winner and confidence level.', 'error')
        return redirect(url_for('main.match_detail', match_id=match_id))
    
    if confidence < 0 or confidence > 100:
        flash('Confidence must be between 0 and 100.', 'error')
        return redirect(url_for('main.match_detail', match_id=match_id))
    
    # Create prediction
    prediction = Prediction(
        user_id=current_user.id,
        match_id=match_id,
        predicted_winner_id=winner_id,
        confidence=confidence / 100.0,  # Store as decimal
        created_at=datetime.utcnow()
    )
    
    db.session.add(prediction)
    db.session.commit()
    
    flash('Your prediction has been recorded!', 'success')
    return redirect(url_for('main.match_detail', match_id=match_id))

@bp.route('/predictions')
@login_required
def my_predictions():
    predictions = Prediction.query.filter_by(
        user_id=current_user.id
    ).order_by(Prediction.created_at.desc()).all()
    
    return render_template('predictions/my_predictions.html',
        predictions=predictions
    )

@bp.route('/leaderboard')
def leaderboard():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(
        User.predictions.any().desc()
    ).paginate(
        page=page, per_page=20, error_out=False
    )
    
    leaderboard_data = []
    for user in users.items:
        stats = user.get_statistics()
        leaderboard_data.append({
            'username': user.username,
            'total_predictions': stats['total_predictions'],
            'correct_predictions': stats['correct_predictions'],
            'accuracy': stats['accuracy'],
            'streak': stats['prediction_streak']
        })
    
    return render_template('predictions/leaderboard.html',
                         title='Leaderboard',
                         leaderboard_data=leaderboard_data,
                         pagination=users)

@bp.route('/sports/<int:sport_id>/matches')
def sport_matches(sport_id):
    sport = Sport.query.get_or_404(sport_id)
    page = request.args.get('page', 1, type=int)
    matches = Match.query.join(Team, Match.home_team_id == Team.id)\
        .filter(Team.sport_id == sport_id)\
        .order_by(Match.start_time.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    return render_template('predictions/sport_matches.html',
                         title=f'{sport.name} Matches',
                         sport=sport,
                         matches=matches)

@bp.route('/api/matches/live')
def live_matches():
    matches = Match.query.filter(
        Match.start_time <= datetime.utcnow(),
        Match.end_time.is_(None)
    ).all()
    
    live_data = []
    for match in matches:
        live_data.append({
            'id': match.id,
            'home_team': match.home_team.name,
            'away_team': match.away_team.name,
            'home_score': match.home_score or 0,
            'away_score': match.away_score or 0,
            'start_time': match.start_time.isoformat(),
            'sport': match.home_team.sport.name
        })
    
    return jsonify(live_data)
