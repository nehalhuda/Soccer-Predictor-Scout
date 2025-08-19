import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import axios from 'axios';

const Predictor = () => {
  const [teams, setTeams] = useState([]);
  const [players, setPlayers] = useState([]);
  const [homeTeam, setHomeTeam] = useState('');
  const [awayTeam, setAwayTeam] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Load initial data
    axios.get('http://localhost:5000/api/teams')
      .then(res => setTeams(res.data))
      .catch(err => console.error(err));
  }, []);

  const fetchFBrefData = () => {
    setIsLoading(true);
    axios.post('http://localhost:5000/api/fetch-fbref')
      .then(() => {
        alert('FBref data loaded successfully!');
        window.location.reload();
      })
      .catch(err => console.error(err))
      .finally(() => setIsLoading(false));
  };

  const predictMatch = () => {
    if (!homeTeam || !awayTeam) return;
    
    setIsLoading(true);
    axios.post('http://localhost:5000/api/predict', {
      home_team: homeTeam,
      away_team: awayTeam
    })
    .then(res => setPrediction(res.data))
    .catch(err => console.error(err))
    .finally(() => setIsLoading(false));
  };

  return (
    <div className="container mt-4">
      <button 
        onClick={fetchFBrefData} 
        className="btn btn-primary mb-4"
        disabled={isLoading}
      >
        {isLoading ? 'Loading...' : 'Load FBref Data'}
      </button>

      <div className="row mb-4">
        <div className="col-md-5">
          <select 
            className="form-select"
            value={homeTeam}
            onChange={(e) => setHomeTeam(e.target.value)}
          >
            <option value="">Select Home Team</option>
            {teams.map(team => (
              <option key={team.id} value={team.id}>{team.name}</option>
            ))}
          </select>
        </div>
        <div className="col-md-2 text-center">vs</div>
        <div className="col-md-5">
          <select 
            className="form-select"
            value={awayTeam}
            onChange={(e) => setAwayTeam(e.target.value)}
          >
            <option value="">Select Away Team</option>
            {teams.map(team => (
              <option key={team.id} value={team.id}>{team.name}</option>
            ))}
          </select>
        </div>
      </div>

      <button 
        onClick={predictMatch}
        className="btn btn-success mb-4"
        disabled={isLoading || !homeTeam || !awayTeam}
      >
        {isLoading ? 'Predicting...' : 'Predict Match'}
      </button>

      {prediction && (
        <div className="card">
          <div className="card-body">
            <h5 className="card-title">Prediction Results</h5>
            <Bar 
              data={{
                labels: ['Home Win', 'Draw', 'Away Win'],
                datasets: [{
                  label: 'Probability %',
                  data: [
                    prediction.home_win * 100,
                    prediction.draw * 100,
                    prediction.away_win * 100
                  ],
                  backgroundColor: [
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)',
                    'rgba(255, 99, 132, 0.5)'
                  ]
                }]
              }}
              options={{
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 100
                  }
                }
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Predictor;