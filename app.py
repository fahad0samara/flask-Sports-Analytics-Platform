from app import create_app, db
from app.models import User, Match, Prediction, Team, Sport

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Match': Match,
        'Prediction': Prediction,
        'Team': Team,
        'Sport': Sport
    }

if __name__ == '__main__':
    app.run(debug=True)
