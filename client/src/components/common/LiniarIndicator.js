import React from 'react';
import './styles/LiniarIndicator.scss';

const LiniarIndicator = ({ percentageLeft, percentaceRight }) => (
  <div className="percentage-indicator">
    <div className="left-percentage" style={{ width: `${percentageLeft}%` }}></div>
    <div className="separator"></div>
    <div className="right-percentage" style={{ width: `${percentaceRight}%` }}></div>
  </div>
);

export default LiniarIndicator;
