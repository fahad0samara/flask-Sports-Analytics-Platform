import logging
from datetime import datetime, timedelta
from app import db, create_app
from app.utils.live_match_tracker import LiveMatchTracker
from app.models import Match

logger = logging.getLogger(__name__)

def update_live_matches():
    """Background task to update live match data"""
    try:
        app = create_app()
        with app.app_context():
            tracker = LiveMatchTracker()
            
            # Update live matches
            success = tracker.update_live_matches()
            if not success:
                logger.error("Failed to update live matches")
                return
            
            # Check for matches that should be starting soon
            upcoming_matches = Match.query.filter(
                Match.status == 'scheduled',
                Match.start_time <= datetime.utcnow() + timedelta(minutes=15)
            ).all()
            
            # Update status for matches starting soon
            for match in upcoming_matches:
                if match.start_time <= datetime.utcnow():
                    match.status = 'live'
            
            db.session.commit()
            
    except Exception as e:
        logger.error(f"Error in match updater task: {str(e)}")

if __name__ == '__main__':
    update_live_matches()
