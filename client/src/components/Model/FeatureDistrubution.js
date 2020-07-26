import React, { Component } from 'react';
import DashWrapper from '../common/DashWrapper';

import Search from '../common/Search';
import ScoreInfo from '../common/ScoreInfo';
import PieChart from '../common/PieChart';
import { connect } from 'react-redux';
import {
  getIsEntitiesLoading,
  getIsEntityDistributionsLoading,
  getEntityDistributions,
} from '../../model/selectors/entities';
import { PercentageProgressBar } from '../common/ProgressBars';
import DayGraph from '../common/DayGraph';
import { getFeaturesData, getIsFeaturesLoading } from '../../model/selectors/features';
import './Model.scss';

// mock search result
const hayStack = [
  { feature: 'Child in focus had a prior court active child welfare case' },
  { feature: 'Child in focus is younger than 1 years old' },
  { feature: 'Feature #1' },
  { feature: 'Feature #2' },
  { feature: 'Feature #3' },
];

class FeatureDistribution extends Component {
  renderDashHeader() {
    return (
      <header className="dash-header">
        <ul className="dash-controls">
          <li>
            <Search hayStack={hayStack} />
          </li>
          <li>&nbsp;</li>
        </ul>
      </header>
    );
  }

  drawDistribution(currentFeature) {
    const { distributions } = this.props;
    if (distributions[currentFeature] === undefined) {
      return <p>No data to display</p>;
    }

    if (distributions[currentFeature] !== undefined && distributions[currentFeature].type === 'numeric') {
      const data = distributions[currentFeature].metrics;
      return <DayGraph data={data} graphIndex={currentFeature} />;
    }

    if (distributions[currentFeature].type === 'category') {
      const data = distributions[currentFeature].metrics;

      if (data[0].length === 1) {
        return <PercentageProgressBar negativeProgress={0} />;
      }

      const maxPercentage = data[1][0] + data[1][1];
      const negativeProgress = Math.floor((data[1][1] / maxPercentage) * 100);

      return <PercentageProgressBar negativeProgress={negativeProgress} />;
    }
  }

  render() {
    const { isDistributionsLoading, isEntityLoading, features, isFeaturesLoading } = this.props;
    const { processedFeatures } = features;
    const isDataLoading = isDistributionsLoading || isEntityLoading || isFeaturesLoading;

    return (
      <div className="component-wrapper">
        <table className="distrib-info">
          <tbody>
            <tr>
              <td>
                <ScoreInfo />
              </td>
              <td>
                <PieChart />
              </td>
            </tr>
          </tbody>
        </table>
        <DashWrapper>
          {this.renderDashHeader()}
          <div className="sticky-wrapper scroll-style">
            <table className="dash-table sticky-header">
              <thead>
                <tr>
                  <th>Feature</th>
                  <th width="25%" className="align-right">
                    Distribution of Values
                  </th>
                </tr>
              </thead>
              <tbody>
                {(!isDataLoading &&
                  processedFeatures.map((currentFeature, featureIndex) => (
                    <tr key={featureIndex}>
                      <td>{currentFeature.description}</td>
                      <td className="align-right">{this.drawDistribution(currentFeature.name)}</td>
                    </tr>
                  ))) || (
                  <tr>
                    <td colSpan="2">
                      <p>Loading...</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </DashWrapper>
      </div>
    );
  }
}

export default connect((state) => ({
  isFeaturesLoading: getIsFeaturesLoading(state),
  isEntityLoading: getIsEntitiesLoading(state),
  isDistributionsLoading: getIsEntityDistributionsLoading(state),
  distributions: getEntityDistributions(state),
  features: getFeaturesData(state),
}))(FeatureDistribution);
