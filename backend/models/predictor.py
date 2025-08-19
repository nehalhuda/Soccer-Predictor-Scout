import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta
import os

class MatchPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = 'models/match_predictor.joblib'
        self.scaler_path = 'models/scaler.joblib'
        self.is_trained = False
        
        # Feature columns for training
        self.feature_columns = [
            'home_team_rating', 'away_team_rating',
            'home_team_form', 'away_team_form',
            'home_goals_scored', 'away_goals_scored',
            'home_goals_conceded', 'away_goals_conceded',
            'home_xG', 'away_xG',
            'days_since_last_match'
        ]
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
    
    def train(self, historical_matches):
        """
        Train the prediction model on historical match data
        historical_matches: List of dicts with match data
        """
        if not historical_matches or len(historical_matches) < 20:
            print("Insufficient data for training. Using default model.")
            self._create_default_model()
            return
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(historical_matches)
            
            # Prepare features and target
            X = df[self.feature_columns]
            y = df['result']  # 'home', 'draw', or 'away'
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Train model (using Gradient Boosting for better performance)
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=3,
                random_state=42
            )
            
            self.model.fit(X_train, y_train)
            
            # Save model and scaler
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            self.is_trained = True
            
            # Calculate training accuracy
            train_accuracy = self.model.score(X_train, y_train)
            test_accuracy = self.model.score(X_test, y_test)
            
            print(f"Model trained successfully!")
            print(f"Training accuracy: {train_accuracy:.3f}")
            print(f"Test accuracy: {test_accuracy:.3f}")
            
        except Exception as e:
            print(f"Error training model: {e}")
            self._create_default_model()
    
    def _create_default_model(self):
        """Create a simple default model when training data is insufficient"""
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        
        # Create minimal dummy data for basic functionality
        X_dummy = np.random.rand(20, len(self.feature_columns))
        y_dummy = np.random.choice(['home', 'draw', 'away'], 20, p=[0.45, 0.25, 0.30])
        
        self.model.fit(X_dummy, y_dummy)
        self.is_trained = False
    
    def load_model(self):
        """Load pre-trained model and scaler"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.is_trained = True
                print("Pre-trained model loaded successfully!")
            else:
                self._create_default_model()
        except Exception as e:
            print(f"Error loading model: {e}")
            self._create_default_model()
    
    def predict(self, home_team_data, away_team_data, match_context=None):
        """
        Predict match outcome between two teams
        
        Parameters:
        home_team_data: Dict with team stats
        away_team_data: Dict with team stats
        match_context: Optional dict with additional context
        """
        if self.model is None:
            self.load_model()
        
        # Prepare feature vector
        features = self._prepare_features(home_team_data, away_team_data, match_context)
        
        if features is None:
            # Return reasonable defaults if feature preparation fails
            return {
                'home_win': 0.45,
                'draw': 0.30,
                'away_win': 0.25,
                'confidence': 0.65,
                'is_trained': self.is_trained
            }
        
        try:
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Get predictions
            probabilities = self.model.predict_proba(features_scaled)[0]
            classes = self.model.classes_
            
            # Convert to dictionary
            result = {
                'home_win': float(probabilities[list(classes).index('home')]),
                'draw': float(probabilities[list(classes).index('draw')]),
                'away_win': float(probabilities[list(classes).index('away')]),
                'confidence': float(np.max(probabilities)),
                'is_trained': self.is_trained
            }
            
            return result
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return {
                'home_win': 0.45,
                'draw': 0.30,
                'away_win': 0.25,
                'confidence': 0.65,
                'is_trained': False
            }
    
    def _prepare_features(self, home_team, away_team, match_context):
        """Prepare feature vector for prediction"""
        try:
            # Calculate basic features
            features = [
                home_team.get('rating', 75),          # home_team_rating
                away_team.get('rating', 75),          # away_team_rating
                home_team.get('form', 0.5),           # home_team_form (0-1)
                away_team.get('form', 0.5),           # away_team_form (0-1)
                home_team.get('goals_scored', 1.5),   # home_goals_scored
                away_team.get('goals_scored', 1.5),   # away_goals_scored
                home_team.get('goals_conceded', 1.2), # home_goals_conceded
                away_team.get('goals_conceded', 1.2), # away_goals_conceded
                home_team.get('xG', 1.8),             # home_xG
                away_team.get('xG', 1.8),             # away_xG
                match_context.get('days_rest', 7) if match_context else 7  # days_since_last_match
            ]
            
            return features
            
        except Exception as e:
            print(f"Feature preparation error: {e}")
            return None
    
    def calculate_team_form(self, recent_results):
        """
        Calculate team form based on recent results
        recent_results: List of results ('win', 'draw', 'loss')
        """
        if not recent_results:
            return 0.5  # Neutral form
        
        form_score = 0
        for result in recent_results[-5:]:  # Last 5 matches
            if result == 'win':
                form_score += 1
            elif result == 'draw':
                form_score += 0.5
            # loss adds 0
        
        return min(1.0, form_score / 5)  # Normalize to 0-1

# Global predictor instance
predictor = MatchPredictor()

# Example usage (for testing)
if __name__ == "__main__":
    # Test the predictor
    test_home_team = {
        'rating': 82,
        'form': 0.7,
        'goals_scored': 2.1,
        'goals_conceded': 0.9,
        'xG': 2.3
    }
    
    test_away_team = {
        'rating': 78,
        'form': 0.4,
        'goals_scored': 1.5,
        'goals_conceded': 1.8,
        'xG': 1.6
    }
    
    test_context = {'days_rest': 4}
    
    prediction = predictor.predict(test_home_team, test_away_team, test_context)
    print("Test Prediction:", prediction)