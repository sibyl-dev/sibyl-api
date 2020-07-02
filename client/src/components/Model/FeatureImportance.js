import React from 'react';
import DashWrapper from '../common/DashWrapper';
import Search from '../common/Search';
import { ProgressIndicator } from '../common/LiniarIndicator';

// mock search result
const hayStack = [
  { feature: 'Child in focus had a prior court active child welfare case' },
  { feature: 'Child in focus is younger than 1 years old' },
  { feature: 'Feature #1' },
  { feature: 'Feature #2' },
  { feature: 'Feature #3' },
];

const FeatureImportance = () => (
  <div className="component-wrapper">
    <div className="blue-box">
      <h4>How the Model works</h4>
      <p>
        The risk scores you see in this tool have been calculated by a type of machine learning model called linear
        regression. The algorithm uses the information you see below.{' '}
      </p>

      <p>
        Each piece of information is multiplied by a predetermined value (the weight), and then all the results are
        added together. The weights have been calculated based on a dataset of historic child welfare information.{' '}
      </p>

      <p>
        Some pieces of information have been found to not be relevant to risk - those are multiplied by 0. Others have
        been found to be very important, and will be multiplied by a higher value. When all the items are added
        together, the result is converted to a number 1-20, which represents the risk associated with the child.
      </p>

      <h4>Model Performance:</h4>
      <p>
        In the test data, over 40% of children who scored 20 were screened-out. Of these, 27% were rereferred and placed
        within 2 years. 46% of children who scored a 1 were screened-in. Of these, only 0.3% were placed within 2 years.{' '}
      </p>
    </div>
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

export default FeatureImportance;
