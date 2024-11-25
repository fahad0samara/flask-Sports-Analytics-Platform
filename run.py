from app import create_app, db
from app.models import User, Sport, Team, Player, Match, Prediction, PlayerStatistics

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Sport': Sport,
        'Team': Team,
        'Player': Player,
        'Match': Match,
        'Prediction': Prediction,
        'PlayerStatistics': PlayerStatistics
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8686, debug=True)
