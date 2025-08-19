import pandas as pd

class DataParser:
    @staticmethod
    def clean_player_data(df):
        """Convert FBref scraped data to database-ready format"""
        df['minutes'] = df['minutes'].fillna(0)
        df['games_played'] = (df['minutes'] / 90).round().astype(int)
        return df