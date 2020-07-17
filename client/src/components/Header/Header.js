import React from 'react';
import { ExcamationIcon } from '../../assets/icons/icons';
import { connect } from 'react-redux';
import { getPageName } from '../../model/selectors/sidebar';
import { getCurrentEntityData, getIsEntitiesLoading } from '../../model/selectors/entities';
import './Header.scss';

const Header = (props) => {
  const { isEntityDataLoading, entityData } = props;

  return (
    <div className="header">
      <div className="main-header">
        <ul>
          <li>
            <h2>{props.pageName}</h2>
          </li>
          <li>
            {!isEntityDataLoading && (
              <span>
                Prediction Score: <strong>{entityData.score}</strong>
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
  isEntityDataLoading: getIsEntitiesLoading(state),
  entityData: getCurrentEntityData(state),
}))(Header);
