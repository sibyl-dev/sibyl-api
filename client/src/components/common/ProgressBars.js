import React from 'react';
import * as d3 from 'd3';
import './styles/ProgressBars.scss';

const renderRightPercentage = (xCoord, yCoord, barWidth, barHeight) => {
  const radius = barHeight > barWidth ? barWidth / 2 : barHeight / 2;
  return `M ${xCoord}, ${yCoord}
            h  ${barWidth - radius}
            a  ${radius},  ${radius} 0 0 1 ${radius}, ${radius}
            v  ${barHeight - 2 * radius}
            a  ${radius}, ${radius} 0 0 1 -${radius}, ${radius}
            h  ${radius - barWidth}
            z`;
};

const renderLeftPercentage = (xCoord, yCoord, width, height) => {
  const radius = height < Math.abs(width) ? height / 2 : Math.abs(width) / 2;
  return `M ${xCoord}, ${yCoord}
            h ${width + radius}
            a ${radius}, ${radius} 0 0 0 -${radius}, ${radius}
            v ${height - 2 * radius}
            a ${radius}, ${radius} 0 0 0 ${radius}, ${radius}
            h ${-radius - width}
            z`;
};

const drawBar = (percentage, maxRange, width, height) => {
  var xCoord = d3.scaleLinear().domain([-maxRange, maxRange]).range([0, width]);

  const barWidth = xCoord(percentage) - xCoord(0);

  return barWidth >= 0
    ? renderRightPercentage(width / 2, height / 2, barWidth, height)
    : renderLeftPercentage(width / 2, height / 2, barWidth, height);
};

export const BiProgressBar = (props) => {
  let { percentage, maxRange, width, height } = props;
  percentage = Number(percentage);

  const getProgressBarClassName = (percentage) => (percentage > 0 ? 'bar-positive' : 'bar-negative');

  return (
    <svg width={width} height="18" className="bidi-progress-bar">
      <rect width={width} height={height} rx={height / 2} fill="rgba(189, 189, 189, 0.5)" y={height / 2} />
      <path d={drawBar(percentage, maxRange, width, height)} className={getProgressBarClassName(percentage)} />
      <rect className="separator" fill="#BDBDBD" x={width / 2} rx="1" ry="1" width="2" height={height} />
    </svg>
  );
};

export const PercentageProgressBar = ({ negativeProgress }) => {
  const positiveProgress = 100 - negativeProgress;
  return (
    <div className="percentage-progress-bar">
      <ul>
        <li>False</li>
        <li className="progress-info">
          <div>
            <span>{negativeProgress}%</span> <span>{positiveProgress}%</span>
          </div>
          <div>
            <div className="percentage-indicator">
              <div className="progress" style={{ width: `${negativeProgress}%` }} />
            </div>
          </div>
        </li>
        <li>True</li>
      </ul>
    </div>
  );
};

export const ProgressIndicator = ({ progressWidth }) => (
  <div className="percentage-indicator">
    <div className="progress" style={{ width: `${progressWidth}%` }} />
  </div>
);
