import React, { Component } from 'react';
import { connect } from 'react-redux';
import { DashWrapper } from '../common/DashWrapper';
import { CategorySelect, ValueSelect, DiffSelect } from '../common/Form';
import Search from '../common/Search';
import SandboxFilters from './SandboxFilters';
import {
  getModelPredictionAction,
  setFilterCategsAction,
  setSortPredDirection,
  setSortDiffDirectionAction,
  setContribFiltersAction,
} from '../../model/actions/features';
import { getIsEntitiesLoading } from '../../model/selectors/entities';
import {
  getIsFeaturesLoading,
  getIsModelPredictLoading,
  getSelectedFilterValues,
  getIsCategoriesLoading,
  getFeatureCategories,
  getFilterCategories,
  getCurrentPredSortDir,
  getReversedModelPredFeatures,
  getCurrentSortDiffDir,
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
  renderDashHeader() {
    const { featureCategories, setFilterCategories, isCategoriesLoading, currentFilterCategs } = this.props;

    return (
      !isCategoriesLoading && (
        <header className="dash-header">
          <ul className="dash-controls">
            <li>
              <Search hayStack={hayStack} />
            </li>
            <li className="sep" />
            <li>
              <CategorySelect
                options={featureCategories}
                onChange={(selectedCategories) => setFilterCategories(selectedCategories)}
                value={currentFilterCategs}
              />
            </li>
            <li>
              <ValueSelect />
            </li>
            <li>
              <DiffSelect />
            </li>
          </ul>
        </header>
      )
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
    return currentFeature === 0 ? trueRow : falseRow;
  }

  getFeatureCathegoryColor = (feature) => {
    const { featureCategories } = this.props;
    const colorIndex = featureCategories.findIndex((currentCategory) => currentCategory.name === feature);

    if (colorIndex === -1) {
      return null;
    }

    return <i className="bullet" style={{ background: featureCategories[colorIndex].color }}></i>;
  };

  setSortContribDirection() {
    const { currentPredSortDir, setSortPrediction } = this.props;
    const currentDirection = currentPredSortDir === 'asc' ? 'des' : 'asc';
    setSortPrediction(currentDirection);
  }

  setSortDiffDirection() {
    const { currentDiffDirection, setSortDiffDirection } = this.props;
    const currentDirection = currentDiffDirection === 'asc' ? 'desc' : 'asc';
    setSortDiffDirection(currentDirection);
  }

  render() {
    const { isModelPredictionLoading, isFeaturesLoading, modelPredFeatures } = this.props;
    const isDataLoading = isFeaturesLoading || isModelPredictionLoading;

    const arrowIconProps = (data) => {
      const arrowClassName = data === 0 ? 'gray' : data > 0 ? 'red' : 'blue';
      const arrowDir = data === 0 ? 'equal' : data > 0 ? 'up' : 'down';
      return {
        className: arrowClassName,
        dir: arrowDir,
      };
    };

    return (
      <div className="component-wrapper">
        <SandboxFilters />
        <div className="dash-title">
          <h4>Model predictions if each value was changed</h4>
        </div>
        <DashWrapper>
          {this.renderDashHeader()}
          <div className="sticky-wrapper scroll-style">
            <table className="dash-table sticky-header sandbox">
              <thead>
                <tr>
                  <th className="align-center">Category</th>
                  <th>Feature</th>
                  <th className="align-right" width="15%">
                    Changed Value
                  </th>
                  <th className="align-right" width="185">
                    <ul className="sort">
                      <li>New Prediction</li>
                      <li>
                        <button type="button" onClick={() => this.setSortContribDirection()} disabled={isDataLoading}>
                          <SortIcon />
                        </button>
                      </li>
                    </ul>
                  </th>
                  <th className="align-right" width="16%">
                    <ul className="sort">
                      <li>Difference</li>
                      <li>
                        <button type="button" onClick={() => this.setSortDiffDirection()} disabled={isDataLoading}>
                          <SortIcon />
                        </button>
                      </li>
                    </ul>
                  </th>
                </tr>
              </thead>
              <tbody>
                {!isModelPredictionLoading ? (
                  modelPredFeatures.length > 0 ? (
                    modelPredFeatures.map((currentFeature) => {
                      const { name, description, category, modelPrediction } = currentFeature;
                      const { reversedScore, currentDifference } = modelPrediction;

                      return (
                        <tr key={name}>
                          <td className="align-center">{this.getFeatureCathegoryColor(category)}</td>
                          <td>
                            <span>{description}</span>
                          </td>
                          <td className="align-right">{this.renderOrderValues(currentFeature[name])}</td>
                          <td className="align-right">{reversedScore}</td>
                          <td className="align-right spaced" valign="middle">
                            <span>{currentDifference}</span>
                            <ArrowIcon {...arrowIconProps(currentDifference)} />
                          </td>
                        </tr>
                      );
                    })
                  ) : (
                    <tr>
                      <td colSpan="6" className="align-center">
                        <p>No Matches found....</p>
                      </td>
                    </tr>
                  )
                ) : (
                  <tr>
                    <td colSpan="6" className="align-center">
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
    featureCategories: getFeatureCategories(state),
    isCategoriesLoading: getIsCategoriesLoading(state),
    currentFilterValue: getSelectedFilterValues(state),
    currentFilterCategs: getFilterCategories(state),
    currentPredSortDir: getCurrentPredSortDir(state),
    modelPredFeatures: getReversedModelPredFeatures(state),
    currentDiffDirection: getCurrentSortDiffDir(state),
  }),
  (dispatch) => ({
    getModelPrediction: () => dispatch(getModelPredictionAction()),
    setFilterCategories: (filterCategs) => dispatch(setFilterCategsAction(filterCategs)),
    setSortPrediction: (direction) => dispatch(setSortPredDirection(direction)),
    setSortDiffDirection: (direction) => dispatch(setSortDiffDirectionAction(direction)),
    setContribFilters: (filters) => dispatch(setContribFiltersAction(filters)),
  }),
)(Sandbox);
