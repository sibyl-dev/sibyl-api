import React, { Component } from 'react';
import Select from 'react-select';
import { connect } from 'react-redux';
import { TrashIcon, QuestionIcon } from '../../assets/icons/icons';
import ModalDialog from '../common/ModalDialog';
import { updateFeaturePredictionScore } from '../../model/actions/features';
import { getIsFeaturesLoading, getUpdatedFeatureScore, getCurrentFeatures } from '../../model/selectors/features';
import { getEntityScore, getCurrentEntityData, getIsEntitiesLoading } from '../../model/selectors/entities';

const featureValues = [
  { value: '0', label: 'True -> False' },
  { value: '1', label: 'False -> True' },
];

const dropdownFeatures = (currentFeatures) => {
  const enhancedFeatures = [];
  currentFeatures.map((feature) => {
    const { description, name, type } = feature;
    enhancedFeatures.push({ value: name, label: description, type });
    return null;
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
    const { storedFeatures, storedValues } = this.state;
    this.setState(
      {
        storedFeatures: {
          ...storedFeatures,
          [featureIndex]: { value: null },
        },
        storedValues: {
          ...storedValues,
          [featureIndex]: { value: null },
        },
      },
      () => this.onFeatureScoreUpdate(),
    );
  }

  onFeatureOptionUpdate(featureIndex, featureValue) {
    const { storedFeatures } = this.state;
    const { storedValues } = this.state;
    const { entities } = this.props;

    const getCurrentFeatureValue = () => {
      const featureType = this.state.storedFeatures[featureIndex].type;

      if (featureType === 'binary') {
        return entities.features[this.state.storedFeatures[featureIndex].value] === 1
          ? { value: 1, label: 'True' }
          : { value: 0, label: 'False' };
      }

      return { value: entities.features[this.state.storedFeatures[featureIndex].value] };
    };
    this.setState(
      {
        storedFeatures: {
          ...storedFeatures,
          [featureIndex]: featureValue,
        },
      },
      () => {
        this.onFeatureScoreUpdate();
        this.renderFeatureValues(featureIndex);
        this.setState({
          storedValues: {
            ...storedValues,
            [featureIndex]: getCurrentFeatureValue(),
          },
        });
      },
    );
  }

  onFeatureValueUpdate(valueIndex, value) {
    const { storedValues } = this.state;
    this.setState(
      {
        storedValues: {
          ...storedValues,
          [valueIndex]: value,
        },
      },
      () => {
        this.onFeatureScoreUpdate();
      },
    );
  }

  onAddFeature() {
    const { featuresCount, maxFeaturesCount } = this.state;
    if (featuresCount.length === maxFeaturesCount) {
      return null;
    }
    this.setState({ featuresCount: [...featuresCount, featuresCount[featuresCount.length - 1] + 1] });
    return null;
  }

  onRemoveFeature(feature) {
    const { featuresCount, storedFeatures, storedValues } = this.state;
    if (featuresCount.length === 1) {
      return;
    }

    featuresCount.splice(featuresCount.indexOf(feature), 1);
    delete storedFeatures[feature];
    delete storedValues[feature];
    this.setState({ featuresCount }, () => this.onFeatureScoreUpdate());
  }

  onFeatureScoreUpdate() {
    const { storedFeatures, storedValues } = this.state;
    const { updateScore } = this.props;

    if (Object.keys(storedFeatures).length !== Object.keys(storedValues).length) {
      return;
    }

    let storedData = [];
    Object.keys(storedFeatures).forEach((feature) => {
      const isPayloadCompleted =
        storedFeatures[feature] !== null &&
        storedFeatures[feature].value !== null &&
        storedValues[feature] !== null &&
        storedValues[feature] !== undefined &&
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
          &quot; icon near &quot;Experiment with changes&quot; title to re-visit this message.
        </p>
        <p>
          <input type="checkbox" id="remind" />
          <label htmlFor="remind">
            <span />
            Don&apos;t remind me again
          </label>
        </p>
      </ModalDialog>
    );
  }

  renderFeatureValues(currentFeature) {
    const { storedFeatures, storedValues } = this.state;
    const featureType = storedFeatures[currentFeature] ? storedFeatures[currentFeature].type : null;
    const selectedValue = Object.keys(storedValues).length !== 0 ? storedValues[currentFeature] : null;

    if (featureType === 'numeric') {
      const inputValue =
        Object.keys(storedValues).length !== 0 && storedValues[currentFeature]
          ? storedValues[currentFeature].value
          : '';
      return (
        <input
          type="number"
          onChange={(event) => this.onFeatureValueUpdate(currentFeature, { value: event.target.value })}
          value={inputValue}
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
    const { features, isFeaturesLoading, isEntitiesLoading } = this.props;
    const { featuresCount, storedFeatures } = this.state;

    if (isFeaturesLoading || isEntitiesLoading) {
      return false; // loader should be returned here;
    }

    return featuresCount.map((currentFeature, featureIndex) => {
      const selectedFeature = Object.keys(storedFeatures).length ? storedFeatures[currentFeature] : null;
      return (
        <tr key={`${currentFeature}`}>
          <td width="3%" className="counter">
            {featureIndex + 1}
          </td>
          <td width="50%">
            <Select
              isSearchable
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
    isFeaturesLoading: getIsFeaturesLoading(state),
    isEntitiesLoading: getIsEntitiesLoading(state),
    entities: getCurrentEntityData(state),
    features: getCurrentFeatures(state),
    entityScore: getEntityScore(state),
    updatedScore: getUpdatedFeatureScore(state),
  }),
  (dispatch) => ({
    updateScore: (featuresData) => dispatch(updateFeaturePredictionScore(featuresData)),
  }),
)(SandboxFilters);
