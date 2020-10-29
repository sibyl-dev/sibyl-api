import React, { Component } from 'react';
import { connect } from 'react-redux';

import DashWrapper from '../common/DashWrapper';

import Search from '../common/Search';
import ScoreInfo from '../common/ScoreInfo';
import PieChart from '../common/PieChart';
import {
  getIsEntitiesLoading,
  getIsEntityDistributionsLoading,
  getEntityDistributions,
} from '../../model/selectors/entities';

import { PercentageProgressBar } from '../common/ProgressBars';
import DayGraph from '../common/DayGraph';
import DistributionBar from '../common/DistributionBar';
import { getFeaturesData, getIsFeaturesLoading } from '../../model/selectors/features';
import { setUserActionRecording } from '../../model/actions/userActions';
import Loader from '../common/Loader';
import { setActivePageAction } from '../../model/actions/sidebar';
import './Model.scss';

class FeatureDistribution extends Component {
  componentDidMount() {
    const userData = {
      element: 'feature_distribution',
      action: 'click',
    };
    this.props.setUserActions(userData);
    this.props.setActivePage('Feature Distribution');
  }

  renderDashHeader() {
    const { features, isFeaturesLoading } = this.props;
    const { processedFeatures } = features;
    const resultsCount = isFeaturesLoading ? 0 : processedFeatures.length;

    return (
      <header className="dash-header">
        <ul className="dash-controls">
          <li>
            <Search />
          </li>
          <li className="sep" />
          <li className="results-counter">
            <span>{resultsCount}</span> factors
          </li>
          <li>&nbsp;</li>
        </ul>
      </header>
    );
  }

  drawDistribution(currentFeature) {
    const { distributions, isDistributionsLoading } = this.props;

    const distribution = distributions[currentFeature];

    const getMetricsDistribution = () => {
      const metricsDistribution = {
        ...distribution,
        distributionName: currentFeature,
        metricsSum: distribution.metrics[1].reduce((acc, val) => acc + val, 0),
        isLoading: isDistributionsLoading,
      };

      metricsDistribution.metricsRatios = distribution.metrics[1].map((metric, index) => ({
        ratio: parseFloat(((metric / metricsDistribution.metricsSum) * 100).toFixed(2)),
        name: distribution.metrics[0][index],
      }));

      return metricsDistribution;
    };

    if (distributions[currentFeature] === undefined) {
      return <p>No data to display</p>;
    }

    if (distributions[currentFeature] !== undefined && distributions[currentFeature].type === 'numeric') {
      const data = distributions[currentFeature].metrics;

      return <DayGraph data={data} graphIndex={currentFeature} />;
    }

    if (distributions[currentFeature].type === 'categorical') {
      const isCategoricalDistribution = distribution.metrics[0].length > 2;

      if (isCategoricalDistribution) {
        return <DistributionBar metrics={getMetricsDistribution()} />;
      }
      return <DistributionBar isBinary metrics={getMetricsDistribution()} />;
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
    return <p>No data to display</p>;
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
                  <th>Factor</th>
                  <th width="25%" className="align-right">
                    Distribution of Values
                  </th>
                </tr>
              </thead>
              <tbody>
                <Loader isLoading={isDataLoading} colSpan="2">
                  {processedFeatures && processedFeatures.length > 0 ? (
                    processedFeatures.map((currentFeature) => (
                      <tr key={currentFeature.name}>
                        <td>{currentFeature.description}</td>
                        <td className="align-right">{this.drawDistribution(currentFeature.name)}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="2" className="align-center">
                        <p>No matches found...</p>
                      </td>
                    </tr>
                  )}
                </Loader>
              </tbody>
            </table>
          </div>
        </DashWrapper>
      </div>
    );
  }
}

export default connect(
  (state) => ({
    isFeaturesLoading: getIsFeaturesLoading(state),
    isEntityLoading: getIsEntitiesLoading(state),
    isDistributionsLoading: getIsEntityDistributionsLoading(state),
    distributions: getEntityDistributions(state),
    features: getFeaturesData(state),
  }),
  (dispatch) => ({
    setUserActions: (userAction) => dispatch(setUserActionRecording(userAction)),
    setActivePage: (pageName) => dispatch(setActivePageAction(pageName)),
  }),
)(FeatureDistribution);
