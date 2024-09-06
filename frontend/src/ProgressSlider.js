import React from 'react';
import './ProgressSlider.css';

function ProgressSlider({ name, value }) {
  return (
    <div className="progress-slider">
      <label>{name}</label>
      <div className="slider-container">
        <div className="slider-track">
          <div className="slider-fill" style={{ width: `${value}%` }}></div>
        </div>
        <span className="slider-value">{value}%</span>
      </div>
    </div>
  );
}

export default ProgressSlider;