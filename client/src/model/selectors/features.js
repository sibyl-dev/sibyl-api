import { createSelector } from 'reselect';
import { getCurrentEntityData, getEntityContributions, getIsEntitiesLoading } from './entities';

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
export const getModelPredDiffFilterValue = (state) => state.features.diffFilterVal;
export const getFeatureTypeFilters = (state) => state.features.featureTypeFilters;
export const getFeatureTypeSortContribDir = (state) => state.features.featureTypeSortDir;
export const getFeatureTypeFilterCategs = (state) => state.features.featureTypeFilterCategs;
export const getFeatureImpSortDir = (state) => state.features.featureImpSortDir;

const maxNegativeContrib = -0.000000001;

const roundContribValue = (contribValue) => {
  if (contribValue >= 0) {
    return contribValue;
  }
  return contribValue < maxNegativeContrib ? contribValue : 0;
};

export const getMaxContributionRange = createSelector(
  [getIsFeaturesLoading, getIsEntitiesLoading, getCurrentFeatures, getCurrentEntityData, getEntityContributions],
  (isFeaturesLoading, isEntityDataLoading, currentFeatures, entityData, contributions) => {
    if (isFeaturesLoading || isEntityDataLoading) {
      return null;
    }

    const entityFeatures = entityData.features;
    let processedFeatures = [];
    let maxRange = 0;

    currentFeatures.forEach((currentFeature) => {
      processedFeatures.push({
        ...currentFeature,
        [currentFeature.name]: entityFeatures[currentFeature.name],
        contributionValue: roundContribValue(contributions[currentFeature.name]),
      });
      return processedFeatures;
    });

    processedFeatures.map((feature) => {
      const { contributionValue } = feature;
      maxRange = maxRange > Math.abs(contributionValue) ? maxRange : Math.abs(contributionValue);
      return null;
    });

    return maxRange;
  },
);

