import React from 'react';
import './ProgressSlider.css';

function ProgressSlider({ name, value }) {
  return (
    <div className="progress-slider">
      <div className="slider-container">
        <div 
          className="slider-track"
          style={{ background: `linear-gradient(90deg, #4CAF50 0%, #4CAF50 ${value}%, #444 ${value}%, #444 100%)` }}
        >
          <span className="slider-label">{name}</span>
          <span className="slider-percentage">{value}%</span>
        </div>
      </div>
    </div>
  );
}

export default ProgressSlider;