import React from 'react';
import { TableFullIcon, TableSplitIcon } from '../../assets/icons/icons';
import './Header.scss';

const Header = () => {
  return (
    <div className="header">
      <div className="main-header">
        <ul>
          <li>
            <h2>Details</h2>
          </li>
          <li>
            Prediction Score: <strong>15</strong>
          </li>
        </ul>
      </div>
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
    </div>
  );
};

export default Header;
