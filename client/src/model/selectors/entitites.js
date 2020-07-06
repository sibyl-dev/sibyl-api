import { createSelector } from 'reselect';

export const getCurrentEntityData = (state) => state.entities.entityData;
export const getIsEntitiesLoading = (state) => state.entities.isEntityDataLoading;

// @TODO - finish and use this selector for entityData,
// this sorts contributions in descendat order
export const getCurrentEntityDataSorted = createSelector(
  [getIsEntitiesLoading, getCurrentEntityData],
  (isEntitiesLoading, currentEntities) => {
    if (isEntitiesLoading) {
      return [];
    }

    const { contributions } = currentEntities;
    let sortedContrib = [];
    for (let currentContrib in contributions) {
      sortedContrib.push([currentContrib, Number(contributions[currentContrib])]);
    }

    sortedContrib.sort((a, b) => b[1] - a[1]);

    return currentEntities;
  },
);

export const entities = createSelector(
  [getIsEntitiesLoading, getCurrentEntityData],
  (isEntitiesLoading, entityData) => {
    if (isEntitiesLoading) {
      return;
    }
    return entityData;
  },
);
