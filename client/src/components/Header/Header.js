import React from 'react';
import { ExcamationIcon } from '../../assets/icons/icons';
import './Header.scss';
import { connect } from 'react-redux';
import { getPageName } from '../../model/selectors/sidebar';

const Header = (props) => {
  return (
    <div className="header">
      <div className="main-header">
        <ul>
          <li>
            <h2>{props.pageName}</h2>
          </li>
          <li>
            Prediction Score: <strong>15</strong>
            <button type="button" className="clean">
              <ExcamationIcon />
            </button>
          </li>
        </ul>
      </div>
    </div>
  );
};
export default connect((state) => ({ pageName: getPageName(state) }))(Header);
