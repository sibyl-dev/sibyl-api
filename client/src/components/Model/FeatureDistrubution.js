import React from 'react';
import DashWrapper from '../common/DashWrapper';

import Search from '../common/Search';
import { ProgressIndicator } from '../common/LiniarIndicator';
import ScoreInfo from '../common/ScoreInfo';

// mock search result
const hayStack = [
  { feature: 'Child in focus had a prior court active child welfare case' },
  { feature: 'Child in focus is younger than 1 years old' },
  { feature: 'Feature #1' },
  { feature: 'Feature #2' },
  { feature: 'Feature #3' },
];

const FeatureDistribution = () => (
  <div className="component-wrapper">
    <table>
      <tr>
        <td>
          <ScoreInfo />
        </td>
      </tr>
    </table>
    <DashWrapper>
      <header className="dash-header">
        <ul className="dash-controls">
          <li>
            <Search hayStack={hayStack} />
          </li>
          <li>&nbsp;</li>
        </ul>
      </header>
      <table className="dash-table">
        <thead>
          <tr>
            <th>Feature</th>
            <th width="20%" className="align-right">
              Importance
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Child in focus had a prior court active child welfare case</td>
            <td className="align-right">
              <ProgressIndicator progressWidth="90%" />
            </td>
          </tr>
          <tr>
            <td>Days the child in focus was in child welfare placement in the last 90 days</td>
            <td className="align-right">
              <ProgressIndicator progressWidth="85%" />
            </td>
          </tr>
          <tr>
            <td>Feature #1</td>
            <td className="align-right">
              <ProgressIndicator progressWidth="70%" />
            </td>
          </tr>
          <tr>
            <td>Feature #2</td>
            <td className="align-right">
              <ProgressIndicator progressWidth="65%" />
            </td>
          </tr>
          <tr>
            <td>Feature #3</td>
            <td className="align-right">
              <ProgressIndicator progressWidth="50%" />
            </td>
          </tr>
          <tr>
            <td>Feature #4</td>
            <td className="align-right">
              <ProgressIndicator progressWidth="45%" />
            </td>
          </tr>
        </tbody>
      </table>
    </DashWrapper>
  </div>
);

export default FeatureDistribution;
