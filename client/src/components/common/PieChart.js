import React, { Component } from 'react';
import * as d3 from 'd3';
import { connect } from 'react-redux';
import GrayBoxWrapper from './GrayBoxWrapper';

import { getCurrentOutcomeData, getIsOutcomeDataLoading } from '../../model/selectors/entities';
import { getOutcomeCountAction } from '../../model/actions/entities';
import './styles/DonutChart.scss';

const childData = [
  { status: 'Removed from home', child: 'child', value: '200' },
  // { status: 'Value #1', child: 'child', value: '200' },
  // { status: 'Value #2', child: 'child', value: '200' },
  // { status: 'Value #3', child: 'child', value: '200' },
  // { status: 'Value #4', child: 'child', value: '200' },
];

const colors = [
  '#EB5757', // red
  // '#F2C94C', // yellow
  // '#F2994A', // orange
  // '#27AE60', // green
  // '#E0E0E0', // gray
];

const pie = d3
  .pie()
  .value((data) => data)
  .sort(null);

const chartSize = 112;
const radius = chartSize / 2;
const arc = d3
  .arc()
  .innerRadius(radius - 8)
  .outerRadius(radius - 2);

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

    return (
      <svg width={chartSize} height={chartSize}>
        <g transform={`translate(${chartSize / 2}, ${chartSize / 2})`}>
          {arcData.map((currentData, index) => (
            <path d={arc(currentData)} fill={index === 0 ? '#EB5757' : '#E0E0E0'} key={currentData.data} />
          ))}
        </g>
      </svg>
    );
  }

  render() {
    const { isOutcomeDataLoading } = this.props;
    return (
      <GrayBoxWrapper>
        <div className="donut-chart">
          <div className="chart">{!isOutcomeDataLoading && this.drawChart()}</div>
          <div className="legend">
            {/* @TODO - to be implemented, currently there's one single cathegory: PRO_PLSM_NEXT730_DUMMY */}
            <ul>
              {childData.map((currentChild, childIndex) => (
                <li key={currentChild.status}>
                  <i style={{ background: colors[childIndex] }} />
                  Taken from Home
                </li>
              ))}
              <li>
                <i style={{ backgroundColor: '#E0E0E0' }} />
                No removed from home
              </li>
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
