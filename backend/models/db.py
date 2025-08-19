from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Player(db.Model):
    """Stores comprehensive player stats from FBref"""
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    fbref_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)
    nationality = db.Column(db.String(50))
    team = db.Column(db.String(100))
    league = db.Column(db.String(100))
    
    # Standard stats
    minutes = db.Column(db.Integer)
    games_played = db.Column(db.Integer)
    starts = db.Column(db.Integer)
    goals = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    cards_yellow = db.Column(db.Integer)
    cards_red = db.Column(db.Integer)
    
    # Advanced metrics (FBref-specific)
    xG = db.Column(db.Float)  # Expected goals
    xA = db.Column(db.Float)  # Expected assists
    progressive_passes = db.Column(db.Integer)
    progressive_carries = db.Column(db.Integer)
    tackles = db.Column(db.Integer)
    interceptions = db.Column(db.Integer)
    
    # Calculated ratings
    overall = db.Column(db.Integer)  # 0-100 rating
    potential = db.Column(db.Integer)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    team_rel = db.relationship('Team', back_populates='players')

    def __repr__(self):
        return f'<Player {self.name} ({self.team})>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'team': self.team,
            'age': self.age,
            'goals': self.goals,
            'assists': self.assists,
            'xg': self.xG,
            'xa': self.xA,
            'overall': self.overall,
            'potential': self.potential
        }

class Team(db.Model):
    """Stores team data from FBref"""
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    fbref_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    league = db.Column(db.String(100))
    country = db.Column(db.String(50))
    
    # Season stats
    matches_played = db.Column(db.Integer)
    wins = db.Column(db.Integer)
    draws = db.Column(db.Integer)
    losses = db.Column(db.Integer)
    goals_for = db.Column(db.Integer)
    goals_against = db.Column(db.Integer)
    xG = db.Column(db.Float)  # Expected goals for
    xGA = db.Column(db.Float)  # Expected goals against
    possession = db.Column(db.Float)  # % possession avg
    
    # Relationships
    players = db.relationship('Player', back_populates='team_rel')
    
    def __repr__(self):
        return f'<Team {self.name} ({self.league})>'

class Match(db.Model):
    """Stores match predictions and results"""
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    season = db.Column(db.String(20))
    
    # Team references
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    
    # Actual results
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    
    # Prediction data
    home_xG = db.Column(db.Float)
    away_xG = db.Column(db.Float)
    prob_home_win = db.Column(db.Float)
    prob_draw = db.Column(db.Float)
    prob_away_win = db.Column(db.Float)
    
    # Relationships
    home_team = db.relationship('Team', foreign_keys=[home_team_id])
    away_team = db.relationship('Team', foreign_keys=[away_team_id])

    def get_prediction_accuracy(self):
        """Calculate if prediction was correct"""
        if self.home_score is None:
            return None
        predicted_outcome = max(
            ['home', prob_home_win],
            ['draw', prob_draw],
            ['away', prob_away_win],
            key=lambda x: x[1]
        )[0]
        
        actual_outcome = (
            'home' if self.home_score > self.away_score else
            'away' if self.home_score < self.away_score else 'draw'
        )
        
        return predicted_outcome == actual_outcome

# Initialize database (run this once)
def init_db():
    with app.app_context():
        db.create_all()