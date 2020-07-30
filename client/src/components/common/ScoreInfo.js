import React, { Component } from 'react';
import { connect } from 'react-redux';
import GrayBoxWrapper from './GrayBoxWrapper';
import { setPredictionScoreAction } from '../../model/actions/entities';
import { getActivePredictionScore, getIsEntitiesLoading } from '../../model/selectors/entities';
import './styles/ScoreInfo.scss';

const scoreValues = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20];

class ScoreInfo extends Component {
  componentDidMount() {
    const { activeScore, setActiveScore } = this.props;

    activeScore !== null && setActiveScore(activeScore);
  }

  componentDidUpdate(nextState) {
    const { activeScore, setActiveScore } = this.props;

    if (nextState.activeScore !== activeScore) {
      setActiveScore(activeScore);
    }
  }

  renderScoreScale() {
    const { activeScore, setActiveScore } = this.props;
    const renderValues = () =>
      scoreValues.map((currentValue, index) => {
        const activeIndex = scoreValues.indexOf(activeScore);
        const getItemsClassNames = () => {
          if (index === activeIndex) {
            return 'active';
          }
          if (index === activeIndex - 1 || index === activeIndex + 1) {
            return 'active-neighbor';
          }
          return null;
        };
        return (
          <li key={currentValue} className={getItemsClassNames()} onClick={() => setActiveScore(currentValue)}>
            {currentValue}
          </li>
        );
      });

    return (
      <div className="score">
        <div className="score-scale">
          <ul className="score-values">{renderValues()}</ul>
          <div className="progress" />
        </div>
      </div>
    );
  }

  render() {
    const { activeScore } = this.props;

    return (
      <GrayBoxWrapper>
        <div className="score-wrapper">
          <header>
            <ul>
              <li>
                <h4>Show info about children who scored</h4>
              </li>
              <li>
                <span>
                  Score <strong>{activeScore}</strong>
                </span>
              </li>
            </ul>
          </header>
          <div>{this.renderScoreScale()}</div>
        </div>
      </GrayBoxWrapper>
    );
  }
}

export default connect(
  (state) => ({
    activeScore: getActivePredictionScore(state),
    isEntitiesLoading: getIsEntitiesLoading(state),
  }),
  (dispatch) => ({
    setActiveScore: (score) => dispatch(setPredictionScoreAction(score)),
  }),
)(ScoreInfo);
