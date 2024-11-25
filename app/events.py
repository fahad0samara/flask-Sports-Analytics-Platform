from flask_socketio import emit
from app import socketio
from app.models import Match, Event
from flask_login import current_user

@socketio.on('connect')
def handle_connect():
    if not current_user.is_authenticated:
        return False
    emit('connect', {'data': 'Connected'})

@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to updates for a specific match"""
    match_id = data.get('match_id')
    if match_id:
        room = f'match_{match_id}'
        join_room(room)
        match = Match.query.get(match_id)
        if match:
            emit('match_data', {
                'match_id': match.id,
                'home_team': match.home_team.name,
                'away_team': match.away_team.name,
                'home_score': match.home_score,
                'away_score': match.away_score,
                'status': match.status,
                'time': match.current_time,
                'events': [event.to_dict() for event in match.events]
            })

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """Unsubscribe from updates for a specific match"""
    match_id = data.get('match_id')
    if match_id:
        room = f'match_{match_id}'
        leave_room(room)

def broadcast_match_update(match_id, update_type, data):
    """Broadcast match updates to all subscribed clients"""
    room = f'match_{match_id}'
    emit('match_update', {
        'type': update_type,
        'data': data
    }, room=room)

def broadcast_event(match_id, event):
    """Broadcast a new match event to all subscribed clients"""
    room = f'match_{match_id}'
    emit('match_event', event.to_dict(), room=room)
