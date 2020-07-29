import React from 'react';
import './styles/LiniarIndicator.scss';

export const LiniarIndicator = ({ percentageLeft, percentageRight, percentage }) => (
  <div className="percentage-indicator">
    <div className="left-percentage" style={{ width: `${percentageLeft}%` }}></div>
    <div className="separator"></div>
    <div className="right-percentage" style={{ width: `${percentageRight}%` }}></div>
  </div>
);

export const ProgressIndicator = ({ progressWidth }) => (
  <div className="percentage-indicator">
    <div className="progress" style={{ width: progressWidth }} />
  </div>
);
