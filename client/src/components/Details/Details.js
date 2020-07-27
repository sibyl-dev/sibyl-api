import React, { Component } from 'react';
import { connect } from 'react-redux';
import { TableFullIcon, TableSplitIcon, SortIcon } from '../../assets/icons/icons';
import DashWrapper from '../common/DashWrapper';
import Select from 'react-select';
import Search from '../common/Search';
import { CategorySelect } from '../common/Form';
import MetTooltip from '../common/MetTooltip';
import { BiProgressBar } from '../common/ProgressBars';
import { sortFeaturesByContribAction } from '../../model/actions/features';
import { getIsEntitiesLoading, getCurrentEntityData, getIsEntityContribLoading } from '../../model/selectors/entities';

import {
  getIsFeaturesLoading,
  getFeaturesData,
  getIsCategoriesLoading,
  getFeatureCategories,
  getSortingContribDir,
} from '../../model/selectors/features';

import './Details.scss';

const mockValues = [
  { value: 'All', label: 'All', isFixed: true },
  { value: 'Value 1', label: 'Value 1', isFixed: true },
  { value: 'Value 2', label: 'Value 2', isFixed: true },
  { value: 'Value 3', label: 'Value 3', isFixed: true },
  { value: 'Value 4', label: 'Value 4', isFixed: true },
  { value: 'Value 5', label: 'Value 5', isFixed: true },
];

export class Details extends Component {
  constructor(props) {
    super(props);
    this.state = {
      viewMode: 'unified',
    };
  }

  changeViewMode(viewMode) {
    this.setState({
      viewMode,
    });
  }

  renderSubheader() {
    const { viewMode } = this.state;

    return (
      <div className="sub-header">
        <ul>
          <li>{viewMode === 'split' ? <Search /> : <h4>Risk Factors List</h4>}</li>
          <li>
            <MetTooltip title="Single Table View" placement="top">
              <button
                type="button"
                className={`view-full ${viewMode === 'unified' ? 'active' : ''}`}
                onClick={() => this.changeViewMode('unified')}
              >
                <TableFullIcon />
              </button>
            </MetTooltip>
            <MetTooltip title="Split View Comparison" placement="top">
              <button
                type="button"
                className={`view-split ${viewMode === 'split' ? 'active' : ''}`}
                onClick={() => this.changeViewMode('split')}
              >
                <TableSplitIcon />
              </button>
            </MetTooltip>
          </li>
        </ul>
      </div>
    );
  }

  renderDashHeader() {
    const { viewMode } = this.state;
    return (
      <header className="dash-header">
        <ul className="dash-controls">
          {viewMode === 'unified' && (
            <React.Fragment>
              <li>
                <Search />
              </li>
              <li className="sep" />
            </React.Fragment>
          )}

          <li>
            <CategorySelect />
          </li>
          <li>
            <Select
              isSearchable={false}
              isMulti={false}
              classNamePrefix="sibyl-select"
              className="sibyl-select"
              options={mockValues}
              placeholder="All Values"
            />
          </li>
          <li>
            <Select
              isSearchable={false}
              isMulti={false}
              classNamePrefix="sibyl-select"
              className="sibyl-select"
              options={mockValues}
              placeholder="Contribution"
            />
          </li>
        </ul>
      </header>
    );
  }

  // getting the contribution max value to set the min/max range (-range, range)
  getContributionsMaxValue(features) {
    let maxRange = 0;
    features.map((currentFeature) => {
      const { contributionValue } = currentFeature;
      maxRange = maxRange > contributionValue ? maxRange : contributionValue;
    });
    return maxRange;
  }

  getFeatureType = (feature) => {
    const { entityData } = this.props;
    const { name, type } = feature;
    return type === 'numeric' ? (entityData.features[name] > 0 ? 'True' : 'False') : entityData.features[name];
  };

  getFeatureColor = (feature) => {
    const { featureCategories } = this.props;
    const colorIndex = featureCategories.findIndex((currentCategory) => currentCategory.name === feature);

    if (colorIndex === -1) {
      return null;
    }

    if (featureCategories[colorIndex].color !== null) {
      return <i className="bullet" style={{ background: `#${featureCategories[colorIndex].color}` }}></i>;
    }

    return <i className="bullet gray"></i>;
  };

  setSortContribDirection() {
    const { setSortContribDir, currentSortDir } = this.props;
    const currentDirection = currentSortDir === 'asc' ? 'desc' : 'asc';
    setSortContribDir(currentDirection);
  }

