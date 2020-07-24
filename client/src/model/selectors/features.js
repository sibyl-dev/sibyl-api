import { createSelector } from 'reselect';
import { getCurrentEntityData } from './entities';

export const getFeaturesImportances = (state) => state.features.featuresImportances;
export const getIsFeaturesLoading = (state) => state.features.isFeaturesLoading;
export const getIsCategoriesLoading = (state) => state.features.isCategoriesLoading;
export const getFeatureCategories = (state) => state.features.categories;
export const getCurrentFeatures = (state) => state.features.featuresData;
export const getUpdatedFeatureScore = (state) => state.features.newFeatureScore;
export const getIsModelPredictLoading = (state) => state.features.isModelPredictionLoading;
export const getCurrentModelPrediction = (state) => state.features.currendModelPredition;
export const getReversedModelPrediction = (state) => state.features.reversedModelPrediction;

// @TODO - later sort
export const getFeaturesImportancesSorted = createSelector(
  [getFeaturesImportances, getIsFeaturesLoading, getCurrentFeatures],
  (importances, isFeaturesLoading, currentFeatures) => {
    const sortable = [];

    for (var importanceValues in importances) {
      sortable.push([importanceValues, importances[importanceValues]]);
    }

    sortable.sort(function (a, b) {
      return b[1] - a[1];
    });

    let sortedImportances = {};
    sortable.forEach(function (item) {
      sortedImportances[item[0]] = item[1];
      console.log(item[1]);
    });

    return sortedImportances;
  },
);

export const getFeaturesData = createSelector(
  [getIsFeaturesLoading, getCurrentFeatures],
  (isFeaturesLoading, features) => {
    return !isFeaturesLoading ? features : [];
  },
);

export const getModelPredictionPayload = createSelector(
  [getIsFeaturesLoading, getCurrentFeatures, getCurrentEntityData],
  (isFeaturesLoading, features, entityData) => {
    if (isFeaturesLoading) {
      return;
    }

    const currentFeatures = [];
    const reversedFeatures = [];
    features.map((currentFeature) => {
      const currentValue = entityData.features[currentFeature.name];

      if (currentFeature.type === 'binary' && currentValue <= 1) {
        currentFeatures.push([currentFeature.name, currentValue]);
        reversedFeatures.push([currentFeature.name, currentValue === 1 ? 0 : 1]);
      }
    });

    return { currentFeatures, reversedFeatures };
  },
);

export const getModelPredictionData = createSelector(
  [getIsModelPredictLoading, getCurrentModelPrediction, getReversedModelPrediction, getCurrentEntityData],
  (isModelLoading, currentPrediction, reversedPrediction, entityData) => {
    if (isModelLoading) {
      return;
    }
    const { features } = entityData;
    let currentPredictionData = {};

    currentPrediction.map((predictItem, predIndex) => {
      if (predictItem[0] === reversedPrediction[predIndex][0]) {
        const currentDiff = predictItem[1] - reversedPrediction[predIndex][1];
        const reversedDiff = reversedPrediction[predIndex][1] - predictItem[1];
        const data = {
          currentScore: predictItem[1],
          reversedScore: reversedPrediction[predIndex][1],
          currentDifference: currentDiff,
          reversedDifference: reversedDiff,
          currentOrder: features[predictItem[0]],
        };
        Object.assign(currentPredictionData, { ...currentPredictionData, [predictItem[0]]: data });
      }
    });
    return currentPredictionData;
  },
);
