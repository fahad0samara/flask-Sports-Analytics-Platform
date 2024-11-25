from flask import jsonify, request, url_for, abort, current_app
from app.api import bp
from app.models import User, Sport, Team, Match, Prediction, PlayerStatistics
from app import db
from flask_login import current_user, login_required
from datetime import datetime

@bp.route('/matches')
def get_matches():
    page = request.args.get('page', 1, type=int)
    matches = Match.query.order_by(Match.date.desc()).paginate(
        page=page, per_page=current_app.config['MATCHES_PER_PAGE'],
        error_out=False)
    data = {
        'matches': [{'id': m.id,
                    'sport': m.sport.name,
                    'home_team': m.home_team.name,
                    'away_team': m.away_team.name,
                    'date': m.date.isoformat(),
                    'status': m.status,
                    'home_score': m.home_score,
                    'away_score': m.away_score} for m in matches.items],
        'total': matches.total,
        'pages': matches.pages,
        'current_page': page
    }
    return jsonify(data)

@bp.route('/predictions', methods=['POST'])
@login_required
def create_prediction():
    data = request.get_json() or {}
    if 'match_id' not in data or 'predicted_winner' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    match = Match.query.get_or_404(data['match_id'])
    if match.status != 'scheduled':
        return jsonify({'error': 'Cannot predict on completed matches'}), 400
    
    prediction = Prediction(
        user_id=current_user.id,
        match_id=data['match_id'],
        predicted_winner=data['predicted_winner'],
        confidence=data.get('confidence', 0.5)
    )
    db.session.add(prediction)
    db.session.commit()
    
    return jsonify({
        'id': prediction.id,
        'match_id': prediction.match_id,
        'predicted_winner': prediction.predicted_winner,
        'confidence': prediction.confidence,
        'created_at': prediction.created_at.isoformat()
    }), 201

@bp.route('/stats/player/<int:player_id>')
def get_player_stats(player_id):
    stats = PlayerStatistics.query.filter_by(player_id=player_id).all()
    data = [{
        'match_id': s.match_id,
        'points': s.points,
        'assists': s.assists,
        'rebounds': s.rebounds,
        'other_stats': s.other_stats
    } for s in stats]
    return jsonify(data)

@bp.route('/stats/team/<int:team_id>')
def get_team_stats(team_id):
    team = Team.query.get_or_404(team_id)
    home_matches = Match.query.filter_by(home_team_id=team_id).all()
    away_matches = Match.query.filter_by(away_team_id=team_id).all()
    
    wins = sum(1 for m in home_matches if m.home_score > m.away_score) + \
           sum(1 for m in away_matches if m.away_score > m.home_score)
    
    total_matches = len(home_matches) + len(away_matches)
    win_rate = wins / total_matches if total_matches > 0 else 0
    
    return jsonify({
        'team_name': team.name,
        'total_matches': total_matches,
        'wins': wins,
        'win_rate': win_rate
    })
