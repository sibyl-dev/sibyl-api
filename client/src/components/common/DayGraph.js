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
    let axisGenerator = d3.axisBottom(xCoord).tickValues([0, data[2], data[3], maxData]);

    const min = xCoord(data[0]);

    const q1 = xCoord(data[1]);

    const median = xCoord(data[2]);

    const q3 = xCoord(data[3]);

    const max = xCoord(data[4]);

    let xMiddleDistFour = xCoord([data[3]]) / 2;

    const formatXTransDistFour = `translate(-${xMiddleDistFour}, -35)`;

    const formatXTickDistFour = `${data[0]} - ${data[3]}`;

    let xMiddleDistThree = (xCoord(data[4]) - xCoord(data[3])) / 2;

    const formatXTransDistThree = `translate(${xMiddleDistThree}, -35)`;

    const formatXTickDistThree = `${data[3]} - ${data[4]}`;

    const predictionCases = {
      distributionOne: {
        condition: [min, q1, median, q3].every((prediction) => prediction === 0),
        dashedSegment: [data[0], data[4]],
      },
      distributionTwo: {
        condition: min === 0 && q1 === 0 && median !== 0 && q3 !== 0 && max !== 0,
        dashedSegment: [data[0], data[2]],
      },
      distributionThree: {
        condition: min === 0 && q1 !== 0 && median !== 0 && q3 !== 0 && max !== 0,
        dashedSegment: [data[0], data[2]],
        xMiddle: xMiddleDistThree,
        formatX: formatXTransDistThree,
        formatTick: formatXTickDistThree,
      },
      distributionFour: {
        condition: min === 0 && q1 === 0 && median === 0 && q3 !== 0 && max !== 0,
        xMiddle: xMiddleDistFour,
        formatX: formatXTransDistFour,
        formatTick: formatXTickDistFour,
      },
    };

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

        if (currentTick === data[3] && predictionCases.distributionFour.condition) {
          return predictionCases.distributionFour.formatX;
        }

        if (
          currentTick === data[3] &&
          (predictionCases.distributionThree.condition || predictionCases.distributionTwo.condition)
        ) {
          return predictionCases.distributionThree.formatX;
        }

        return 'translate(0,-35)';
      })
      .attr('color', (currentTick) => {
        if (currentTick === data[3]) {
          return '#4F4F4F';
        }
        return '#828282';
      })
      .text((currentTick) => {
        if (currentTick === data[3] && predictionCases.distributionFour.condition) {
          return predictionCases.distributionFour.formatTick;
        }

        if (
          currentTick === data[3] &&
          (predictionCases.distributionThree.condition || predictionCases.distributionTwo.condition)
        ) {
          return predictionCases.distributionThree.formatTick;
        }

        return currentTick;
      });

    xAxis.select('.domain').attr('color', '#9B9FB3').attr('stroke-width', 2);

    xAxis
      .append('g')
      .attr('class', 'label')
      .append('text')
      .attr('x', xCoord(data[4]) + 38)
      .attr('y', 3.5)
      .attr('fill', 'rgba(155, 159, 179, 1')
      .attr('font-size', '14')
      .attr('transform', 'translate(20, 0)')
      .text('Value');

    const generateStrokeCoord = () => {
      const path = d3.select('.domain').node();

      const pathLength = path.getTotalLength();

      const segmentCoords = (segment) => {
        const segmentList = segment.map((segmentCoord) => {
          let beginning = 0;

          let end = pathLength;

          let target = null;

          segmentCoord = xCoord(segmentCoord);

          while (pathLength) {
            target = Math.floor((beginning + end) / 2);

            let svgPointPosition = path.getPointAtLength(target);

            if ((target === end || target === beginning) && svgPointPosition.x !== segmentCoord) {
              break;
            }

            if (svgPointPosition.x > segmentCoord) {
              end = target;
            } else if (svgPointPosition.x < segmentCoord) {
              beginning = target;
            } else break;
          }

          return target;
        });

        return segmentList;
      };

      const { distributionOne, distributionTwo, distributionThree } = predictionCases;

      const generateDashSegment = (distribution) => {
        let strokeDashArray = segmentCoords(distribution.dashedSegment)[0];

        let firstStrokeDashCoord = segmentCoords(distribution.dashedSegment)[0];

        while (firstStrokeDashCoord < segmentCoords(distribution.dashedSegment)[1]) {
          firstStrokeDashCoord += 4;
          strokeDashArray += ', 4';
        }

        let count = 0;

        let dashPatternEnd = pathLength - segmentCoords(distribution.dashedSegment)[1];

        if (count % 2 === 0) {
          strokeDashArray += ', 4';
          strokeDashArray += `, ${dashPatternEnd}`;
          count = +1;
        }

        return strokeDashArray;
      };

      switch (true) {
        case distributionOne.condition:
          return generateDashSegment(distributionOne);

        case distributionTwo.condition:
          return generateDashSegment(distributionTwo);

        case distributionThree.condition:
          return generateDashSegment(distributionThree);

        default:
          return null;
      }
    };

    xAxis.attr('stroke-dasharray', `${generateStrokeCoord()}`);

    xAxis
      .selectAll(`#_${graphIndex} .tick line`)
      .attr('stroke', (currentTick) => (currentTick === 0 || currentTick === maxData ? '#9B9FB3' : null))
      .attr('stroke-width', 2)
      .attr('transform', 'translate(0,-6)')
      .attr('stroke-dasharray', 0)
      .attr('y2', 12);
  }

  drawData(value) {
    const { xCoord } = this.getCoords();

    let width;

    let xPosition;

    const min = xCoord(value[0]);

    const q1 = xCoord(value[1]);

    const median = xCoord(value[2]);

    const q3 = xCoord(value[3]);

    const max = xCoord(value[4]);

    const predictionCases = {
      distributionOne: {
        condition: [min, q1, median, q3].every((prediction) => prediction === 0),
      },

      distributionTwo: {
        condition: min === 0 && q1 === 0 && median !== 0 && q3 !== 0 && max !== 0,
      },

      distributionThree: {
        condition: min === 0 && q1 !== 0 && median !== 0 && q3 !== 0 && max !== 0,
      },

      distributionFour: {
        condition: min === 0 && q1 === 0 && median === 0 && q3 !== 0 && max !== 0,
      },
    };

    const { distributionOne, distributionTwo, distributionThree, distributionFour } = predictionCases;

    if (distributionOne.condition) {
      // for hiding the start of segment
      const offsetValue = 0.5;

      width = 5;

      xPosition = xCoord([value[1]]) - offsetValue;
    }

    if (distributionTwo.condition) {
      // for hiding the end of segment
      const offsetValue = 1.5;

      width = xCoord(value[4]) - xCoord(value[3]) + offsetValue;

      xPosition = xCoord([value[3]]);
    }

    if (distributionThree.condition) {
      const offsetValue = 1.5;

      width = xCoord(value[4]) - xCoord(value[3]) + offsetValue;

      xPosition = xCoord([value[3]]);
    }

    if (distributionFour.condition) {
      const offsetValue = 1.5;

      width = xCoord(value[3]) - xCoord(value[1]);

      xPosition = xCoord([value[2]]) - offsetValue;
    }

    return (
      <rect
        width={width}
        height="20"
        fill="rgba(56, 63, 103, 1)"
        x={xPosition}
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
        <svg
          width={dimensions.width + 15}
          height={dimensions.height}
          id={`_${this.props.graphIndex}`}
          overflow="visible"
        >
          <g className="axis-x" />
          <g className="data">{this.drawData(data)}</g>
        </svg>
      )) || <p>No data to display.</p>
    );
  }
}

export default DayGraph;
