import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Predictor from './components/Predictor';
import Scout from './components/Scout';
import Navbar from './components/Navbar';

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <div className="container mt-4">
        <Routes>
          <Route path="/" element={<Predictor />} />
          <Route path="/scout" element={<Scout />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;