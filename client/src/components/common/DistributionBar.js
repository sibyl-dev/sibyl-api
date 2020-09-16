import React from 'react';
import { v4 as uuidv4 } from 'uuid';
import MetTooltip from './MetTooltip';

import './styles/DistributionBar.scss';

const DistributionBar = ({ metrics, isBinary }) => {
  const { isLoading } = metrics;

  if (isLoading) {
    return null;
  }

  const clonedMetrics = JSON.parse(JSON.stringify(metrics));

  let { metricsRatios } = clonedMetrics;

  metricsRatios = metricsRatios
    .map((metric) => {
      const { ratio } = metric;

      const roundDownRatio = Math.floor(ratio);
      const ratioDecimals = ratio - Math.floor(ratio);

      return {
        ...metric,
        ratioDown: roundDownRatio,
        decimals: ratioDecimals,
      };
    })
    .sort((a, b) => (a.decimals < b.decimals ? 1 : -1));

  const calcSumDiff = 100 - metricsRatios.reduce((acc, metric) => acc + metric.ratioDown, 0);

  metricsRatios = metricsRatios.map((metric) => {
    metric.sumDiff = calcSumDiff;

    return {
      ...metric,
    };
  });

  const sumDiffValue = metricsRatios[0].sumDiff;

  for (let i = 0; i < sumDiffValue; i += 1) {
    metricsRatios[i].ratioDown += 1;
  }

  const filteredMetrics = metricsRatios.filter((metric) => {
    //  check if ratios are a pair of 100 and 0

    let { ratioDown } = metric;

    if (metricsRatios.length === 2) {
      if (ratioDown === 100) {
        ratioDown = '~100%';
        return metric;
      }

      if (ratioDown === 0) {
        ratioDown = '~0%';
        return metric;
      }
    }
    return metric;
  });

  const formattedMetrics = filteredMetrics
    .map((metric) => {
      const { ratioDown } = metric;

      const metricTitlePercent = ratioDown === '~100%' || ratioDown === '~0%' ? ratioDown : `${ratioDown}%`;

      const metricWidthPercent =
        ratioDown === '~100%' || ratioDown === '~0%' ? ratioDown.substring(1) : `${ratioDown}%`;

      metric.metricTitlePercent = metricTitlePercent;
      metric.metricWidthPercent = metricWidthPercent;

      return metric;
    })
    .sort((a, b) => (a.ratioDown < b.ratioDown ? 1 : -1));

  const styledBars = formattedMetrics.map((bar, index) => {
    const ratiosStyle = [
      {
        color: '#383F67',
        opacity: '1',
      },
      {
        color: '#383F67',
        opacity: '0.85',
      },
      {
        color: '#383F67',
        opacity: '0.7',
      },
      {
        color: '#383F67',
        opacity: '0.55',
      },
      {
        color: '#383F67',
        opacity: '0.3',
      },
      {
        color: '#383F67',
        opacity: '0.15',
      },
    ];

    return {
      ...bar,
      style: ratiosStyle[index],
    };
  });

  const barsToRender = styledBars.map((bar, index, { length }) => {
    const { style, metricTitlePercent } = bar;

    let { metricWidthPercent } = bar;

    if (style !== undefined) {
      if (isBinary) {
        const setBinaryDataTitle = (el) => {
          if (el !== null) {
            el.setAttribute('data-before', metricTitlePercent);
          }
        };

        return (
          <React.Fragment key={uuidv4()}>
            <div
              ref={setBinaryDataTitle}
              data-placement="top"
              className="binary-data"
              style={{
                width: metricWidthPercent,
              }}
            />
          </React.Fragment>
        );
      }

      {
        const tooltipContent = () => (
          <div className="tooltip-content">
            <div className="tooltip-header">
              <div>Category</div>
              <div>Distribution</div>
            </div>
            <hr />
            <ul className="tooltip-list">
              {styledBars.map((tooltipBar) => {
                const { style: tooltipStyle, metricTitlePercent: tooltipBarPercent, name: tooltipBarName } = tooltipBar;

                if (tooltipStyle !== undefined) {
                  return (
                    <li key={uuidv4()}>
                      <span
                        className="tooltip-circle"
                        style={{
                          backgroundColor: `${tooltipStyle.color}`,
                          opacity: `${tooltipStyle.opacity}`,
                        }}
                      />
                      <div className="tooltip-categ-name">{tooltipBarName}</div>
                      <div key={uuidv4()} className="tooltip-categ-percent">
                        {tooltipBarPercent === '0%' ? `~${tooltipBarPercent}` : tooltipBarPercent}
                      </div>
                    </li>
                  );
                }
                return null;
              })}
            </ul>
          </div>
        );

        const lastBarWidth = styledBars[length - 1].metricWidthPercent;

        const secondToLastBarWidth = styledBars[length - 2].metricWidthPercent;

        const barIsOnePercent = (currentValue) => currentValue === '1%';

        const areLastBarsEqual = [lastBarWidth, secondToLastBarWidth].every(barIsOnePercent);

        const increasedSecondToLastBarWidth = `${parseInt(secondToLastBarWidth.charAt(0), 10) + 0.5}%`;

        if (areLastBarsEqual) {
          styledBars[length - 2].metricWidthPercent = increasedSecondToLastBarWidth;
        }

        const minBarWidth = metricWidthPercent !== '0%';

        if (minBarWidth) {
          return (
            <React.Fragment key={uuidv4()}>
              <MetTooltip title={tooltipContent()} placement="top" className="tooltip">
                <div
                  data-placement="top"
                  className="categorical-data"
                  style={{
                    background: `${style.color}`,
                    width: metricWidthPercent,
                    opacity: `${style.opacity}`,
                  }}
                />
              </MetTooltip>
            </React.Fragment>
          );
        }
        return null;
      }
    }
    return null;
  });

  if (isBinary) {
    return (
      <>
        <div className="binary-wrapper">
          <div className="binary-title-l">False</div>
          <div className="binary-bar">{barsToRender}</div>
          <div className="binary-title-r">True</div>
        </div>
      </>
    );
  }

  return (
    <>
      <div className="categorical-wrapper">
        <div className="categorical-bar">{barsToRender}</div>
      </div>
    </>
  );
};

export default DistributionBar;