  renderUnifiedMode() {
    const { isEntityLoading, isFeaturesLoading, isCategoriesLoading, isEntityContribLoading, features } = this.props;
    const { processedFeatures } = features;

    const isDataLoading = isEntityLoading || isFeaturesLoading || isCategoriesLoading || isEntityContribLoading;
    const maxContributionRange = !isDataLoading ? this.getContributionsMaxValue(processedFeatures) : 0;

    return (
      <div>
        {this.renderDashHeader()}
        <div className="sticky-wrapper scroll-style">
          <table className="dash-table sticky-header">
            <thead>
              <tr>
                <th className="align-center">Category</th>
                <th>Feature</th>
                <th className="align-right">Value</th>
                <th className="align-center" width="15%">
                  <ul className="sort">
                    <li>Contribution</li>
                    <li>
                      <button type="button" onClick={() => this.setSortContribDirection()}>
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
                  processedFeatures.map((currentFeature, featureIndex) => (
                    <tr key={featureIndex}>
                      <td className="align-center" width="12">
                        {this.getFeatureColor(currentFeature.category)}
                      </td>
                      <td>{currentFeature.description}</td>
                      <td className="align-right">{this.getFeatureType(currentFeature)}</td>
                      <td className="align-center" width="145">
                        <BiProgressBar
                          percentage={currentFeature.contributionValue}
                          width="110"
                          height="8"
                          maxRange={maxContributionRange}
                        />
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="4" className="align-center">
                      No Matches found...
                    </td>
                  </tr>
                )
              ) : (
                <tr>
                  <td colSpan="4" className="align-center">
                    <p>Loading ...</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  renderSplitMode() {
    const { features, isFeaturesLoading, isEntityContribLoading } = this.props;
    const { processedFeatures, positiveFeaturesContrib, negativeFeaturesContrib } = features;
    const isDataLoading = isEntityContribLoading || isFeaturesLoading;
    const maxContributionRange = !isDataLoading ? this.getContributionsMaxValue(processedFeatures) : 0;

    return (
      <div className="split-wrapper">
        <div className="split-side">
          <h4>Risk Factors</h4>
          <div className="split-container">
            {this.renderDashHeader()}
            <div className="sticky-wrapper scroll-style">
              <table className="dash-table sticky-header">
                <thead>
                  <tr>
                    <th className="align-center" width="10%">
                      Category
                    </th>
                    <th>Feature</th>
                    <th className="align-right">Value</th>
                    <th className="align-center" width="15%">
                      <ul className="sort">
                        <li>Contribution</li>
                        <li>
                          <button type="button" onClick={() => this.setSortContribDirection()}>
                            <SortIcon />
                          </button>
                        </li>
                      </ul>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {!isDataLoading ? (
                    positiveFeaturesContrib.length > 0 ? (
                      positiveFeaturesContrib.map((currentFeature, featureIndex) => (
                        <tr key={featureIndex}>
                          <td className="align-center">{this.getFeatureColor(currentFeature.category)}</td>
                          <td>{currentFeature.description}</td>
                          <td className="align-right">{this.getFeatureType(currentFeature)}</td>
                          <td className="align-center" width="145">
                            <BiProgressBar
                              percentage={currentFeature.contributionValue}
                              width="110"
                              height="8"
                              maxRange={maxContributionRange}
                              isSingle
                            />
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="4" className="align-center">
                          No Matches found...
                        </td>
                      </tr>
                    )
                  ) : (
                    <tr>
                      <td colSpan="4" className="align-center">
                        Loading...
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div className="split-separator" />
        <div className="split-side">
          <h4>Protective Factors</h4>
          <div className="split-container">
            {this.renderDashHeader()}
            <div className="sticky-wrapper scroll-style">
              <table className="dash-table sticky-header">
                <thead>
                  <tr>
                    <th className="align-center" width="10%">
                      Category
                    </th>
                    <th>Feature</th>
                    <th className="align-right">Value</th>
                    <th className="align-center" width="25%">
                      <ul className="sort">
                        <li>Contribution</li>
                        <li>
                          <button type="button" onClick={() => this.setSortContribDirection()}>
                            <SortIcon />
                          </button>
                        </li>
                      </ul>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {!isDataLoading ? (
                    negativeFeaturesContrib.length > 0 ? (
                      negativeFeaturesContrib.map(
                        (currentFeature, featureIndex) =>
                          currentFeature.contributionValue < 0 && (
                            <tr key={featureIndex}>
                              <td className="align-center">{this.getFeatureColor(currentFeature.category)}</td>
                              <td>{currentFeature.description}</td>
                              <td className="align-right">{this.getFeatureType(currentFeature)}</td>
                              <td className="align-center" width="145">
                                <BiProgressBar
                                  percentage={currentFeature.contributionValue}
                                  width="110"
                                  height="8"
                                  maxRange={maxContributionRange}
                                  isSingle
                                />
                              </td>
                            </tr>
                          ),
                      )
                    ) : (
                      <tr>
                        <td colSpan="4" className="align-center">
                          No Matches found...
                        </td>
                      </tr>
                    )
                  ) : (
                    <tr>
                      <td colSpan="4" className="align-center">
                        Loading...
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  }

  render() {
    const { viewMode } = this.state;

    return (
      <div>
        {this.renderSubheader()}
        <div className="component-wrapper no-shadow">
          <DashWrapper className={`${viewMode === 'split' ? 'no-shadow' : ''} `}>
            {viewMode === 'split' ? this.renderSplitMode() : this.renderUnifiedMode()}
          </DashWrapper>
        </div>
      </div>
    );
  }
}

export default connect(
  (state) => ({
    isEntityLoading: getIsEntitiesLoading(state),
    isFeaturesLoading: getIsFeaturesLoading(state),
    isCategoriesLoading: getIsCategoriesLoading(state),
    isEntityContribLoading: getIsEntityContribLoading(state),
    entityData: getCurrentEntityData(state),
    features: getFeaturesData(state),
    featureCategories: getFeatureCategories(state),
    currentSortDir: getSortingContribDir(state),
  }),
  (dispatch) => ({
    setSortContribDir: (direction) => dispatch(sortFeaturesByContribAction(direction)),
  }),
)(Details);
