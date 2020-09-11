import React from 'react';
import { v4 as uuidv4 } from 'uuid';
import MetTooltip from '../common/MetTooltip';

import './styles/CategoricalBar.scss';

const tooltipContent = ({ countsRatios }) => {
  return (
    <div className="tooltip-content">
      <div className="tooltip-header">
        <div>Category</div>
        <div>Distribution</div>
      </div>
      <hr />
      <ul className="tooltip-list">
        {countsRatios.map(({ style, ratio }) => {
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
                <span className="tooltip-categ-name">{'category.name'}</span>
                <span key={uuidv4()} className="tooltip-categ-percent">
                  {ratio}%
                </span>
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

const CategoricalBar = ({ category }) => {
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

  const categoriesToRender = countsRatios.map(({ style, ratio }) => {
    if (style !== undefined) {
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
    } else {
      return null;
    }
  });

  return <div className="categorical-bar">{categoriesToRender}</div>;
};

export default CategoricalBar;
