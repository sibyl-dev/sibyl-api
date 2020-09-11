import React, { Component } from 'react';
import { connect } from 'react-redux';
import Select from 'react-select';
import Button from '@material-ui/core/Button';
import { TableFullIcon, TableSplitIcon, SortIcon, ChevronDownIcon, ChevronUpIcon } from '../../assets/icons/icons';
import DashWrapper from '../common/DashWrapper';
import Search from '../common/Search';
import { CategorySelect } from '../common/Form';
import Loader from '../common/Loader';
import MetTooltip from '../common/MetTooltip';
import { BiProgressBar } from '../common/ProgressBars';
import {
  sortFeaturesByContribAction,
  // setFilterValuesAction,
  setFilterCategsAction,
  setContribFiltersAction,
  // setFeatureTypeFilterAction,
  setFeatureTypeSortContribDirAction,
  setFeatureTypeFilterCategsAction,
  setFilterCriteriaAction,
} from '../../model/actions/features';
import { getIsEntitiesLoading, getCurrentEntityData, getIsEntityContribLoading } from '../../model/selectors/entities';

import {
  getIsFeaturesLoading,
  getFeaturesData,
  getIsCategoriesLoading,
  getFeatureCategories,
  getSortingContribDir,
  // getSelectedFilterValues,
  getFilterCategories,
  getCurrentContribFilters,
  // getFeatureTypeFilters,
  getFeatureTypeSortContribDir,
  getGrouppedFeatures,
  getFeatureTypeFilterCategs,
  getMaxContributionRange,
} from '../../model/selectors/features';
import { setUserActionRecording } from '../../model/actions/userActions';

import { setActivePageAction } from '../../model/actions/sidebar';
import './Details.scss';

// const filterValues = [
//   { value: 'all', label: 'All Values', isFixed: true },
//   { value: 'binary', label: 'True/False', isFixed: true },
//   { value: 'numeric', label: 'Numerical', isFixed: true },
// ];

const contribFilters = [
  { value: 'all', label: 'All Contributions', isFixed: true },
  { value: 'risk', label: 'Risk', isFixed: true },
  { value: 'protective', label: 'Protective', isFixed: true },
];

const initialContributionView = {
  isCombinedExpanded: false,
  isPositiveViewExpanded: false,
  isNegativeViewExpanded: false,
};

