import React, { Component } from 'react';
import Select from 'react-select';
import { TrashIcon, QuestionIcon } from '../../assets/icons/icons';
import ModalDialog from '../common/ModalDialog';
import { connect } from 'react-redux';
import { updateFeaturePredictionScore } from '../../model/actions/features';
import { getIsFeaturesLoding, getFeaturesData, getUpdatedFeatureScore } from '../../model/selectors/features';
import { getEntityScore } from '../../model/selectors/entities';

const featureValues = [
  { value: '0', label: 'True -> False' },
  { value: '1', label: 'False -> True' },
];

const dropdownFeatures = (currentFeatures) => {
  const enhancedFeatures = [];
  currentFeatures.map((feature) => {
    const { description, name, type } = feature;
    enhancedFeatures.push({ value: name, label: description, type });
  });
  return enhancedFeatures;
};

class SandboxFilters extends Component {
  constructor(props) {
    super(props);
    this.state = {
      featuresCount: [0],
      maxFeaturesCount: 4,
      storedFeatures: {},
      storedValues: {},
      isModalOpen: false,
    };
    this.onAddFeature = this.onAddFeature.bind(this);
  }

  toggleModalState(modalState) {
    this.setState({
      isModalOpen: modalState,
    });
  }

  onResetFeature(featureIndex) {
    this.setState({
      storedFeatures: {
        ...this.state.storedFeatures,
        [featureIndex]: { value: null },
      },
      storedValues: {
        ...this.state.storedValues,
        [featureIndex]: { value: null },
      },
    });
  }

  onFeatureOptionUpdate(featureIndex, featureValue) {
    this.setState(
      {
        storedFeatures: {
          ...this.state.storedFeatures,
          [featureIndex]: featureValue,
        },
      },
      () => {
        this.onFeatureScoreUpdate();
        this.renderFeatureValues(featureIndex);
      },
    );
  }

  onFeatureValueUpdate(valueIndex, value) {
    this.setState(
      {
        storedValues: {
          ...this.state.storedValues,
          [valueIndex]: value,
        },
      },
      () => this.onFeatureScoreUpdate(),
    );
  }

  onAddFeature() {
    const { featuresCount, maxFeaturesCount } = this.state;
    if (featuresCount.length === maxFeaturesCount) {
      return null;
    }
    this.setState({ featuresCount: [...featuresCount, featuresCount[featuresCount.length - 1] + 1] });
  }

  onRemoveFeature(feature) {
    const { featuresCount, storedFeatures, storedValues } = this.state;
    if (featuresCount.length === 1) {
      return;
    }

    featuresCount.splice(featuresCount.indexOf(feature), 1);
    delete storedFeatures[feature];
    delete storedValues[feature];
    this.setState({ featuresCount });
  }

  onFeatureScoreUpdate() {
    const { storedFeatures, storedValues } = this.state;
    const { updateScore } = this.props;

    if (Object.keys(storedFeatures).length !== Object.keys(storedValues).length) {
      return;
    }

    let storedData = [];
    Object.keys(storedFeatures).map((feature) => {
      const isPayloadCompleted =
        storedFeatures[feature] !== null &&
        storedFeatures[feature].value !== null &&
        storedValues[feature] !== null &&
        storedValues[feature].value !== null &&
        storedValues[feature].value !== '';

      if (!isPayloadCompleted) {
        return;
      }
      storedData.push([storedFeatures[feature].value, storedValues[feature].value]);
    });

    storedData.length !== 0 && updateScore(storedData);
  }

  renderModal() {
    const { isModalOpen } = this.state;
    return (
      <ModalDialog isOpen={isModalOpen} title="Notice" onClose={() => this.toggleModalState(false)}>
        <p>
          The predictions on this screen show how the model’s predictions would change under different circumstances.
          Here, you can look into what the model values, and make changes based on information you may have.
        </p>
        <p className="highlight">It DOES NOT predict how reality would change under these conditions.</p>
        <p className="note">
          Press on the &quot;
          <QuestionIcon width="10" height="10" color="#6B9AD1" />
          &quot; icon near "Experiment with changes" title to re-visit this message.
        </p>
        <p>
          <input type="checkbox" id="remind" />
          <label htmlFor="remind">
            <span />
            Don't remind me again
          </label>
        </p>
      </ModalDialog>
    );
  }

