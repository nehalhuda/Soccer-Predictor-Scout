# backend/app.py
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, request
from flask_cors import CORS

from models.db import db, Player, Team, Match
from scraper.fbref_scraper import FBrefScraper
from scraper.data_parser import DataParser
from models.predictor import predictor  # keep if used elsewhere
import pandas as pd  # keep if used elsewhere

# ---- create app BEFORE any @app.route ----
app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///soccer.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Initialize components
scraper = FBrefScraper()
parser = DataParser()

# ---- routes ----
@app.route("/")
def home():
    return jsonify({"message": "Soccer Predictor API", "status": "active"})

@app.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"ok": True}), 200

# Import AFTER app exists; alias to avoid clashing with /api/teams route name
from services.football_data import get_teams as fd_get_teams

@app.route("/api/teams_fd", methods=["GET"])
def teams_from_football_data():
    comp = request.args.get("competition", "PL")  # e.g., PL, PD, SA, BL1
    return jsonify(fd_get_teams(comp)), 200

@app.route("/api/fetch-fbref", methods=["POST"])
def fetch_fbref_data():
    """Fetch and store data from FBref"""
    try:
        league_url = request.json.get("league_url", "/en/comps/9/Premier-League-Stats")
        data = scraper.get_league_data(league_url)

        with app.app_context():
            for _, row in data.iterrows():
                player = Player(
                    fbref_id=row.get("fbref_id", f"player_{row['name'].lower().replace(' ', '_')}"),
                    name=row["name"],
                    position=row["position"],
                    age=row["age"],
                    team=row["team"],
                    league=row["league"],
                    minutes=row["minutes"],
                    games_played=row.get("games_played", 0),
                    goals=row.get("goals", 0),
                    assists=row.get("assists", 0),
                    xG=row.get("xg", 0),
                    xA=row.get("xa", 0),
                    overall=row.get("overall", 70),
                )
                db.session.add(player)
            db.session.commit()

        return jsonify({"status": "success", "players_added": len(data), "message": "FBref data loaded successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/players", methods=["GET"])
def get_players_route():
    """Get all players"""
    players = Player.query.all()
    return jsonify([p.to_dict() for p in players])

@app.route("/api/teams", methods=["GET"])
def get_teams_route():
    """Get all teams (from your DB)"""
    teams = Team.query.all()
    return jsonify([t.to_dict() for t in teams])

@app.route("/api/predict", methods=["POST"])
def predict_match():
    """Predict match outcome (dummy for now)"""
    data = request.get_json(force=True) or {}
    _home_team_id = data.get("home_team")
    _away_team_id = data.get("away_team")
    prediction = {
        "home_win": 0.45,
        "draw": 0.30,
        "away_win": 0.25,
        "confidence": 0.78,
    }
    return jsonify(prediction)

@app.route("/api/analyze-squad", methods=["POST"])
def analyze_squad():
    """Analyze a custom squad"""
    payload = request.get_json(force=True) or {}
    squad = payload.get("squad", [])
    _formation = payload.get("formation", "4-4-2")

    total_rating = sum(player.get("overall", 0) for player in squad)
    avg_rating = total_rating / len(squad) if squad else 0

    return jsonify({
        "average_rating": round(avg_rating, 1),
        "total_rating": total_rating,
        "formation_suitability": "Good" if len(squad) == 11 else "Incomplete",
        "strengths": ["Attack", "Creativity"],
        "weaknesses": ["Defense", "Physicality"],
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
