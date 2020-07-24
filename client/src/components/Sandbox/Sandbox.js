import React, { Component } from 'react';
import { connect } from 'react-redux';
import { DashWrapper } from '../common/DashWrapper';
import { CategorySelect, ValueSelect, DiffSelect } from '../common/Form';
import Search from '../common/Search';
import SandboxFilters from './SandboxFilters';
import { getModelPredictionAction } from '../../model/actions/features';
import { getIsEntitiesLoading } from '../../model/selectors/entities';
import {
  getIsFeaturesLoading,
  getModelPredictionData,
  getIsModelPredictLoading,
  getFeaturesData,
} from '../../model/selectors/features';

import { ArrowIcon, SortIcon } from '../../assets/icons/icons';
import './Sandbox.scss';

// mock search result
const hayStack = [
  { feature: 'Child in focus had a prior court active child welfare case' },
  { feature: 'Child in focus is younger than 1 years old' },
  { feature: 'Feature #1' },
  { feature: 'Feature #2' },
  { feature: 'Feature #3' },
];

class Sandbox extends Component {
  componentDidUpdate(prevProps) {
    const { isFeaturesLoading, getModelPrediction } = this.props;
    if (prevProps.isFeaturesLoading !== isFeaturesLoading && !isFeaturesLoading) {
      getModelPrediction();
    }
  }

  renderDashHeader() {
    return (
      <header className="dash-header">
        <ul className="dash-controls">
          <li>
            <Search hayStack={hayStack} />
          </li>
          <li className="sep" />
          <li>
            <CategorySelect />
          </li>
          <li>
            <ValueSelect />
          </li>
          <li>
            <DiffSelect />
          </li>
        </ul>
      </header>
    );
  }

  renderOrderValues(currentFeature) {
    const falseRow = (
      <span>
        True -&gt; <b>False</b>
      </span>
    );
    const trueRow = (
      <span>
        False -&gt; <b>True</b>
      </span>
    );

    return currentFeature.currentOrder === 0 ? trueRow : falseRow;
  }

  render() {
    const { modelPredictionData, isModelPredictionLoading, isFeaturesLoading, features } = this.props;
    const isDataLoading = isFeaturesLoading || isModelPredictionLoading;
    return (
      <div className="component-wrapper">
        <SandboxFilters />
        <div className="dash-title">
          <h4>Model predictions if each value was changed</h4>
        </div>
        <DashWrapper>
          {this.renderDashHeader()}
          <div className="sticky-wrapper scroll-style">
            <table className="dash-table sticky-header">
              <thead>
                <tr>
                  <th className="align-center">Category</th>
                  <th>Feature</th>
                  <th className="align-right" width="15%">
                    Changed Value
                  </th>
                  <th className="align-right" width="16%">
                    <ul className="sort">
                      <li>New Prediction</li>
                      <li>
                        <button type="button">
                          <SortIcon />
                        </button>
                      </li>
                    </ul>
                  </th>
                  <th className="align-right" width="16%">
                    <ul className="sort">
                      <li>Difference</li>
                      <li>
                        <button type="button">
                          <SortIcon />
                        </button>
                      </li>
                    </ul>
                  </th>
                </tr>
              </thead>
              <tbody>
                {(!isDataLoading &&
                  features.map((currentFeature) => {
                    if (modelPredictionData[currentFeature.name]) {
                      const currentData = modelPredictionData[currentFeature.name];
                      return (
                        <tr key={currentFeature.name}>
                          <td className="align-center">
                            <i className="bullet gray"></i>
                          </td>
                          <td>
                            <span>{currentFeature.description}</span>
                          </td>
                          <td className="align-right">{this.renderOrderValues(currentData)}</td>
                          <td className="align-right">{currentData.reversedScore}</td>
                          <td className="align-right spaced" valign="middle">
                            <span>{currentData.currentDifference}</span> <ArrowIcon className="blue" />
                          </td>
                        </tr>
                      );
                    }
                  })) || (
                  <tr>
                    <td colSpan="6">
                      <p>Loading....</p>
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

export default connect(
  (state) => ({
    isEntityLoading: getIsEntitiesLoading(state),
    isFeaturesLoading: getIsFeaturesLoading(state),
    isModelPredictionLoading: getIsModelPredictLoading(state),
    features: getFeaturesData(state),
    modelPredictionData: getModelPredictionData(state),
  }),
  (dispatch) => ({
    getModelPrediction: () => dispatch(getModelPredictionAction()),
  }),
)(Sandbox);
