import React, { Component } from 'react';
import * as d3 from 'd3';
import { connect } from 'react-redux';
import GrayBoxWrapper from './GrayBoxWrapper';

import { getCurrentOutcomeData, getIsOutcomeDataLoading } from '../../model/selectors/entities';
import { getOutcomeCountAction } from '../../model/actions/entities';
import './styles/DonutChart.scss';

const childData = [{ status: 'Removed from Home' }, { status: 'Not removed from home' }];

const colors = [
  '#EB5757', // red
  '#E0E0E0', // gray
  // '#F2C94C', // yellow
  // '#F2994A', // orange
  // '#27AE60', // green
];

const pie = d3
  .pie()
  .value((data) => data)
  .sort(null);

const chartSize = 112;
const radius = chartSize / 2;
const arc = d3
  .arc()
  .innerRadius(radius - 10)
  .outerRadius(radius - 2);

const getPercentage = (total, value) => ((value / total) * 100).toFixed(2);

class PieChart extends Component {
  componentDidMount() {
    this.props.getOutcomeData();
  }

  drawChart() {
    const { currentOutcomeData } = this.props;
    const data = Object.values(currentOutcomeData)[0].metrics;
    const maxRadius = data[1][0];
    const drawing = data[1][1];
    const arcData = pie([drawing, maxRadius]);
    const percentage = getPercentage(maxRadius + drawing, drawing);

    return (
      <div className="donut">
        <svg width={chartSize} height={chartSize}>
          <g transform={`translate(${chartSize / 2}, ${chartSize / 2})`}>
            {arcData.map((currentData, index) => (
              <g key={currentData.data}>
                <path d={arc(currentData)} fill={index === 0 ? '#EB5757' : '#E0E0E0'} key={currentData.data} />
              </g>
            ))}
          </g>
        </svg>
        <span className="percentage">{percentage}%</span>
      </div>
    );
  }

  render() {
    const { isOutcomeDataLoading } = this.props;
    return (
      <GrayBoxWrapper>
        <div className="donut-chart">
          <div className="chart">{!isOutcomeDataLoading && this.drawChart()}</div>
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
  }
}

export default connect(
  (state) => ({
    isOutcomeDataLoading: getIsOutcomeDataLoading(state),
    currentOutcomeData: getCurrentOutcomeData(state),
  }),
  (dispatch) => ({
    getOutcomeData: () => dispatch(getOutcomeCountAction()),
  }),
)(PieChart);
