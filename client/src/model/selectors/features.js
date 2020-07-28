import { createSelector } from 'reselect';
import { getCurrentEntityData, getEntityContributions } from './entities';

export const getFeaturesImportances = (state) => state.features.featuresImportances;
export const getIsFeaturesLoading = (state) => state.features.isFeaturesLoading;
export const getIsCategoriesLoading = (state) => state.features.isCategoriesLoading;
export const getCurrentFeatureCategories = (state) => state.features.categories;
export const getCurrentFeatures = (state) => state.features.featuresData;
export const getUpdatedFeatureScore = (state) => state.features.newFeatureScore;
export const getIsModelPredictLoading = (state) => state.features.isModelPredictionLoading;
export const getCurrentModelPrediction = (state) => state.features.currendModelPredition;
export const getReversedModelPrediction = (state) => state.features.reversedModelPrediction;
export const getFeaturesFilterCriteria = (state) => state.features.filterCriteria;
export const getSortingContribDir = (state) => state.features.sortContribDir;
export const getSelectedFilterValues = (state) => state.features.filterValue;
export const getFilterCategories = (state) => state.features.filterCategs;

export const getFeaturesData = createSelector(
  [
    getIsFeaturesLoading,
    getCurrentFeatures,
    getCurrentEntityData,
    getEntityContributions,
    getFeaturesFilterCriteria,
    getSortingContribDir,
    getSelectedFilterValues,
    getFilterCategories,
  ],
  (
    isFeaturesLoading,
    features,
    entityData,
    contributions,
    filterCriteria,
    sortContribDir,
    filterValues,
    filterCategs,
  ) => {
    const entityFeatures = entityData.features;
    let processedFeatures = [];

    features.map((currentFeature) => {
      processedFeatures.push({
        ...currentFeature,
        [currentFeature.name]: entityFeatures[currentFeature.name],
        contributionValue: contributions[currentFeature.name],
      });
    });

    processedFeatures.sort((current, next) =>
      sortContribDir === 'asc'
        ? next.contributionValue - current.contributionValue
        : current.contributionValue - next.contributionValue,
    );

    if (filterValues !== 'all') {
      processedFeatures = processedFeatures.filter((currentFeature) => currentFeature.type === filterValues);
    }

    if (filterCriteria) {
      const regex = new RegExp(filterCriteria, 'gi');
      processedFeatures = processedFeatures.filter((currentFeature) => currentFeature.description.match(regex));
    }

    if (filterCategs !== null && filterCategs.length > 0) {
      processedFeatures = processedFeatures.filter(
        (currentFeature) => filterCategs.indexOf(currentFeature.category) !== -1,
      );
    }

    const positiveFeaturesContrib = processedFeatures.filter((currentFeature) => currentFeature.contributionValue > 0);
    const negativeFeaturesContrib = processedFeatures.filter((currentFeature) => currentFeature.contributionValue < 0);

    negativeFeaturesContrib.sort((current, next) =>
      sortContribDir === 'asc'
        ? current.contributionValue - next.contributionValue
        : next.contributionValue - current.contributionValue,
    );

    return !isFeaturesLoading ? { processedFeatures, positiveFeaturesContrib, negativeFeaturesContrib } : [];
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

    let currentPredictionData = {};
    currentPrediction.map((predictItem, predIndex) => {
      if (predictItem[0] === reversedPrediction[predIndex][0]) {
        const currentDiff = reversedPrediction[predIndex][1] - predictItem[1];
        const data = {
          reversedScore: reversedPrediction[predIndex][1],
          currentDifference: currentDiff,
        };
        Object.assign(currentPredictionData, { ...currentPredictionData, [predictItem[0]]: data });
      }
    });
    return currentPredictionData;
  },
);

export const getFeatureCategories = createSelector(
  [getIsCategoriesLoading, getCurrentFeatureCategories],
  (isCategoriesLoading, featureCategories) => {
    if (isCategoriesLoading) {
      return [];
    }
    const categoryColors = [
      '#eb5757',
      '#f2994a',
      '#21b0b0',
      '#27ae60',
      '#9B51E0',
      '#2D9CDB',
      '#FF5146',
      '#219653',
      '#2F80ED',
      '#9e09b8',
      '#b8096e',
      '#2e6ccb',
    ];
    let categories = [];

    featureCategories.map((currentCategory, catIndex) => {
      categories.push({
        name: currentCategory.name,
        color: currentCategory.color === null ? categoryColors[catIndex] : currentCategory.color,
      });
    });

    return categories;
  },
);