// @TODO - update getMaxContributionRange to  return processedFeatures and not the maxRange only
export const getFeaturesData = createSelector(
  [
    getIsFeaturesLoading,
    getIsEntitiesLoading,
    getCurrentFeatures,
    getCurrentEntityData,
    getEntityContributions,
    getFeaturesFilterCriteria,
    getSortingContribDir,
    getSelectedFilterValues,
    getFilterCategories,
    getCurrentContribFilters,
    getFeaturesImportances,
  ],
  (
    isFeaturesLoading,
    isEntityDataLoading,
    features,
    entityData,
    contributions,
    filterCriteria,
    sortContribDir,
    filterValues,
    filterCategs,
    contribFilters,
    featureImportance,
  ) => {
    if (isFeaturesLoading || isEntityDataLoading) {
      return [];
    }

    const entityFeatures = entityData.features;
    let processedFeatures = [];

    features.map((currentFeature) => {
      processedFeatures.push({
        ...currentFeature,
        [currentFeature.name]: entityFeatures[currentFeature.name],
        contributionValue: roundContribValue(contributions[currentFeature.name]),
        featureImportance: featureImportance[currentFeature.name],
      });
      return processedFeatures;
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
      processedFeatures = processedFeatures.filter((currentFeature) => {
        const { type, name } = currentFeature;
        if (type === 'binary' && entityFeatures[name] === 0) {
          return currentFeature.negated_description.match(regex);
        }
        return currentFeature.description.match(regex);
      });
    }

    if (filterCategs !== null && filterCategs.length > 0) {
      processedFeatures = processedFeatures.filter(
        (currentFeature) => filterCategs.indexOf(currentFeature.category) !== -1,
      );
    }

    let positiveFeaturesContrib = processedFeatures.filter((currentFeature) => currentFeature.contributionValue > 0);
    let negativeFeaturesContrib = processedFeatures.filter((currentFeature) => currentFeature.contributionValue < 0);

    if (contribFilters === 'risk') {
      processedFeatures = positiveFeaturesContrib;
    }

    if (contribFilters === 'protective') {
      processedFeatures = negativeFeaturesContrib;
    }

    return { processedFeatures };
  },
);

export const getGrouppedFeatures = createSelector(
  [
    getIsFeaturesLoading,
    getIsEntitiesLoading,
    getCurrentFeatures,
    getCurrentEntityData,
    getEntityContributions,
    getFeatureTypeFilters,
    getFeatureTypeSortContribDir,
    getFeaturesFilterCriteria,
    getFeatureTypeFilterCategs,
  ],
  (
    isFeaturesLoading,
    isEntityDataLoading,
    currentFeatures,
    entityData,
    contributions,
    featureTypeFilters,
    featureSortDir,
    filterCriteria,
    filterCategs,
  ) => {
    if (isFeaturesLoading || isEntityDataLoading) {
      return [];
    }

    const entityFeatures = entityData.features;
    let processedFeatures = [];

    currentFeatures.map((currentFeature) =>
      processedFeatures.push({
        ...currentFeature,
        [currentFeature.name]: entityFeatures[currentFeature.name],
        contributionValue: roundContribValue(contributions[currentFeature.name]),
      }),
    );

    if (filterCriteria) {
      const regex = new RegExp(filterCriteria, 'gi');
      processedFeatures = processedFeatures.filter((currentFeature) => {
        const { type, name } = currentFeature;
        if (type === 'binary' && entityFeatures[name] === 0) {
          return currentFeature.negated_description.match(regex);
        }
        return currentFeature.description.match(regex);
      });
    }

    let positiveFeaturesContrib = processedFeatures.filter((currentFeature) => currentFeature.contributionValue > 0);
    let negativeFeaturesContrib = processedFeatures.filter((currentFeature) => currentFeature.contributionValue < 0);

    positiveFeaturesContrib.sort((current, next) => next.contributionValue - current.contributionValue);
    negativeFeaturesContrib.sort((current, next) => current.contributionValue - next.contributionValue);

    if (featureTypeFilters.negativeFeatures !== 'all') {
      negativeFeaturesContrib = negativeFeaturesContrib.filter(
        (currentFeature) => currentFeature.type === featureTypeFilters.negativeFeatures,
      );
    }

    if (featureTypeFilters.positiveFeatures !== 'all') {
      positiveFeaturesContrib = positiveFeaturesContrib.filter(
        (currentFeature) => currentFeature.type === featureTypeFilters.positiveFeatures,
      );
    }

    positiveFeaturesContrib.sort((current, next) =>
      featureSortDir.positiveFeatures === 'asc'
        ? next.contributionValue - current.contribValue
        : current.contributionValue - next.contributionValue,
    );

    negativeFeaturesContrib.sort((current, next) =>
      featureSortDir.negativeFeatures !== 'asc'
        ? current.contributionValue - next.contribValue
        : next.contributionValue - current.contributionValue,
    );

    if (filterCategs.positiveFeatures !== null && filterCategs.positiveFeatures.length > 0) {
      positiveFeaturesContrib = positiveFeaturesContrib.filter(
        (currentFeature) => filterCategs.positiveFeatures.indexOf(currentFeature.category) !== -1,
      );
    }

    if (filterCategs.negativeFeatures !== null && filterCategs.negativeFeatures.length > 0) {
      negativeFeaturesContrib = negativeFeaturesContrib.filter(
        (currentFeature) => filterCategs.negativeFeatures.indexOf(currentFeature.category) !== -1,
      );
    }

    return { positiveFeaturesContrib, negativeFeaturesContrib };
  },
);

export const getModelPredictionPayload = createSelector(
  [getIsFeaturesLoading, getIsEntitiesLoading, getCurrentFeatures, getCurrentEntityData],
  (isFeaturesLoading, isEntityDataLoading, features, entityData) => {
    if (isFeaturesLoading || isEntityDataLoading) {
      return [];
    }

    const currentFeatures = [];
    const reversedFeatures = [];

    features.map((currentFeature) => {
      const currentValue = entityData.features[currentFeature.name];

      if (currentFeature.type === 'binary' && currentValue <= 1) {
        currentFeatures.push([currentFeature.name, currentValue]);
        reversedFeatures.push([currentFeature.name, currentValue === 1 ? 0 : 1]);
      }
      return null;
    });

    return { currentFeatures, reversedFeatures };
  },
);

export const getModelPredictionData = createSelector(
  [getIsModelPredictLoading, getCurrentModelPrediction, getReversedModelPrediction],
  (isModelLoading, currentPrediction, reversedPrediction) => {
    if (isModelLoading) {
      return [];
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
      return null;
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
    // const categoryColors = [
    //   '#eb5757',
    //   '#f2994a',
    //   '#21b0b0',
    //   '#27ae60',
    //   '#9B51E0',
    //   '#2D9CDB',
    //   '#FF5146',
    //   '#219653',
    //   '#2F80ED',
    //   '#9e09b8',
    //   '#b8096e',
    //   '#2e6ccb',
    // ];

    const categoryColors = [
      '#B30202',
      '#f2994a',
      '#21b0b0',
      '#27ae60',
      '#9B51E0',
      '#B32D90', //
      '#C93655', //
      '#219653',
      '#024EB3', //
      '#9e09b8',
      '#b8096e',
      '#2e6ccb',
    ];
    let categories = [];

    featureCategories.map((currentCategory, catIndex) =>
      categories.push({
        name: currentCategory.name,
        color: currentCategory.color === null ? categoryColors[catIndex] : currentCategory.color,
        abbreviation: currentCategory.abbreviation,
      }),
    );

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
    getModelPredictFilterValue,
    getModelPredDiffFilterValue,
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
    filterValues,
    diffFilter,
  ) => {
    const isDataLoading = isFeaturesLoading || isModelLoading;
    if (isDataLoading) {
      return [];
    }
    const entityFeatures = entityData.features;
    let processedFeatures = [];
    features.map((currentFeature) =>
      processedFeatures.push({
        ...currentFeature,
        [currentFeature.name]: entityFeatures[currentFeature.name],
        contributionValue: roundContribValue(contributions[currentFeature.name]),
        modelPrediction:
          modelPredictData[currentFeature.name] !== undefined ? modelPredictData[currentFeature.name] : null,
      }),
    );

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

    if (filterValues !== 'all') {
      processedFeatures =
        filterValues === 'true'
          ? processedFeatures.filter((currentFeature) => currentFeature[currentFeature.name] === 0)
          : processedFeatures.filter((currentFeature) => currentFeature[currentFeature.name] !== 0);
    }

    if (diffFilter !== 'difference') {
      processedFeatures = diffFilter === 'risk' ? negativeFeaturesContrib : positiveFeaturesContrib;
    }

    return processedFeatures;
  },
);

export const getSortedByImportanceFeatures = createSelector(
  [getIsFeaturesLoading, getFeaturesData, getFeatureImpSortDir],
  (isFeaturesLoading, featuresData, sortDir) => {
    if (isFeaturesLoading) {
      return [];
    }

    const { processedFeatures } = featuresData;

    const sortedFeatures = processedFeatures.sort((prevFeature, nextFeature) =>
      sortDir === 'asc'
        ? nextFeature.featureImportance - prevFeature.featureImportance
        : prevFeature.featureImportance - nextFeature.featureImportance,
    );

    return sortedFeatures;
  },
);
