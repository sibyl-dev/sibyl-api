import React, { Component } from 'react';
import { connect } from 'react-redux';
import { DashWrapper } from '../common/DashWrapper';
import { CategorySelect, ValueSelect, DiffSelect } from '../common/Form';
import Search from '../common/Search';
import SandboxFilters from './SandboxFilters';
import { getModelPredictionAction, setFilterCategsAction } from '../../model/actions/features';
import { getIsEntitiesLoading } from '../../model/selectors/entities';
import {
  getIsFeaturesLoading,
  getModelPredictionData,
  getIsModelPredictLoading,
  getFeaturesData,
  getSelectedFilterValues,
  getIsCategoriesLoading,
  getFeatureCategories,
  getFilterCategories,
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
  componentDidMount() {
    const { isFeaturesLoading, getModelPrediction } = this.props;
    if (!isFeaturesLoading) {
      getModelPrediction();
    }
  }

  componentDidUpdate(prevProps) {
    const { isFeaturesLoading, getModelPrediction } = this.props;
    if (prevProps.isFeaturesLoading !== isFeaturesLoading && !isFeaturesLoading) {
      getModelPrediction();
    }
  }

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

    return currentFeature.currentOrder === 0 ? trueRow : falseRow;
  }

  getFeatureCathegoryColor = (feature) => {
    const { featureCategories } = this.props;
    const colorIndex = featureCategories.findIndex((currentCategory) => currentCategory.name === feature);

    if (colorIndex === -1) {
      return null;
    }

    return <i className="bullet" style={{ background: featureCategories[colorIndex].color }}></i>;
  };

  render() {
    const { modelPredictionData, isModelPredictionLoading, isFeaturesLoading, features } = this.props;
    const { processedFeatures } = features;
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
                {!isDataLoading ? (
                  processedFeatures.length > 0 ? (
                    processedFeatures.map((currentFeature) => {
                      if (modelPredictionData[currentFeature.name] !== undefined) {
                        const currentData = modelPredictionData[currentFeature.name];
                        return (
                          <tr key={currentFeature.name}>
                            <td className="align-center">{this.getFeatureCathegoryColor(currentFeature.category)}</td>
                            <td>
                              <span>{currentFeature.description}</span>
                            </td>
                            <td className="align-right">{this.renderOrderValues(currentData)}</td>
                            <td className="align-right">{currentData.reversedScore}</td>
                            <td className="align-right spaced" valign="middle">
                              <span>{currentData.currentDifference}</span>
                              <ArrowIcon {...arrowIconProps(currentData.currentDifference)} />
                            </td>
                          </tr>
                        );
                      }
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
    features: getFeaturesData(state),
    modelPredictionData: getModelPredictionData(state),
    featureCategories: getFeatureCategories(state),
    isCategoriesLoading: getIsCategoriesLoading(state),
    currentFilterValue: getSelectedFilterValues(state),
    currentFilterCategs: getFilterCategories(state),
  }),
  (dispatch) => ({
    getModelPrediction: () => dispatch(getModelPredictionAction()),
    setFilterCategories: (filterCategs) => dispatch(setFilterCategsAction(filterCategs)),
  }),
)(Sandbox);
