import React, { Component } from 'react';
import { connect } from 'react-redux';
import Select from 'react-select';
import { TableFullIcon, TableSplitIcon, SortIcon } from '../../assets/icons/icons';
import DashWrapper from '../common/DashWrapper';
import Search from '../common/Search';
import { CategorySelect } from '../common/Form';
import Loader from '../common/Loader';
import MetTooltip from '../common/MetTooltip';
import { BiProgressBar } from '../common/ProgressBars';
import {
  sortFeaturesByContribAction,
  setFilterValuesAction,
  setFilterCategsAction,
  setContribFiltersAction,
  setFeatureTypeFilterAction,
  setFeatureTypeSortContribDirAction,
  setFeatureTypeFilterCategsAction,
} from '../../model/actions/features';
import { getIsEntitiesLoading, getCurrentEntityData, getIsEntityContribLoading } from '../../model/selectors/entities';

import {
  getIsFeaturesLoading,
  getFeaturesData,
  getIsCategoriesLoading,
  getFeatureCategories,
  getSortingContribDir,
  getSelectedFilterValues,
  getFilterCategories,
  getCurrentContribFilters,
  getFeatureTypeFilters,
  getFeatureTypeSortContribDir,
  getGrouppedFeatures,
  getFeatureTypeFilterCategs,
} from '../../model/selectors/features';
import { setUserActionRecording } from '../../model/actions/userActions';

import { setActivePageAction } from '../../model/actions/sidebar';
import './Details.scss';

const filterValues = [
  { value: 'all', label: 'All Values', isFixed: true },
  { value: 'binary', label: 'True/False', isFixed: true },
  { value: 'numeric', label: 'Numerical', isFixed: true },
];

const contribFilters = [
  { value: 'all', label: 'All Contributions', isFixed: true },
  { value: 'risk', label: 'Risk', isFixed: true },
  { value: 'protective', label: 'Protective', isFixed: true },
];

export class Details extends Component {
  constructor(props) {
    super(props);
    this.state = {
      viewMode: 'unified',
    };
  }

  componentDidMount() {
    const userData = {
      element: 'details_page',
      action: 'click',
    };
    this.props.setUserActions(userData);
    this.props.setPageName('Details');
  }

  componentWillUnmount() {
    this.props.setContribFilters('all');
  }

  changeViewMode(viewMode) {
    this.setState(
      {
        viewMode,
      },
      () => this.recordUserAction(),
    );
  }

