import React from 'react';
import { connect } from 'react-redux';
import DashWrapper from '../common/DashWrapper';
import Search from '../common/Search';
import { ProgressIndicator } from '../common/ProgressBars';
import { getFeaturesImportances, getFeaturesData, getIsFeaturesLoading } from '../../model/selectors/features';

const BoxNote = () => (
  <div className="blue-box">
    <h4>How the Model works</h4>
    <p>
      The risk scores you see in this tool have been calculated by a type of machine learning model called linear
      regression. The algorithm uses the information you see below.
    </p>

    <p>
      Each piece of information is multiplied by a predetermined value (the weight), and then all the results are added
      together. The weights have been calculated based on a dataset of historic child welfare information.
    </p>

    <p>
      Some pieces of information have been found to not be relevant to risk - those are multiplied by 0. Others have
      been found to be very important, and will be multiplied by a higher value. When all the items are added together,
      the result is converted to a number 1-20, which represents the risk associated with the child.
    </p>

    <h4>Model Performance:</h4>
    <p>
      In the test data, over 40% of children who scored 20 were screened-out. Of these, 27% were rereferred and placed
      within 2 years. 46% of children who scored a 1 were screened-in. Of these, only 0.3% were placed within 2 years.
    </p>
  </div>
);

const getFeatureImportanceMax = (importances) => Math.max.apply(null, Object.values(importances));

const FeatureImportance = (props) => {
  const { featuresImportances, features, isFeaturesLoading } = props;
  const { processedFeatures } = features;
  const importanceMax = getFeatureImportanceMax(featuresImportances);

  return (
    <div className="component-wrapper">
      <BoxNote />
      <DashWrapper>
        <header className="dash-header">
          <ul className="dash-controls">
            <li>
              <Search />
            </li>
            <li>&nbsp;</li>
          </ul>
        </header>
        <div className="sticky-wrapper scroll-style">
          <table className="dash-table sticky-header">
            <thead>
              <tr>
                <th>Feature</th>
                <th width="20%" className="align-right">
                  Importance
                </th>
              </tr>
            </thead>
            <tbody>
              {!isFeaturesLoading &&
                processedFeatures.map((currentFeature) => (
                  <tr key={currentFeature.name}>
                    <td>{currentFeature.description}</td>
                    <td>
                      <ProgressIndicator
                        maxValue={importanceMax}
                        progressWidth={featuresImportances[currentFeature.name]}
                      />
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </DashWrapper>
    </div>
  );
};

export default connect((state) => ({
  isFeaturesLoading: getIsFeaturesLoading(state),
  features: getFeaturesData(state),
  featuresImportances: getFeaturesImportances(state),
}))(FeatureImportance);
