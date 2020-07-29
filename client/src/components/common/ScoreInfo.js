import React, { Component } from 'react';
import './styles/ScoreInfo.scss';
import GrayBoxWrapper from './GrayBoxWrapper';

const values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20];

class SoreInfo extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activeScore: 10,
    };
  }

  setActiveScore(score) {
    this.setState({
      activeScore: score,
    });
  }

  renderScoreScale() {
    const { activeScore } = this.state;
    const renderValues = () =>
      values.map((currentValue, index) => {
        const activeIndex = values.indexOf(activeScore);
        const getItemsClassNames = () => {
          if (index === activeIndex) {
            return 'active';
          }
          if (index === activeIndex - 1 || index === activeIndex + 1) {
            return 'active-neighbor';
          }
        };
        return (
          <li key={currentValue} className={getItemsClassNames()} onClick={() => this.setActiveScore(currentValue)}>
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
    const { activeScore } = this.state;
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

export default SoreInfo;
