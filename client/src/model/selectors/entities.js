import { createSelector } from 'reselect';
import Cookies from 'universal-cookie';

export const getIsEntitiesLoading = (state) => state.entities.isEntityDataLoading;
export const getCurrentEntityData = (state) => state.entities.entityData;
export const getIsEntityContribLoading = (state) => state.entities.isEntityContributionsLoading;
export const getEntityContributions = (state) => state.entities.entityContributions;
export const getIsEntityScoreLoading = (state) => state.entities.isEntityScoreLoading;
export const getEntityScore = (state) => state.entities.entityScore;
export const getIsEntityDistributionsLoading = (state) => state.entities.isEntityDistributionsLoading;
export const getEntityDistributions = (state) => state.entities.entityDistributions;
export const getPredictionScore = (state) => state.entities.predictionScore;
export const getIsOutcomeDataLoading = (state) => state.entities.isOutcomeDataLoading;
export const getCurrentOutcomeData = (state) => state.entities.outcomeData;
export const getCurrentModels = (state) => state.entities.models;

export const currentUserID = (state) => state.entities.userID;
export const currentEntityID = (state) => state.entities.entityID;

export const getCurrentEntityID = createSelector([currentEntityID], (entityID) => {
  const cookies = new Cookies();

  if (entityID === null) {
    entityID = cookies.get('entityID');
  }
  return entityID || 0;
});

export const getSelectedModelID = createSelector([getCurrentModels], (models) => models[0].id);

export const getCurrentUserID = createSelector([currentUserID], (userID) => {
  const cookies = new Cookies();
  if (userID === null || userID === undefined) {
    userID = cookies.get('userID');
  }

  return userID || 'null';
});

export const getActivePredictionScore = createSelector(
  [getPredictionScore, getEntityScore],
  (predictionScore, entityScore) => (predictionScore !== null ? predictionScore : entityScore),
);
