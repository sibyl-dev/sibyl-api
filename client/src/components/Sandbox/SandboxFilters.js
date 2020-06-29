import React, { Component } from 'react';
import Select from 'react-select';
import { TrashIcon, QuestionIcon } from '../../assets/icons/icons';
// import { ModalDialog } from 'react-bootstrap';
import ModalDialog from '../common/ModalDialog';

const featureOptions = [
  { value: 'All', label: 'All', icon: 'all', isFixed: true },
  { value: 'Category 1', label: 'Category 1', icon: 'red', isFixed: true },
  { value: 'Category 2', label: 'Category 2', icon: 'blue', isFixed: true },
  { value: 'Category 3', label: 'Category 3', icon: 'green', isFixed: true },
  { value: 'Category 4', label: 'Category 4', icon: 'red', isFixed: true },
  { value: 'Category 5', label: 'Category 5', icon: 'orange', isFixed: true },
];

const featureValues = [
  { value: 'All', label: 'All', isFixed: true },
  { value: 'True -> False', label: 'True -> False', isFixed: true },
  { value: 'False -> True', label: 'False -> True', isFixed: true },
  { value: 'Categorycal', label: 'Categorycal', isFixed: true },
  { value: 'Numerical', label: 'Numerical', isFixed: true },
];

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

  renderFeatureComponent() {
    const { featuresCount, storedFeatures, storedValues } = this.state;

    return featuresCount.map((currentFeature, featureIndex) => {
      const selectedFeature = Object.keys(storedFeatures).length ? storedFeatures[featureIndex] : null;
      const selectedValue = Object.keys(storedValues).length ? storedValues[featureIndex] : null;
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
              options={featureOptions}
              placeholder="Select / Search a Feature"
              onChange={(value) => this.onFeatureOptionUpdate(featureIndex, value)}
              value={selectedFeature}
            />
          </td>
          <td>
            <div className="separator" />
          </td>
          <td width="30%">
            <Select
              isSearchable={false}
              isMulti={false}
              classNamePrefix="sibyl-select"
              className="sibyl-select"
              options={featureValues}
              placeholder="Change Value"
              onChange={(value) => this.onFeatureValueUpdate(featureIndex, value)}
              value={selectedValue}
            />
          </td>
          <td align="center" width="9%">
            <ul className="feature-controls">
              <li>
                <button type="button" className="clean reset-feature" onClick={() => this.onResetFeature(featureIndex)}>
                  Reset
                </button>
              </li>
              <li>
                {featureIndex !== 0 && (
                  <button type="button" className="clean trash" onClick={() => this.onRemoveFeature(featureIndex)}>
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

  onResetFeature(featureIndex) {
    this.setState({
      storedFeatures: {
        ...this.state.storedFeatures,
        [featureIndex]: null,
      },
      storedValues: {
        ...this.state.storedValues,
        [featureIndex]: null,
      },
    });
  }

  onFeatureOptionUpdate(featureIndex, featureValue) {
    this.setState({
      storedFeatures: {
        ...this.state.storedFeatures,
        [featureIndex]: featureValue,
      },
    });
  }

  onFeatureValueUpdate(valueIndex, value) {
    this.setState({
      storedValues: {
        ...this.state.storedValues,
        [valueIndex]: value,
      },
    });
  }

  onAddFeature() {
    const { featuresCount, maxFeaturesCount } = this.state;
    if (featuresCount.length === maxFeaturesCount) {
      return null;
    }

    this.setState({ featuresCount: [...featuresCount, featuresCount.length + 1] });
  }

  onRemoveFeature(featureIndex) {
    const { featuresCount, storedFeatures, storedValues } = this.state;
    if (featuresCount.length === 1) {
      return;
    }

    featuresCount.splice(featuresCount.indexOf(featureIndex), 1);
    delete storedFeatures[featureIndex];
    delete storedValues[featureIndex];
    this.setState({ featuresCount });
  }

  render() {
    const { featuresCount, maxFeaturesCount, isModalOpen } = this.state;

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
            Updated Prediction: <strong>19</strong>
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
          <ModalDialog isOpen={isModalOpen} title="Notice" onClose={() => this.toggleModalState(false)}>
            <p>
              The predictions on this screen show how the model’s predictions would change under different
              circumstances. Here, you can look into what the model values, and make changes based on information you
              may have.
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
        </div>
      </div>
    );
  }
}

export default SandboxFilters;
