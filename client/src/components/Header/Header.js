import React from 'react';
import { connect } from 'react-redux';
import { ExcamationIcon } from '../../assets/icons/icons';
import { getPageName } from '../../model/selectors/sidebar';
import { getIsEntityScoreLoading, getEntityScore } from '../../model/selectors/entities';
import './Header.scss';

const Header = (props) => {
  const { isEntityScoreLoading, entityScore } = props;

  return (
    <div className="header">
      <div className="main-header">
        <ul>
          <li>
            <h2>{props.pageName}</h2>
          </li>
          <li>
            {!isEntityScoreLoading && (
              <span>
                Risk Score: <strong>{entityScore}</strong>
                <button type="button" className="clean">
                  <ExcamationIcon />
                </button>
              </span>
            )}
          </li>
        </ul>
      </div>
    </div>
  );
};
export default connect((state) => ({
  pageName: getPageName(state),
  isEntityScoreLoading: getIsEntityScoreLoading(state),
  entityScore: getEntityScore(state),
}))(Header);
