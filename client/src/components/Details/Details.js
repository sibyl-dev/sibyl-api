import React from 'react';
import { TableFullIcon, TableSplitIcon } from '../../assets/icons/icons';

const Details = () => (
  <div>
    <div className="sub-header">
      <ul>
        <li>Risk Factors List</li>
        <li>
          <button type="button" className="view-full active">
            <TableFullIcon />
          </button>
          <button type="button" className="view-split">
            <TableSplitIcon />
          </button>
        </li>
      </ul>
    </div>
    <div className="component-wrapper no-shadow">
      <p>Details page here</p>
    </div>
  </div>
);

export default Details;
