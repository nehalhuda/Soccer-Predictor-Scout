from flask import Flask, jsonify, request
from flask_cors import CORS
from models.db import db, Player, Team, Match
from scraper.fbref_scraper import FBrefScraper
from scraper.data_parser import DataParser
from models.predictor import predictor
import pandas as pd

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///soccer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize components
scraper = FBrefScraper()
parser = DataParser()

@app.route('/')
def home():
    return jsonify({"message": "Soccer Predictor API", "status": "active"})

@app.route('/api/fetch-fbref', methods=['POST'])
def fetch_fbref_data():
    """Fetch and store data from FBref"""
    try:
        league_url = request.json.get('league_url', '/en/comps/9/Premier-League-Stats')
        data = scraper.get_league_data(league_url)
        
        with app.app_context():
            for _, row in data.iterrows():
                player = Player(
                    fbref_id=row.get('fbref_id', f"player_{row['name'].lower().replace(' ', '_')}"),
                    name=row['name'],
                    position=row['position'],
                    age=row['age'],
                    team=row['team'],
                    league=row['league'],
                    minutes=row['minutes'],
                    games_played=row.get('games_played', 0),
                    goals=row.get('goals', 0),
                    assists=row.get('assists', 0),
                    xG=row.get('xg', 0),
                    xA=row.get('xa', 0),
                    overall=row.get('overall', 70)
                )
                db.session.add(player)
            db.session.commit()
        
        return jsonify({
            "status": "success",
            "players_added": len(data),
            "message": "FBref data loaded successfully"
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/players', methods=['GET'])
def get_players():
    """Get all players"""
    players = Player.query.all()
    return jsonify([player.to_dict() for player in players])

@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Get all teams"""
    teams = Team.query.all()
    return jsonify([team.to_dict() for team in teams])

@app.route('/api/predict', methods=['POST'])
def predict_match():
    """Predict match outcome"""
    data = request.json
    home_team_id = data.get('home_team')
    away_team_id = data.get('away_team')
    
    # For now, return dummy predictions
    prediction = {
        'home_win': 0.45,
        'draw': 0.30,
        'away_win': 0.25,
        'confidence': 0.78
    }
    
    return jsonify(prediction)

@app.route('/api/analyze-squad', methods=['POST'])
def analyze_squad():
    """Analyze a custom squad"""
    squad = request.json.get('squad', [])
    formation = request.json.get('formation', '4-4-2')
    
    # Simple analysis
    total_rating = sum(player['overall'] for player in squad)
    avg_rating = total_rating / len(squad) if squad else 0
    
    return jsonify({
        'average_rating': round(avg_rating, 1),
        'total_rating': total_rating,
        'formation_suitability': 'Good' if len(squad) == 11 else 'Incomplete',
        'strengths': ['Attack', 'Creativity'],
        'weaknesses': ['Defense', 'Physicality']
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)