  renderFeatureValues(currentFeature) {
    const { storedFeatures, storedValues } = this.state;
    const featureType = storedFeatures[currentFeature] ? storedFeatures[currentFeature].type : null;
    const selectedValue = Object.keys(storedValues).length ? storedValues[currentFeature] : null;

    if (featureType === 'numeric') {
      return (
        <input
          type="number"
          onKeyUp={(event) => this.onFeatureValueUpdate(currentFeature, { value: event.target.value })}
        />
      );
    }

    return (
      <Select
        isSearchable={false}
        isMulti={false}
        classNamePrefix="sibyl-select"
        className="sibyl-select"
        options={featureValues}
        placeholder="Change Value"
        onChange={(value) => this.onFeatureValueUpdate(currentFeature, value)}
        value={selectedValue}
      />
    );
  }

  renderFeatureComponent() {
    const { features, isFeaturesLoading } = this.props;
    const { featuresCount, storedFeatures, storedValues } = this.state;

    if (isFeaturesLoading) {
      return; // loader should be returned here;
    }

    return featuresCount.map((currentFeature, featureIndex) => {
      const selectedFeature = Object.keys(storedFeatures).length ? storedFeatures[currentFeature] : null;

      return (
        <tr key={`${currentFeature}_${featureIndex}`}>
          <td width="3%" className="counter">
            {featureIndex + 1}
          </td>
          <td width="50%">
            <Select
              isSearchable={true}
              isMulti={false}
              classNamePrefix="sibyl-select"
              className="sibyl-select"
              options={dropdownFeatures(features)}
              placeholder="Select / Search a Feature"
              onChange={(value) => this.onFeatureOptionUpdate(currentFeature, value)}
              value={selectedFeature}
            />
          </td>
          <td>
            <div className="separator" />
          </td>
          <td width="30%">{this.renderFeatureValues(currentFeature)}</td>
          <td align="center" width="9%">
            <ul className="feature-controls">
              <li>
                <button
                  type="button"
                  className="clean reset-feature"
                  onClick={() => this.onResetFeature(currentFeature)}
                >
                  Reset
                </button>
              </li>
              <li>
                {featureIndex !== 0 && (
                  <button type="button" className="clean trash" onClick={() => this.onRemoveFeature(currentFeature)}>
                    <TrashIcon />
                  </button>
                )}
              </li>
            </ul>
          </td>
        </tr>
      );
    });
  }

  render() {
    const { featuresCount, maxFeaturesCount } = this.state;
    const { entityScore, updatedScore } = this.props;

    return (
      <div className="sandbox-filters">
        <header>
          <h4>
            Experiment with changes
            <button type="button" className="clean" onClick={() => this.toggleModalState(true)}>
              <QuestionIcon />
            </button>
          </h4>
          <div className="filter-tab">
            Updated Prediction: <strong>{updatedScore !== null ? updatedScore : entityScore}</strong>
          </div>
        </header>
        <div className="filter-wrapper">
          <table>
            <thead>
              <tr>
                <td colSpan="3">Features</td>
                <td colSpan="2">Values</td>
              </tr>
            </thead>
            <tbody>{this.renderFeatureComponent()}</tbody>
            <tfoot>
              <tr>
                <td colSpan="5">
                  <button
                    type="button"
                    className="clean add-feature"
                    onClick={this.onAddFeature}
                    disabled={featuresCount.length === maxFeaturesCount}
                  >
                    + Add Feature
                  </button>
                  <span className="max-count">
                    {maxFeaturesCount - featuresCount.length}/{maxFeaturesCount - 1} Remaining
                  </span>
                </td>
              </tr>
            </tfoot>
          </table>
          {this.renderModal()}
        </div>
      </div>
    );
  }
}

export default connect(
  (state) => ({
    isFeaturesLoading: getIsFeaturesLoding(state),
    features: getFeaturesData(state),
    entityScore: getEntityScore(state),
    updatedScore: getUpdatedFeatureScore(state),
  }),
  (dispatch) => ({
    updateScore: (featuresData) => dispatch(updateFeaturePredictionScore(featuresData)),
  }),
)(SandboxFilters);
