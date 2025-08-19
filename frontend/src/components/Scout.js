import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Scout = () => {
  const [players, setPlayers] = useState([]);
  const [squad, setSquad] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:5000/api/players')
      .then(res => setPlayers(res.data));
  }, []);

  return (
    <div>
      <h2>Player Scout</h2>
      <div className="row">
        <div className="col-md-6">
          <h4>Available Players</h4>
          {players.map(player => (
            <div key={player.id}>{player.name} ({player.position})</div>
          ))}
        </div>
        <div className="col-md-6">
          <h4>Your Squad</h4>
          {squad.length === 0 && "No players selected"}
        </div>
      </div>
    </div>
  );
};

export default Scout;