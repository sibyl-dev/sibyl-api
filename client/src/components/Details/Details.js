import React from 'react';
import { TableFullIcon, TableSplitIcon, SortIcon } from '../../assets/icons/icons';
import DashWrapper from '../common/DashWrapper';
import Select from 'react-select';
import Search from '../common/Search';
import { CategorySelect, ValueSelect } from '../common/Form';
import LiniarIndicator from '../common/LiniarIndicator';

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

const Details = () => (
  <div>
    <div className="sub-header">
      <ul>
        <li>Risk Factors List</li>
        <li>
          <button type="button" className="view-full active">
            <TableFullIcon />
          </button>
          <button type="button" className="view-split">
            <TableSplitIcon />
          </button>
        </li>
      </ul>
    </div>
    <div className="component-wrapper no-shadow">
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
        <div className="sticky-wrapper scroll-style" style={{ maxHeight: '600px' }}>
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
              <tr>
                <td className="align-center">
                  <i className="bullet red"></i>
                </td>
                <td>Child in focus had a prior court active child welfare case</td>
                <td className="align-right">True</td>
                <td className="align-center">
                  <LiniarIndicator percentageLeft="0" percentaceRight="50" />
                </td>
              </tr>
              <tr>
                <td className="align-center">
                  <i className="bullet orange"></i>
                </td>
                <td>Days the child in focus was in child welfare placement in the last 90 days</td>
                <td className="align-right">True</td>
                <td className="align-center">
                  <LiniarIndicator percentageLeft="0" percentaceRight="40" />
                </td>
              </tr>
              <tr>
                <td className="align-center">
                  <i className="bullet orange"></i>
                </td>
                <td>Days the child in focus was in child welfare placement in the last 90 days</td>
                <td className="align-right">True</td>
                <td className="align-center">
                  <LiniarIndicator percentageLeft="0" percentaceRight="30" />
                </td>
              </tr>
              <tr>
                <td className="align-center">
                  <i className="bullet orange"></i>
                </td>
                <td>Days the child in focus was in child welfare placement in the last 90 days</td>
                <td className="align-right">True</td>
                <td className="align-center">
                  <LiniarIndicator percentageLeft="0" percentaceRight="20" />
                </td>
              </tr>
              <tr>
                <td className="align-center">
                  <i className="bullet orange"></i>
                </td>
                <td>Days the child in focus was in child welfare placement in the last 90 days</td>
                <td className="align-right">True</td>
                <td className="align-center">
                  <LiniarIndicator percentageLeft="0" percentaceRight="15" />
                </td>
              </tr>
              <tr>
                <td className="align-center">
                  <i className="bullet orange"></i>
                </td>
                <td>Days the child in focus was in child welfare placement in the last 90 days</td>
                <td className="align-right">True</td>
                <td className="align-center">
                  <LiniarIndicator percentageLeft="0" percentaceRight="10" />
                </td>
              </tr>

              <tr>
                <td className="align-center">
                  <i className="bullet orange"></i>
                </td>
                <td>Feature #1</td>
                <td className="align-right">True</td>
                <td className="align-center">
                  <LiniarIndicator percentageLeft="10" percentaceRight="0" />
                </td>
              </tr>
              <tr>
                <td className="align-center">
                  <i className="bullet orange"></i>
                </td>
                <td>Feature #1</td>
                <td className="align-right">True</td>
                <td className="align-center">
                  <LiniarIndicator percentageLeft="15" percentaceRight="0" />
                </td>
              </tr>
              <tr>
                <td className="align-center">
                  <i className="bullet orange"></i>
                </td>
                <td>Feature #1</td>
                <td className="align-right">True</td>
                <td className="align-center">
                  <LiniarIndicator percentageLeft="20" percentaceRight="0" />
                </td>
              </tr>
              <tr>
                <td className="align-center">
                  <i className="bullet orange"></i>
                </td>
                <td>Feature #1</td>
                <td className="align-right">True</td>
                <td className="align-center">
                  <LiniarIndicator percentageLeft="30" percentaceRight="0" />
                </td>
              </tr>
              <tr>
                <td className="align-center">
                  <i className="bullet orange"></i>
                </td>
                <td>Feature #1</td>
                <td className="align-right">True</td>
                <td className="align-center">
                  <LiniarIndicator percentageLeft="40" percentaceRight="0" />
                </td>
              </tr>
              <tr>
                <td className="align-center">
                  <i className="bullet orange"></i>
                </td>
                <td>Feature #1</td>
                <td className="align-right">True</td>
                <td className="align-center">
                  <LiniarIndicator percentageLeft="50" percentaceRight="0" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </DashWrapper>
    </div>
  </div>
);

export default Details;
