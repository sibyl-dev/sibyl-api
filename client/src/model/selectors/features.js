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
export const getCurrentContribFilters = (state) => state.features.contribFilters;
export const getCurrentPredSortDir = (state) => state.features.sortPredDirection;
export const getCurrentSortDiffDir = (state) => state.features.sortDiffDirection;
export const getModelPredictFilterValue = (state) => state.features.modelPredFilterValue;

const maxNegativeContrib = -0.000000001;

const roundContribValue = (contribValue) => {
  if (contribValue >= 0) {
    return contribValue;
  }
  return contribValue < maxNegativeContrib ? contribValue : 0;
};

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
    getCurrentContribFilters,
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
    contribFilters,
  ) => {
    if (isFeaturesLoading) {
      return [];
    }

    const entityFeatures = entityData.features;
    let processedFeatures = [];

    features.map((currentFeature) => {
      processedFeatures.push({
        ...currentFeature,
        [currentFeature.name]: entityFeatures[currentFeature.name],
        contributionValue: roundContribValue(contributions[currentFeature.name]),
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

    if (contribFilters === 'risk') {
      processedFeatures = negativeFeaturesContrib;
    }

    if (contribFilters === 'protective') {
      processedFeatures = positiveFeaturesContrib;
    }

    return { processedFeatures, positiveFeaturesContrib, negativeFeaturesContrib };
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
  [getIsModelPredictLoading, getCurrentModelPrediction, getReversedModelPrediction],
  (isModelLoading, currentPrediction, reversedPrediction) => {
    if (isModelLoading) {
      return;
    }

    let currentPredictionData = {};
    currentPrediction.map((predictItem) => {
      const reversedPredIndex = reversedPrediction.findIndex((currentPred) => currentPred[0] === predictItem[0]);
      const currentDiff = reversedPrediction[reversedPredIndex][1] - predictItem[1];
      const data = {
        reversedScore: reversedPrediction[reversedPredIndex][1],
        currentDifference: currentDiff,
      };
      Object.assign(currentPredictionData, { [predictItem[0]]: data });
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

export const getReversedModelPredFeatures = createSelector(
  [
    getIsFeaturesLoading,
    getCurrentFeatures,
    getIsModelPredictLoading,
    getModelPredictionData,
    getCurrentEntityData,
    getEntityContributions,
    getCurrentPredSortDir,
    getCurrentSortDiffDir,
    getFilterCategories,
    getFeaturesFilterCriteria,
    getCurrentContribFilters,
    getModelPredictFilterValue,
  ],
  (
    isFeaturesLoading,
    features,
    isModelLoading,
    modelPredictData,
    entityData,
    contributions,
    predictSortDir,
    sortDiffDir,
    filterCategs,
    filterCriteria,
    contribFilters,
    filterValues,
  ) => {
    const isDataLoading = isFeaturesLoading || isModelLoading;
    if (isDataLoading) {
      return [];
    }
    const entityFeatures = entityData.features;
    let processedFeatures = [];

    features.map((currentFeature) => {
      processedFeatures.push({
        ...currentFeature,
        [currentFeature.name]: entityFeatures[currentFeature.name],
        contributionValue: roundContribValue(contributions[currentFeature.name]),
        modelPrediction:
          modelPredictData[currentFeature.name] !== undefined ? modelPredictData[currentFeature.name] : null,
      });
    });

    processedFeatures = processedFeatures.filter((currentFeature) => currentFeature.modelPrediction !== null);

    predictSortDir !== null &&
      processedFeatures.sort((current, next) =>
        predictSortDir === 'asc'
          ? current.modelPrediction.reversedScore - next.modelPrediction.reversedScore
          : next.modelPrediction.reversedScore - current.modelPrediction.reversedScore,
      );

    sortDiffDir !== null &&
      processedFeatures.sort((current, next) =>
        sortDiffDir === 'asc'
          ? current.modelPrediction.currentDifference - next.modelPrediction.currentDifference
          : next.modelPrediction.currentDifference - current.modelPrediction.currentDifference,
      );

    if (filterCategs !== null && filterCategs.length > 0) {
      processedFeatures = processedFeatures.filter(
        (currentFeature) => filterCategs.indexOf(currentFeature.category) !== -1,
      );
    }

    if (filterCriteria) {
      const regex = new RegExp(filterCriteria, 'gi');
      processedFeatures = processedFeatures.filter((currentFeature) => currentFeature.description.match(regex));
    }

    const positiveFeaturesContrib = processedFeatures.filter(
      (currentFeature) => currentFeature.modelPrediction.currentDifference > 0,
    );

    const negativeFeaturesContrib = processedFeatures.filter(
      (currentFeature) => currentFeature.modelPrediction.currentDifference < 0,
    );

    if (contribFilters === 'risk') {
      processedFeatures = negativeFeaturesContrib;
    }

    if (contribFilters === 'protective') {
      processedFeatures = positiveFeaturesContrib;
    }

    if (filterValues !== 'all') {
      processedFeatures =
        filterValues === 'true'
          ? processedFeatures.filter((currentFeature) => currentFeature[currentFeature.name] === 0)
          : processedFeatures.filter((currentFeature) => currentFeature[currentFeature.name] !== 0);
    }

    return processedFeatures;
  },
);
