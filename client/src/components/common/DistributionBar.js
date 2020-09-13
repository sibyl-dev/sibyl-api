import React from 'react';
import { v4 as uuidv4 } from 'uuid';
import MetTooltip from './MetTooltip';

import './styles/DistributionBar.scss';

const tooltipContent = ({ countsRatios }) => {
  return (
    <div className="tooltip-content">
      <div className="tooltip-header">
        <div>Category</div>
        <div>Distribution</div>
      </div>
      <hr />
      <ul className="tooltip-list">
        {countsRatios.map(({ style, ratio, name }) => {
          if (style !== undefined) {
            return (
              <li key={uuidv4()}>
                <span
                  className="tooltip-circle"
                  style={{
                    backgroundColor: `${style.color}`,
                    opacity: `${style.opacity}`,
                  }}
                ></span>
                <div className="tooltip-categ-name">{name}</div>
                <div key={uuidv4()} className="tooltip-categ-percent">
                  {ratio}%
                </div>
              </li>
            );
          } else {
            return null;
          }
        })}
      </ul>
    </div>
  );
};

const DistributionBar = ({ category, isBinary }) => {
  const { isLoading } = category;

  if (isLoading) {
    return null;
  }

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

  const clonedCategory = JSON.parse(JSON.stringify(category));

  clonedCategory.countsRatios.sort((a, b) => (a.ratio < b.ratio ? 1 : -1));

  clonedCategory.countsRatios = clonedCategory.countsRatios.map((count, index) => {
    return {
      ...count,
      style: ratiosStyle[index],
    };
  });

  const { countsRatios } = clonedCategory;

  const categoriesToRender = countsRatios.map(({ style, ratio }, index) => {
    //calculate ratios formula
    if (style !== undefined) {
      if (isBinary) {
        const setCategoryRef = (el) => {
          el.setAttribute('data-before', `${isBinary ? ratio : null}%`);
        };

        return (
          <React.Fragment key={uuidv4()}>
            <div
              ref={setCategoryRef}
              data-placement="top"
              className="binary-data"
              style={{
                width: `${ratio}%`,
              }}
            ></div>
          </React.Fragment>
        );
      } else {
        return (
          <React.Fragment key={uuidv4()}>
            <MetTooltip title={tooltipContent(clonedCategory)} placement="top" className="tooltip">
              <div
                data-placement="top"
                className="categorical-data"
                style={{
                  background: `${style.color}`,
                  width: `${ratio}%`,
                  opacity: `${style.opacity}`,
                }}
              ></div>
            </MetTooltip>
          </React.Fragment>
        );
      }
    } else {
      return null;
    }
  });

  if (isBinary) {
    return (
      <React.Fragment>
        <div className="binary-wrapper">
          <div className="binary-title-l">False</div>
          <div className="binary-bar">{categoriesToRender}</div>
          <div className="binary-title-r">True</div>
        </div>
      </React.Fragment>
    );
  } else {
    return (
      <React.Fragment>
        <div className="categorical-wrapper">
          <div className="categorical-bar">{categoriesToRender}</div>
        </div>
      </React.Fragment>
    );
  }
};

export default DistributionBar;
