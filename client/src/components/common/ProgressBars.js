import React from 'react';
import * as d3 from 'd3';
import { ArrowIcon } from '../../assets/icons/icons';
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

const drawBar = (percentage, maxRange, width, height, isSingle) => {
  let xCoord = d3
    .scaleLinear()
    .domain([isSingle ? 0 : -maxRange, maxRange])
    .range([0, width]);

  const barWidth = xCoord(percentage) - xCoord(0);

  return barWidth >= 0
    ? renderRightPercentage(isSingle ? 0 : width / 2, height / 2, barWidth, height)
    : renderLeftPercentage(isSingle ? width : width / 2, height / 2, barWidth, height);
};

export const BiProgressBar = (props) => {
  let { percentage, maxRange, width, height } = props;
  let isSingle = props.isSingle || false;
  percentage = Number(percentage);
  const svgHeight = Math.abs(height) + 10;
  const getProgressBarClassName = (currPercentage) => (currPercentage >= 0 ? 'bar-positive' : 'bar-negative');

  return (
    <ul className="bidi-wrapper">
      <li>{!isSingle && <ArrowIcon dir="down" />}</li>
      <li>
        <svg width={width} height={svgHeight} className="bidi-progress-bar">
          <defs>
            <clipPath id="focusClip">
              <rect width={width} height={height} rx={height / 2} y={height / 2} />
            </clipPath>
          </defs>
          <rect width={width} height={height} rx={height / 2} fill="rgba(189, 189, 189, 0.5)" y={height / 2} />
          <g clipPath="url(#focusClip)">
            <path
              d={drawBar(percentage, maxRange, width, height, isSingle)}
              className={getProgressBarClassName(percentage)}
            />
          </g>
          {!isSingle && <rect className="separator" fill="#BDBDBD" x={width / 2} width="2" height={svgHeight} />}
        </svg>
      </li>
      <li>
        {!isSingle && <ArrowIcon dir="up" />}
        {isSingle && percentage < 0 && <ArrowIcon dir="down" />}
        {isSingle && percentage > 0 && <ArrowIcon dir="up" />}
      </li>
    </ul>
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

export const ProgressIndicator = ({ maxValue, progressWidth }) => {
  const width = (progressWidth * 100) / maxValue;
  return (
    <div className="percentage-indicator">
      <div className="progress" style={{ width: `${width}%` }} />
    </div>
  );
};
