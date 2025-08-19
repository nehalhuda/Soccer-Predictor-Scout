import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from fake_useragent import UserAgent

class FBrefScraper:
    def __init__(self):
        self.base_url = "https://fbref.com"
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.ua.random})
        self.delay = 5  # seconds between requests

    def get_league_data(self, league_url):
        """Scrape all teams and players from a league"""
        league_data = []
        teams = self._get_teams(league_url)
        
        for team in teams[:3]:  # Limit to 3 teams for testing
            players = self._get_players(team['url'])
            for player in players:
                player['team'] = team['name']
                player['league'] = team['league']
                league_data.append(player)
            time.sleep(self.delay)
        
        return pd.DataFrame(league_data)

    def _get_teams(self, league_url):
        """Get all teams in a league"""
        response = self.session.get(f"{self.base_url}{league_url}")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        teams = []
        table = soup.find('table', {'id': 'results2023-202491_overall'})
        for row in table.tbody.find_all('tr'):
            team_link = row.find('a', href=True)
            if team_link and 'squads' in team_link['href']:
                teams.append({
                    'name': team_link.text.strip(),
                    'url': team_link['href'],
                    'league': league_url.split('/')[-2]
                })
        return teams

    def _get_players(self, team_url):
        """Get all players from a team"""
        response = self.session.get(f"{self.base_url}{team_url}")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        players = []
        tables = {
            'standard': 'stats_standard_9',
            'shooting': 'stats_shooting_9',
            'passing': 'stats_passing_9'
        }
        
        # Get basic player info
        std_table = soup.find('table', {'id': tables['standard']})
        for row in std_table.tbody.find_all('tr'):
            cols = row.find_all(['th', 'td'])
            if len(cols) > 5:  # Minimum columns for valid player
                player = {
                    'fbref_id': cols[0].get('data-append-csv'),
                    'name': cols[0].text.strip(),
                    'position': cols[1].text.strip(),
                    'age': int(cols[2].text.split('-')[0]),
                    'minutes': int(cols[5].text.replace(',', '')) if cols[5].text else 0
                }
                players.append(player)
        
        # Enrich with advanced stats
        for stat_type in ['shooting', 'passing']:
            table = soup.find('table', {'id': tables[stat_type]})
            if table:
                for i, row in enumerate(table.tbody.find_all('tr')):
                    if i < len(players):
                        cols = row.find_all(['th', 'td'])
                        if stat_type == 'shooting':
                            players[i]['xg'] = float(cols[8].text) if cols[8].text else 0.0
                        elif stat_type == 'passing':
                            players[i]['xa'] = float(cols[15].text) if cols[15].text else 0.0
        
        return players