import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-success shadow-sm">
      <div className="container">
        {/* Brand Logo */}
        <Link className="navbar-brand fw-bold" to="/">
          ⚽ SoccerPredictor
        </Link>
        
        {/* Mobile Toggle Button */}
        <button 
          className="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        {/* Navigation Items */}
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            {/* Match Predictor Link */}
            <li className="nav-item">
              <Link 
                className={`nav-link ${location.pathname === '/' ? 'active fw-bold' : ''}`}
                to="/"
              >
                🎯 Match Predictor
              </Link>
            </li>
            
            {/* Team Scout Link */}
            <li className="nav-item">
              <Link 
                className={`nav-link ${location.pathname === '/scout' ? 'active fw-bold' : ''}`}
                to="/scout"
              >
                🔍 Team Scout
              </Link>
            </li>
            
            {/* Data Status Link */}
            <li className="nav-item">
              <Link 
                className={`nav-link ${location.pathname === '/data' ? 'active fw-bold' : ''}`}
                to="/data"
              >
                📊 Data Status
              </Link>
            </li>
          </ul>

          {/* Right-side Items */}
          <ul className="navbar-nav">
            <li className="nav-item">
              <span className="nav-link text-light">
                📈 Powered by FBref
              </span>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;