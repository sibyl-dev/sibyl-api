import React, { Component } from 'react';
import { connect } from 'react-redux';
import DashWrapper from '../common/DashWrapper';
import Search from '../common/Search';
import { ProgressIndicator } from '../common/ProgressBars';
import {
  getFeaturesImportances,
  getFeaturesData,
  getIsFeaturesLoading,
  getSortedByImportanceFeatures,
  getFeatureImpSortDir,
} from '../../model/selectors/features';

import { setUserActionRecording } from '../../model/actions/userActions';
import Loader from '../common/Loader';
import { setActivePageAction } from '../../model/actions/sidebar';
import { setFeatureImpSortDirAction } from '../../model/actions/features';
import { SortIcon } from '../../assets/icons/icons';

const BoxNote = () => (
  <div className="blue-box">
    <h4>How the Model works</h4>
    <p>
      The risk scores you see in this tool have been calculated by a type of machine learning model called linear
      regression. The algorithm uses the factors you see below.
    </p>

    <p>
      Each factor is multiplied by a predetermined value (the weight), and then all the results are added together. The
      weights have been calculated based on a dataset of historic child welfare information.
    </p>

    <p>
      Some factors have been found to not be relevant to risk - those are multiplied by 0. Others have been found to be
      very important, and will be multiplied by a higher value. When all the items are added together, the result is
      converted to a number 1-20, which represents the risk associated with the child.
    </p>

    <h4>Model Performance:</h4>
    <p>
      In the test data, over 40% of children who scored 20 were screened-out. Of these, 27% were rereferred and placed
      within 2 years. 46% of children who scored a 1 were screened-in. Of these, only 0.3% were placed within 2 years.
    </p>
  </div>
);

const getFeatureImportanceMax = (importances) => Math.max.apply(null, Object.values(importances));

class FeatureImportance extends Component {
  componentDidMount() {
    const userData = {
      element: 'feature_importance',
      action: 'click',
    };
    this.props.setUserActions(userData);
    this.props.setActivePage('Global Feature Importance');
  }

  setSortFeaturesDirection() {
    const { setSortDir, currentSortDir } = this.props;
    setSortDir(currentSortDir === 'asc' ? 'desc' : 'asc');
  }

  render() {
    const { sortedImpFeatures, features, isFeaturesLoading, featuresImportances } = this.props;

    const { processedFeatures } = features;
    const importanceMax = getFeatureImportanceMax(featuresImportances);
    const resultsCount = isFeaturesLoading ? 0 : processedFeatures.length;

    return (
      <div className="component-wrapper">
        <BoxNote />
        <DashWrapper>
          <header className="dash-header">
            <ul className="dash-controls">
              <li>
                <Search />
              </li>
              <li className="sep" />
              <li className="results-counter">
                <span>{resultsCount} factors</span>
              </li>
              <li>&nbsp;</li>
            </ul>
          </header>
          <div className="sticky-wrapper scroll-style">
            <table className="dash-table sticky-header">
              <thead>
                <tr>
                  <th>Feature</th>
                  <th width="20%" className="align-right">
                    <ul className="sort">
                      <li>Importance</li>
                      <li>
                        <button type="button" onClick={() => this.setSortFeaturesDirection()}>
                          <SortIcon />
                        </button>
                      </li>
                    </ul>
                  </th>
                </tr>
              </thead>
              <tbody>
                <Loader isLoading={isFeaturesLoading} colSpan="2">
                  {sortedImpFeatures &&
                    sortedImpFeatures.map((currentFeature) => (
                      <tr key={currentFeature.name}>
                        <td>{currentFeature.description}</td>
                        <td>
                          <ProgressIndicator
                            maxValue={importanceMax}
                            progressWidth={currentFeature.featureImportance}
                          />
                        </td>
                      </tr>
                    ))}
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
    features: getFeaturesData(state),
    featuresImportances: getFeaturesImportances(state),
    sortedImpFeatures: getSortedByImportanceFeatures(state),
    currentSortDir: getFeatureImpSortDir(state),
  }),
  (dispatch) => ({
    setUserActions: (userAction) => dispatch(setUserActionRecording(userAction)),
    setActivePage: (pageName) => dispatch(setActivePageAction(pageName)),
    setSortDir: (direction) => dispatch(setFeatureImpSortDirAction(direction)),
  }),
)(FeatureImportance);
