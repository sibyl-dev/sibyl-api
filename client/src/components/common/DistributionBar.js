import React from 'react';
import { v4 as uuidv4 } from 'uuid';
import MetTooltip from './MetTooltip';

import './styles/DistributionBar.scss';

const DistributionBar = ({ category, isBinary }) => {
  const { isLoading } = category;

  if (isLoading) {
    return null;
  }

  const clonedCategory = JSON.parse(JSON.stringify(category));

  let { countsRatios } = clonedCategory;

  countsRatios = countsRatios.map((count) => {
    const roundDownRatio = Math.floor(count.ratio);
    const ratioDecimals = count.ratio - Math.floor(count.ratio);

    return {
      ...count,
      ratioDown: roundDownRatio,
      decimals: ratioDecimals,
    };
  });

  countsRatios.sort((a, b) => (a.decimals < b.decimals ? 1 : -1));

  const calcSumDiff = 100 - countsRatios.reduce((acc, val) => acc + val.ratioDown, 0);

  countsRatios = countsRatios.map((count) => {
    count.sumDiff = calcSumDiff;

    return {
      ...count,
    };
  });

  const sumDiffValue = countsRatios[0].sumDiff;

  for (let i = 0; i < sumDiffValue; i += 1) {
    countsRatios[i].ratioDown += 1;
  }

  const filteredRatios = countsRatios.filter((count) => {
    //  check if ratios are a pair of 100 and 0

    if (countsRatios.length === 2) {
      if (count.ratioDown === 100) {
        count.ratioDown = `~100%`;
        return count;
      }

      if (count.ratioDown === 0) {
        count.ratioDown = `~0%`;
        return count;
      }
    }
    return count;
  });

  const titleWidthRatios = filteredRatios.map((count) => {
    const { ratioDown } = count;

    const ratioTitlePercent = ratioDown === '~100%' || ratioDown === '~0%' ? ratioDown : `${ratioDown}%`;

    const ratioWidthPercent = ratioDown === '~100%' || ratioDown === '~0%' ? ratioDown.substring(1) : `${ratioDown}%`;

    count.ratioTitlePercent = ratioTitlePercent;
    count.ratioWidthPercent = ratioWidthPercent;

    return count;
  });

  titleWidthRatios.sort((a, b) => (a.ratioDown < b.ratioDown ? 1 : -1));

  const styledRatios = titleWidthRatios.map((count, index) => {
    const baseColor = '#383F67';

    const ratiosStyle = [
      {
        color: baseColor,
        opacity: '1',
      },
      {
        color: baseColor,
        opacity: '0.85',
      },
      {
        color: baseColor,
        opacity: '0.7',
      },
      {
        color: baseColor,
        opacity: '0.55',
      },
      {
        color: baseColor,
        opacity: '0.3',
      },
      {
        color: baseColor,
        opacity: '0.15',
      },
    ];

    return {
      ...count,
      style: ratiosStyle[index],
    };
  });

  const barsToRender = styledRatios.map((count) => {
    const { style, ratioTitlePercent, ratioWidthPercent } = count;

    if (style !== undefined) {
      if (isBinary) {
        const setBinaryDataTitle = (el) => {
          if (el !== null) {
            el.setAttribute('data-before', ratioTitlePercent);
          }
        };

        return (
          <React.Fragment key={uuidv4()}>
            <div
              ref={setBinaryDataTitle}
              data-placement="top"
              className="binary-data"
              style={{
                width: ratioWidthPercent,
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
              {styledRatios.map((count) => {
                const { style, ratioTitlePercent, name } = count;

                if (style !== undefined) {
                  return (
                    <li key={uuidv4()}>
                      <span
                        className="tooltip-circle"
                        style={{
                          backgroundColor: `${style.color}`,
                          opacity: `${style.opacity}`,
                        }}
                      />
                      <div className="tooltip-categ-name">{name}</div>
                      <div key={uuidv4()} className="tooltip-categ-percent">
                        {ratioTitlePercent === '0%' ? `~${ratioTitlePercent}` : ratioTitlePercent}
                      </div>
                    </li>
                  );
                }
                return null;
              })}
            </ul>
          </div>
        );

        const minBarWidth = ratioWidthPercent !== '0%';

        if (minBarWidth) {
          return (
            <React.Fragment key={uuidv4()}>
              <MetTooltip title={tooltipContent()} placement="top" className="tooltip">
                <div
                  data-placement="top"
                  className="categorical-data"
                  style={{
                    visibility: `${ratioWidthPercent === '0%' ? 'hidden' : ''}`,
                    background: `${style.color}`,
                    width: ratioWidthPercent,
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
