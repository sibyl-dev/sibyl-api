import React, { Component } from 'react';
import { connect } from 'react-redux';
import { DashWrapper } from '../common/DashWrapper';
import { CategorySelect, ValueSelect, DiffSelect } from '../common/Form';
import Search from '../common/Search';

import { ArrowIcon, SortIcon } from '../../assets/icons/icons';
import SandboxFilters from './SandboxFilters';
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
  render() {
    return (
      <div className="component-wrapper">
        <SandboxFilters />
        <div className="dash-title">
          <h4>Model predictions if each value was changed</h4>
        </div>
        <DashWrapper>
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
          <table className="dash-table">
            <thead>
              <tr>
                <th className="align-center">Category</th>
                <th>Feature</th>
                <th className="align-right">Changed Value</th>
                <th className="align-right">
                  <ul className="sort">
                    <li>New Prediction</li>
                    <li>
                      <button type="button">
                        <SortIcon />
                      </button>
                    </li>
                  </ul>
                </th>
                <th className="align-right">
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
              <tr>
                <td className="align-center">
                  <i className="bullet red"></i>
                </td>
                <td>
                  <span>Child in focus had a prior court active child welfare case</span>
                </td>
                <td className="align-right">
                  True -&gt; <b>False</b>
                </td>
                <td className="align-right">19</td>
                <td className="align-right spaced" valign="middle">
                  <span>4</span> <ArrowIcon dir="up" className="red" />
                </td>
              </tr>

              <tr>
                <td className="align-center">
                  <i className="bullet orange"></i>
                </td>
                <td>
                  <span>Child in focus is younger than 1 years old</span>
                </td>
                <td className="align-right">
                  True -&gt; <b>False</b>
                </td>
                <td className="align-right">19</td>
                <td className="align-right spaced" valign="middle">
                  <span>4</span> <ArrowIcon className="blue" />
                </td>
              </tr>

              <tr>
                <td className="align-center">
                  <i className="bullet green"></i>
                </td>
                <td>
                  <span>Feature #1</span>
                </td>
                <td className="align-right">
                  True -&gt; <b>False</b>
                </td>
                <td className="align-right">19</td>
                <td className="align-right spaced" valign="middle">
                  <span>4</span> <ArrowIcon className="blue" />
                </td>
              </tr>
            </tbody>
          </table>
        </DashWrapper>
      </div>
    );
  }
}

export default connect(
  (state) => ({}),
  (dispatch) => ({}),
)(Sandbox);
