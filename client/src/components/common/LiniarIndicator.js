import React from 'react';
import './styles/LiniarIndicator.scss';

export const LiniarIndicator = ({ percentageLeft, percentageRight }) => (
  <div className="percentage-indicator">
    <div className="left-percentage" style={{ width: `${percentageLeft}%` }} />
    <div className="separator" />
    <div className="right-percentage" style={{ width: `${percentageRight}%` }} />
  </div>
);

export const ProgressIndicator = ({ progressWidth }) => (
  <div className="percentage-indicator">
    <div className="progress" style={{ width: progressWidth }} />
  </div>
);
