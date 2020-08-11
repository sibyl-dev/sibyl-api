import React, { useState } from 'react';
import { connect } from 'react-redux';
import { ExcamationIcon } from '../../assets/icons/icons';
import { getPageName } from '../../model/selectors/sidebar';
import { getIsEntityScoreLoading, getEntityScore } from '../../model/selectors/entities';
import ModalDialog from '../common/ModalDialog';
import './Header.scss';

const toggleModalDialog = (modalState, onClose) => (
  <ModalDialog isOpen={modalState} onClose={onClose} title="Risk Score">
    <p>
      This is the risk score prediction for this child. The scores range from 1 to 20. The higher the risk score, the
      higher the chance of placement. A score of **1** therefore represents the bottom 5% of risk among referred
      children, and a **20** represents the top 5%.
    </p>
  </ModalDialog>
);

const Header = (props) => {
  const { isEntityScoreLoading, entityScore, currentPage } = props;
  const [isModalOpen, toggleModal] = useState(false);
  const excludedPages = ['Global Feature Importance', 'Feature Distribution'];
  let isRiskScoreVisible = !excludedPages.includes(currentPage);

  return (
    <div className="header">
      <div className="main-header">
        <ul>
          <li>
            <h2>{props.pageName}</h2>
          </li>
          <li>
            {!isEntityScoreLoading && isRiskScoreVisible && (
              <span>
                Risk Score: <strong>{entityScore}</strong>
                <button type="button" className="clean" onClick={() => toggleModal(true)}>
                  <ExcamationIcon />
                </button>
              </span>
            )}
          </li>
        </ul>
      </div>
      {toggleModalDialog(isModalOpen, toggleModal)}
    </div>
  );
};
export default connect((state) => ({
  pageName: getPageName(state),
  isEntityScoreLoading: getIsEntityScoreLoading(state),
  entityScore: getEntityScore(state),
  currentPage: getPageName(state),
}))(Header);