export class Details extends Component {
  constructor(props) {
    super(props);
    this.state = {
      viewMode: 'unified',
      featureContribView: initialContributionView,
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

  getExpanded(featureContribView, viewMode, featureType = null) {
    if (viewMode === 'unified') {
      return featureContribView.isCombinedExpanded;
    }

    if (featureType === 'positiveFeatures') return featureContribView.isPositiveViewExpanded;

    return featureContribView.isNegativeViewExpanded;
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
    const { viewMode, featureContribView } = this.state;
    const { isNegativeViewExpanded, isPositiveViewExpanded } = featureContribView;

    return (
      <div className="sub-header">
        <ul>
          <li className="search-field-holder">
            {viewMode === 'split' ? (
              <Search disabled={!isNegativeViewExpanded || !isPositiveViewExpanded} />
            ) : (
              <h4>Factor Contributions</h4>
            )}
          </li>
          {viewMode === 'split' ? (
            <li className={`expand-tip ${isNegativeViewExpanded && isPositiveViewExpanded ? 'hide' : ''}`}>
              <span>Click &ldquo;Show All Factors&ldquo; to enable Search and Filter in both tables</span>
            </li>
          ) : null}
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

  renderDashHeader(featureType) {
    const { viewMode, featureContribView } = this.state;
    const { isCombinedExpanded } = featureContribView;
    const {
      // setFilterValues,
      // currentFilterValue,
      isCategoriesLoading,
      featureCategories,
      setFilterCategories,
      currentFilterCategs,
      setContribFilters,
      currentContribFilters,
      // setFeatureFilters,
      // featureTypeFilters,
      setFeatureTypeFilterCategs,
      currentFeatureTypeCategs,
    } = this.props;

    // const setFeatureFilterValues = (filterValue) =>
    //   featureType !== 'all' ? setFeatureFilters(featureType, filterValue) : setFilterValues(filterValue);

    // const getFilterValue = () =>
    //   featureType !== 'all'
    //     ? filterValues.filter((currentValue) => currentValue.value === featureTypeFilters[featureType])
    //     : filterValues.filter((currentValue) => currentValue.value === currentFilterValue);

    const setFeatureCategsFilter = (categs) =>
      featureType !== 'all' ? setFeatureTypeFilterCategs(featureType, categs) : setFilterCategories(categs);

    const getCurrentCategs = () =>
      featureType !== 'all' ? currentFeatureTypeCategs[featureType] : currentFilterCategs;

    return (
      !isCategoriesLoading && (
        <header className="dash-header">
          <ul className="dash-controls">
            {viewMode === 'unified' && (
              <>
                <li>
                  <Search disabled={!isCombinedExpanded} />
                </li>
                <li className="sep" />
              </>
            )}
            <li className={`category-select-${featureType}`}>
              <CategorySelect
                options={featureCategories}
                onChange={(selectedCategories) => setFeatureCategsFilter(selectedCategories)}
                value={getCurrentCategs()}
                disabled={!this.getExpanded(featureContribView, viewMode, featureType)}
              />
            </li>
            {/* <li>
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
            </li> */}
            {viewMode === 'unified' && (
              <>
                <li>
                  <Select
                    isSearchable={false}
                    isMulti={false}
                    classNamePrefix="sibyl-select"
                    className="sibyl-select"
                    options={contribFilters}
                    isDisabled={!this.getExpanded(featureContribView, viewMode)}
                    placeholder="Contribution"
                    onChange={(currentFilters) => setContribFilters(currentFilters.value)}
                    value={contribFilters.filter((currentContrib) => currentContrib.value === currentContribFilters)}
                  />
                </li>
                <li className={`expand-tip ${isCombinedExpanded ? 'hide' : ''}`}>
                  <span>Click &ldquo;Show All Factors&ldquo; to enable Search and Filter</span>
                </li>
              </>
            )}
          </ul>
        </header>
      )
    );
  }

  toggleDash(featureContribView, viewMode, featureType) {
    const { setContribFilters, setFilterCriteria, setFeatureTypeFilterCategs, setFilterCategories } = this.props;
    const { isCombinedExpanded, isPositiveViewExpanded, isNegativeViewExpanded } = featureContribView;

    // reset filters
    if (featureContribView) {
      setContribFilters('all');
      setFilterCriteria('');

      if (featureType !== 'all') {
        setFeatureTypeFilterCategs(featureType, null);
      } else {
        setFilterCategories(null);
      }
    }

    // create new state for featureContribView
    const updatedFeatureContribView = {
      ...featureContribView,
      isCombinedExpanded: viewMode === 'unified' ? !isCombinedExpanded : isCombinedExpanded,
    };

    if (viewMode !== 'unified') {
      if (featureType === 'positiveFeatures') {
        updatedFeatureContribView.isPositiveViewExpanded = !isPositiveViewExpanded;
      } else {
        updatedFeatureContribView.isNegativeViewExpanded = !isNegativeViewExpanded;
      }
    }

    this.setState(
      {
        viewMode,
        featureContribView: updatedFeatureContribView,
      },
      () => this.recordUserAction,
    );
  }

  renderFooter(featureType, isDataLoading) {
    const { isCategoriesLoading, grouppedFeatures, features } = this.props;
    const { positiveFeaturesContrib, negativeFeaturesContrib } = grouppedFeatures;
    const { processedFeatures } = features;

    const { featureContribView, viewMode } = this.state;
    const featureContribViewValue = this.getExpanded(featureContribView, viewMode, featureType);

    const getResultsCount = () => {
      if (isDataLoading) {
        return 0;
      }

      const limitNumber = viewMode === 'unified' ? 10 : 5;
      const positiveLength =
        positiveFeaturesContrib.length > limitNumber && !featureContribViewValue
          ? limitNumber
          : positiveFeaturesContrib.length;
      const negativeLength =
        negativeFeaturesContrib.length > limitNumber && !featureContribViewValue
          ? limitNumber
          : negativeFeaturesContrib.length;
      const processedLength =
        processedFeatures.length > limitNumber && !featureContribViewValue ? limitNumber : processedFeatures.length;

      return featureType !== 'all'
        ? featureType === 'positiveFeatures'
          ? positiveLength
          : negativeLength
        : processedLength;
    };

    const toggleButton = () => (
      <Button
        className="expand-button"
        onClick={() => this.toggleDash(featureContribView, viewMode, featureType)}
        startIcon={featureContribViewValue ? <ChevronUpIcon /> : <ChevronDownIcon />}
      >
        {' '}
        {featureContribViewValue ? 'HIDE EXTRA FACTORS' : 'SHOW ALL FACTORS'}
      </Button>
    );

    return (
      !isCategoriesLoading && (
        <div className="dash-footer">
          <p>
            Showing <span>{getResultsCount()}</span> factors
          </p>
          {toggleButton()}
        </div>
      )
    );
  }

  getFeatureType(feature) {
    const { entityData } = this.props;
    const { name, type } = feature;
    return type === 'binary' ? (entityData.features[name] > 0 ? 'True' : 'False') : entityData.features[name];
  }

  getFeatureCategoryColor(feature) {
    const { featureCategories } = this.props;
    const colorIndex = featureCategories.findIndex((currentCategory) => currentCategory.name === feature);

    if (colorIndex === -1) {
      return null;
    }

    return (
      <>
        <MetTooltip title={featureCategories[colorIndex].name} placement="top">
          <i className="bullet" style={{ background: featureCategories[colorIndex].color }} />
        </MetTooltip>
        <span className="feature-category-label">{featureCategories[colorIndex].abbreviation}</span>
      </>
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
        {this.renderFooter('all', isDataLoading)}
      </div>
    );
  }

  getFeatureDescription(feature) {
    return feature.type === 'binary' && this.getFeatureType(feature) === 'False'
      ? feature.negated_description
      : feature.description;
  }

  renderFeatures(features, isDataLoading, featuresType = 'all') {
    const { maxContributionRange } = this.props;
    const { viewMode, featureContribView } = this.state;
    const featureContribViewValue = this.getExpanded(featureContribView, viewMode, featuresType);

    let featuresToShow = null;
    if (!featureContribViewValue && features) {
      featuresToShow =
        featuresType === 'all'
          ? features.slice(0, 5).concat(features.slice(Math.max(features.length - 5, 1)))
          : features.slice(0, 10);
    } else {
      featuresToShow = features;
    }

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
              {featuresToShow && featuresToShow.length > 0 ? (
                featuresToShow.map((currentFeature) => (
                  <tr key={currentFeature.name}>
                    <td className="align-center">{this.getFeatureCategoryColor(currentFeature.category)}</td>
                    <td>{this.getFeatureDescription(currentFeature)}</td>
                    <td className="align-right">
                      {currentFeature.type !== 'binary' ? this.getFeatureType(currentFeature) : '-'}
                    </td>
                    <td className="align-center" width="145">
                      <BiProgressBar
                        percentage={currentFeature.contributionValue}
                        width="110"
                        height="10"
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
            {this.renderFooter('positiveFeatures', isDataLoading)}
          </div>
        </div>
        <div className="split-separator" />
        <div className="split-side">
          <h4>Protective Factors</h4>
          <div className="split-container">
            {this.renderDashHeader('negativeFeatures', isDataLoading)}
            {this.renderFeatures(negativeFeaturesContrib, isDataLoading, 'negativeFeatures')}
            {this.renderFooter('negativeFeatures', isDataLoading)}
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
    // currentFilterValue: getSelectedFilterValues(state),
    currentFilterCategs: getFilterCategories(state),
    currentContribFilters: getCurrentContribFilters(state),
    // featureTypeFilters: getFeatureTypeFilters(state),
    currentFeatureTypeSortDir: getFeatureTypeSortContribDir(state),
    grouppedFeatures: getGrouppedFeatures(state),
    currentFeatureTypeCategs: getFeatureTypeFilterCategs(state),
    maxContributionRange: getMaxContributionRange(state),
  }),
  (dispatch) => ({
    setSortContribDir: (direction) => dispatch(sortFeaturesByContribAction(direction)),
    // setFilterValues: (filterValue) => dispatch(setFilterValuesAction(filterValue)),
    setFilterCategories: (filterCategs) => dispatch(setFilterCategsAction(filterCategs)),
    setFilterCriteria: (filterValue) => dispatch(setFilterCriteriaAction(filterValue)),

    setContribFilters: (currentContribFilters) => dispatch(setContribFiltersAction(currentContribFilters)),
    // setFeatureFilters: (featureType, filter) => dispatch(setFeatureTypeFilterAction(featureType, filter)),
    setFeatureSortDir: (featureType, direction) => dispatch(setFeatureTypeSortContribDirAction(featureType, direction)),
    setFeatureTypeFilterCategs: (featureType, categs) =>
      dispatch(setFeatureTypeFilterCategsAction(featureType, categs)),
    setUserActions: (userAction) => dispatch(setUserActionRecording(userAction)),
    setPageName: (pageName) => dispatch(setActivePageAction(pageName)),
  }),
)(Details);
