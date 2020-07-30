import React, { Component } from 'react';
import * as d3 from 'd3';

const dimensions = {
  width: 250,
  height: 80,
  margin: 25,
};

class DayGraph extends Component {
  componentDidMount() {
    this.renderAxis();
  }

  getCoords() {
    const { data } = this.props;
    const maxData = data[data.length - 1];
    const { width, margin } = dimensions;
    const xCoord = d3
      .scaleLinear()
      .domain([0, maxData])
      .range([0, width - margin * 2]);
    return { xCoord };
  }

  renderAxis() {
    const { data, graphIndex } = this.props;
    const maxData = data[data.length - 1];

    const { xCoord } = this.getCoords();
    let axisGenerator = d3.axisBottom(xCoord).tickValues([0, data[1], data[3], maxData]);
    const xAxis = d3.select(`#_${graphIndex} .axis-x`).attr('transform', 'translate(25,35)').call(axisGenerator);

    xAxis
      .selectAll(`#_${graphIndex} .tick text`)
      .attr('font-size', '14')
      .attr('font-family', 'Roboto')
      .attr('transform', (currentTick) => {
        if (currentTick === 0) {
          return 'translate(-15, -15)';
        }

        if (currentTick === maxData) {
          return 'translate(20, -15)';
        }

        return 'translate(0,-35)';
      })
      .attr('color', '#828282');

    xAxis.select('.domain').attr('color', '#828282').attr('stroke-width', 2);

    xAxis
      .selectAll(`#_${graphIndex} .tick line`)
      .attr('stroke', (currentTick) => (currentTick === 0 || currentTick === maxData ? '#828282' : null))
      .attr('stroke-width', 2)
      .attr('transform', 'translate(0,-6)');
  }

  drawData(value) {
    const { xCoord } = this.getCoords();
    const width = xCoord(value[3]) - xCoord(value[1]);
    if (value[3] === 0) {
      return null;
    }

    return (
      <rect
        width={width}
        height="20"
        fill="rgba(129, 104, 231, 0.5)"
        x={xCoord([value[1]])}
        rx="2"
        ry="2"
        transform="translate(25, 25)"
      />
    );
  }

  render() {
    const { data } = this.props;
    return (
      (data[4] !== 0 && (
        <svg width={dimensions.width + 15} height={dimensions.height} id={`_${this.props.graphIndex}`}>
          <g className="axis-x" />
          <g className="data">{this.drawData(data)}</g>
        </svg>
      )) || <p>No data to display.</p>
    );
  }
}

export default DayGraph;
