import { createSelector } from 'reselect';

export const getFeaturesImportances = (state) => state.features.featuresImportances;
export const getIsFeaturesLoding = (state) => state.features.isFeaturesLoading;
export const getIsCategoriesLoading = (state) => state.features.isCategoriesLoading;
export const getFeatureCategories = (state) => state.features.categories;
export const getCurrentFeatures = (state) => state.features.featuresData;

// @TODO - later sort
export const getFeaturesImportancesSorted = createSelector(
  [getFeaturesImportances, getIsFeaturesLoding],
  (importances, isFeaturesLoading) => {
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
    debugger;
    return sortedImportances;
  },
);

export const getFeaturesData = createSelector(
  [getIsFeaturesLoding, getCurrentFeatures],
  (isFeaturesLoading, features) => {
    return !isFeaturesLoading ? features : [];
  },
);
