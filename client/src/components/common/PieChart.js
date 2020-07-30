import React from 'react';
import * as d3 from 'd3';
import GrayBoxWrapper from './GrayBoxWrapper';

import './styles/DonutChart.scss';

const childData = [
  { status: 'Removed from home', child: 'child', value: '200' },
  { status: 'Value #1', child: 'child', value: '200' },
  { status: 'Value #2', child: 'child', value: '200' },
  { status: 'Value #3', child: 'child', value: '200' },
  { status: 'Value #4', child: 'child', value: '200' },
];

const colors = [
  '#EB5757', // red
  '#F2C94C', // yellow
  '#F2994A', // orange
  '#27AE60', // green
  '#E0E0E0', // gray
];

const pie = d3
  .pie()
  .value((d) => d.value)
  .sort(null);

const chartSize = 112;
const radius = chartSize / 2;
const arc = d3
  .arc()
  .innerRadius(radius - 8)
  .outerRadius(radius - 2);

const drawArc = (index) => {
  const arcData = pie(childData);
  return arc(arcData[index]);
};

const PieChart = () => (
  <GrayBoxWrapper>
    <div className="donut-chart">
      <div className="chart">
        <svg id="piechart" width={chartSize} height={chartSize}>
          <g transform={`translate(${chartSize / 2}, ${chartSize / 2})`}>
            {childData.map((currentChild, childIndex) => (
              <path key={currentChild.status} d={drawArc(childIndex)} fill={colors[childIndex]} />
            ))}
          </g>
        </svg>
      </div>
      <div className="legend">
        <ul>
          {childData.map((currentChild, childIndex) => (
            <li key={currentChild.status}>
              <i style={{ background: colors[childIndex] }} />
              {currentChild.status}
            </li>
          ))}
        </ul>
      </div>
    </div>
  </GrayBoxWrapper>
);

export default PieChart;