  renderSubheader() {
    const { viewMode } = this.state;

    return (
      <div className="sub-header">
        <ul>
          <li>{viewMode === 'split' ? <Search /> : <h4>Factor Contributions</h4>}</li>
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

  renderDashHeader(featureType, isDataLoading) {
    const { viewMode } = this.state;
    const {
      setFilterValues,
      currentFilterValue,
      isCategoriesLoading,
      featureCategories,
      setFilterCategories,
      currentFilterCategs,
      setContribFilters,
      currentContribFilters,
      setFeatureFilters,
      featureTypeFilters,
      setFeatureTypeFilterCategs,
      currentFeatureTypeCategs,
      grouppedFeatures,
      features,
    } = this.props;
    const { positiveFeaturesContrib, negativeFeaturesContrib } = grouppedFeatures;
    const { processedFeatures } = features;

    const setFeatureFilterValues = (filterValue) =>
      featureType !== 'all' ? setFeatureFilters(featureType, filterValue) : setFilterValues(filterValue);

    const getFilterValue = () =>
      featureType !== 'all'
        ? filterValues.filter((currentValue) => currentValue.value === featureTypeFilters[featureType])
        : filterValues.filter((currentValue) => currentValue.value === currentFilterValue);

    const setFeatureCategsFilter = (categs) =>
      featureType !== 'all' ? setFeatureTypeFilterCategs(featureType, categs) : setFilterCategories(categs);

    const getCurrentCategs = () =>
      featureType !== 'all' ? currentFeatureTypeCategs[featureType] : currentFilterCategs;

    const getResultsCount = () => {
      if (isDataLoading) {
        return 0;
      }
      return featureType !== 'all'
        ? featureType === 'positiveFeatures'
          ? positiveFeaturesContrib.length
          : negativeFeaturesContrib.length
        : processedFeatures.length;
    };

    return (
      !isCategoriesLoading && (
        <header className="dash-header">
          <ul className="dash-controls">
            {viewMode === 'unified' && (
              <>
                <li>
                  <Search />
                </li>
                <li className="sep" />
              </>
            )}
            <li>
              <CategorySelect
                options={featureCategories}
                onChange={(selectedCategories) => setFeatureCategsFilter(selectedCategories)}
                value={getCurrentCategs()}
              />
            </li>
            <li>
              <Select
                isSearchable={false}
                isMulti={false}
                classNamePrefix="sibyl-select"
                className="sibyl-select"
                options={filterValues}
                placeholder="All Values"
                value={getFilterValue()}
                onChange={(filterValue) => setFeatureFilterValues(filterValue.value)}
              />
            </li>
            {viewMode === 'unified' && (
              <li>
                <Select
                  isSearchable={false}
                  isMulti={false}
                  classNamePrefix="sibyl-select"
                  className="sibyl-select"
                  options={contribFilters}
                  placeholder="Contribution"
                  onChange={(currentFilters) => setContribFilters(currentFilters.value)}
                  value={contribFilters.filter((currentContrib) => currentContrib.value === currentContribFilters)}
                />
              </li>
            )}
            <li className="sep" />
            <li className="results-counter">
              <span>{getResultsCount()}</span> factors
            </li>
          </ul>
        </header>
      )
    );
  }

  // getting the contribution max value to set the min/max range (-range, range)
  getContributionsMaxValue() {
    let maxRange = 0;
    const { processedFeatures } = this.props.features;

    processedFeatures.map((currentFeature) => {
      const { contributionValue } = currentFeature;
      maxRange = maxRange > Math.abs(contributionValue) ? maxRange : Math.abs(contributionValue);
      return null;
    });
    return maxRange;
  }

  getFeatureType(feature) {
    const { entityData } = this.props;
    const { name, type } = feature;
    return type === 'binary' ? (entityData.features[name] > 0 ? 'True' : 'False') : entityData.features[name];
  }

  getFeatureCathegoryColor(feature) {
    const { featureCategories } = this.props;
    const colorIndex = featureCategories.findIndex((currentCategory) => currentCategory.name === feature);

    if (colorIndex === -1) {
      return null;
    }

    return (
      <MetTooltip title={featureCategories[colorIndex].name} placement="top">
        <i className="bullet" style={{ background: featureCategories[colorIndex].color }} />
      </MetTooltip>
    );
  }

  setSortContribDirection() {
    const { setSortContribDir, currentSortDir } = this.props;
    const currentDirection = currentSortDir === 'asc' ? 'desc' : 'asc';
    setSortContribDir(currentDirection);
  }

  setFeatureSortContribDir(featureType) {
    const { setFeatureSortDir, currentFeatureTypeSortDir } = this.props;
    const direction = currentFeatureTypeSortDir[featureType] === 'asc' ? 'desc' : 'asc';
    setFeatureSortDir(featureType, direction);
  }

  renderUnifiedMode() {
    const { isEntityLoading, isFeaturesLoading, isCategoriesLoading, isEntityContribLoading, features } = this.props;
    const { processedFeatures } = features;

    const isDataLoading = isEntityLoading || isFeaturesLoading || isCategoriesLoading || isEntityContribLoading;
    return (
      <div>
        {this.renderDashHeader('all', isDataLoading)}
        {this.renderFeatures(processedFeatures, isDataLoading)}
      </div>
    );
  }

  renderFeatures(features, isDataLoading, featuresType = 'all') {
    const maxContributionRange = !isDataLoading ? this.getContributionsMaxValue() : 0;
    const { viewMode } = this.state;

    return (
      <div className="sticky-wrapper scroll-style">
        <table className="dash-table sticky-header">
          <thead>
            <tr>
              <th className="align-center" width="10%">
                Category
              </th>
              <th>Factor</th>
              <th className="align-right">Value</th>
              <th className="align-center" width="15%">
                <ul className="sort">
                  <li>Contribution</li>
                  <li>
                    <button
                      type="button"
                      onClick={() =>
                        viewMode === 'unified'
                          ? this.setSortContribDirection()
                          : this.setFeatureSortContribDir(featuresType)
                      }
                    >
                      <SortIcon />
                    </button>
                  </li>
                </ul>
              </th>
            </tr>
          </thead>
          <tbody>
            <Loader isLoading={isDataLoading}>
              {features && features.length > 0 ? (
                features.map((currentFeature) => (
                  <tr key={currentFeature.name}>
                    <td className="align-center">{this.getFeatureCathegoryColor(currentFeature.category)}</td>
                    <td>{currentFeature.description}</td>
                    <td className="align-right">{this.getFeatureType(currentFeature)}</td>
                    <td className="align-center" width="145">
                      <BiProgressBar
                        percentage={currentFeature.contributionValue}
                        width="110"
                        height="8"
                        maxRange={maxContributionRange}
                        isSingle={viewMode === 'split'}
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
              )}
            </Loader>
          </tbody>
        </table>
      </div>
    );
  }

  renderSplitMode() {
    const { isFeaturesLoading, isEntityContribLoading, grouppedFeatures } = this.props;
    const { positiveFeaturesContrib, negativeFeaturesContrib } = grouppedFeatures;
    const isDataLoading = isEntityContribLoading || isFeaturesLoading;

    return (
      <div className="split-wrapper">
        <div className="split-side">
          <h4>Risk Factors</h4>
          <div className="split-container">
            {this.renderDashHeader('positiveFeatures', isDataLoading)}
            {this.renderFeatures(positiveFeaturesContrib, isDataLoading, 'positiveFeatures')}
          </div>
        </div>
        <div className="split-separator" />
        <div className="split-side">
          <h4>Protective Factors</h4>
          <div className="split-container">
            {this.renderDashHeader('negativeFeatures', isDataLoading)}
            {this.renderFeatures(negativeFeaturesContrib, isDataLoading, 'negativeFeatures')}
          </div>
        </div>
      </div>
    );
  }

  recordUserAction() {
    const { viewMode } = this.state;
    const userData = {
      element: viewMode === 'split' ? 'split_view' : 'unified_view',
      action: 'click',
    };
    this.props.setUserActions(userData);
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
    currentFilterValue: getSelectedFilterValues(state),
    currentFilterCategs: getFilterCategories(state),
    currentContribFilters: getCurrentContribFilters(state),
    featureTypeFilters: getFeatureTypeFilters(state),
    currentFeatureTypeSortDir: getFeatureTypeSortContribDir(state),
    grouppedFeatures: getGrouppedFeatures(state),
    currentFeatureTypeCategs: getFeatureTypeFilterCategs(state),
  }),
  (dispatch) => ({
    setSortContribDir: (direction) => dispatch(sortFeaturesByContribAction(direction)),
    setFilterValues: (filterValue) => dispatch(setFilterValuesAction(filterValue)),
    setFilterCategories: (filterCategs) => dispatch(setFilterCategsAction(filterCategs)),
    setContribFilters: (currentContribFilters) => dispatch(setContribFiltersAction(currentContribFilters)),
    setFeatureFilters: (featureType, filter) => dispatch(setFeatureTypeFilterAction(featureType, filter)),
    setFeatureSortDir: (featureType, direction) => dispatch(setFeatureTypeSortContribDirAction(featureType, direction)),
    setFeatureTypeFilterCategs: (featureType, categs) =>
      dispatch(setFeatureTypeFilterCategsAction(featureType, categs)),
    setUserActions: (userAction) => dispatch(setUserActionRecording(userAction)),
    setPageName: (pageName) => dispatch(setActivePageAction(pageName)),
  }),
)(Details);
