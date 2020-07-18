import { createSelector } from 'reselect';

export const getIsFeaturesLoding = (state) => state.features.isFeaturesLoading;
export const getIsCategoriesLoading = (state) => state.features.isCategoriesLoading;
export const getFeatureCategories = (state) => state.features.categories;
export const getCurrentFeatures = (state) => state.features.featuresData;

export const getFeaturesData = createSelector(
  [getIsFeaturesLoding, getCurrentFeatures],
  (isFeaturesLoading, features) => {
    return !isFeaturesLoading ? features : [];
  },
);
