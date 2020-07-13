import React, { Component } from 'react';
import { TableFullIcon, TableSplitIcon, SortIcon } from '../../assets/icons/icons';
import DashWrapper from '../common/DashWrapper';
import Select from 'react-select';
import Search from '../common/Search';
import { CategorySelect } from '../common/Form';
import { BiProgressBar } from '../common/ProgressBars';
import { connect } from 'react-redux';
import { getEntityAction } from '../../model/actions/entities';
import { getIsEntitiesLoading, getCurrentEntityData } from '../../model/selectors/entitites';

import './Details.scss';

// mock search result
const hayStack = [
  { feature: 'Child in focus had a prior court active child welfare case' },
  { feature: 'Child in focus is younger than 1 years old' },
  { feature: 'Feature #1' },
  { feature: 'Feature #2' },
  { feature: 'Feature #3' },
];

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
      isViewSplitted: false,
    };
    this.changeViewMode = this.changeViewMode.bind(this);
  }

  changeViewMode() {
    const { isViewSplitted } = this.state;

    this.setState({
      isViewSplitted: !isViewSplitted,
    });
  }

  renderSubheader() {
    const { isViewSplitted } = this.state;

    return (
      <div className="sub-header">
        <ul>
          <li>{isViewSplitted ? <Search hayStack={hayStack} /> : <h4>Risk Factors List</h4>}</li>
          <li>
            <button
              type="button"
              className={`view-full ${!isViewSplitted ? 'active' : ''}`}
              onClick={this.changeViewMode}
              disabled={!isViewSplitted}
            >
              <TableFullIcon />
            </button>
            <button
              type="button"
              className={`view-split ${isViewSplitted ? 'active' : ''}`}
              onClick={this.changeViewMode}
              disabled={isViewSplitted}
            >
              <TableSplitIcon />
            </button>
          </li>
        </ul>
      </div>
    );
  }

  renderDashHeader() {
    const { isViewSplitted } = this.state;
    return (
      <header className="dash-header">
        <ul className="dash-controls">
          {!isViewSplitted && (
            <React.Fragment>
              <li>
                <Search hayStack={hayStack} />
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
  getContributionsMaxValue(stack) {
    let maxRange = 0;
    const values = Object.values(stack);
    values.map((currentValue) => (maxRange = Math.max(maxRange, Math.abs(currentValue))));
    return maxRange;
  }

  renderUnifiedMode() {
    const { isEntityLoading, entityData } = this.props;
    const { featuresData, contributions, features } = entityData;

    const getFeatureType = (feature) => {
      const { name } = feature;
      return parseInt(features[name]) > 0 ? 'True' : 'False';
    };

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
                      <button type="button">
                        <SortIcon />
                      </button>
                    </li>
                  </ul>
                </th>
              </tr>
            </thead>
            <tbody>
              {!isEntityLoading &&
                featuresData.map((currentFeature, featureIndex) => (
                  <tr key={featureIndex}>
                    <td className="align-center">
                      <i className="bullet red"></i>
                    </td>
                    <td>{currentFeature.description}</td>
                    <td className="align-right">
                      {currentFeature.type === 'Boolean' ? getFeatureType(currentFeature) : ''}
                    </td>
                    <td className="align-center" width="145">
                      <BiProgressBar
                        percentage={contributions[currentFeature.name]}
                        width="110"
                        height="8"
                        maxRange={this.getContributionsMaxValue(contributions)}
                      />
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  renderSplitMode() {
    const { isEntityLoading, entityData } = this.props;
    const { featuresData, contributions, features } = entityData;

    const getFeatureType = (feature) => {
      const { name } = feature;
      return parseInt(features[name]) > 0 ? 'True' : 'False';
    };

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
                          <button type="button">
                            <SortIcon />
                          </button>
                        </li>
                      </ul>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {!isEntityLoading &&
                    featuresData.map(
                      (currentFeature, featureIndex) =>
                        contributions[currentFeature.name] > 0 && (
                          <tr key={featureIndex}>
                            <td className="align-center">
                              <i className="bullet red"></i>
                            </td>
                            <td>{currentFeature.description}</td>
                            <td className="align-right">
                              {currentFeature.type === 'Boolean' ? getFeatureType(currentFeature) : ''}
                            </td>
                            <td className="align-center" width="145">
                              <BiProgressBar
                                percentage={contributions[currentFeature.name]}
                                width="110"
                                height="8"
                                maxRange={this.getContributionsMaxValue(contributions)}
                                isSingle
                              />
                            </td>
                          </tr>
                        ),
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
                          <button type="button">
                            <SortIcon />
                          </button>
                        </li>
                      </ul>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {!isEntityLoading &&
                    featuresData.map(
                      (currentFeature, featureIndex) =>
                        contributions[currentFeature.name] < 0 && (
                          <tr key={featureIndex}>
                            <td className="align-center">
                              <i className="bullet red"></i>
                            </td>
                            <td>{currentFeature.description}</td>
                            <td className="align-right">
                              {currentFeature.type === 'Boolean' ? getFeatureType(currentFeature) : ''}
                            </td>
                            <td className="align-center" width="145">
                              <BiProgressBar
                                percentage={contributions[currentFeature.name]}
                                width="110"
                                height="8"
                                maxRange={this.getContributionsMaxValue(contributions)}
                                isSingle
                              />
                            </td>
                          </tr>
                        ),
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
    const { isViewSplitted } = this.state;

    return (
      <div>
        {this.renderSubheader()}
        <div className="component-wrapper no-shadow">
          <DashWrapper className={`${isViewSplitted ? 'no-shadow' : ''} `}>
            {isViewSplitted ? this.renderSplitMode() : this.renderUnifiedMode()}
          </DashWrapper>
        </div>
      </div>
    );
  }
}

export default connect((state) => ({
  isEntityLoading: getIsEntitiesLoading(state),
  entityData: getCurrentEntityData(state),
}))(Details);
