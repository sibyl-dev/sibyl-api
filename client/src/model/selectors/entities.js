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

export const currentEntityID = (state) => state.entities.entityID;

export const getCurrentEntityID = createSelector([currentEntityID], (entityID) => {
  const cookies = new Cookies();

  if (entityID === null) {
    entityID = cookies.get('entityID');
  }
  return entityID;
});

export const getActivePredictionScore = createSelector(
  [getPredictionScore, getEntityScore],
  (predictionScore, entityScore) => (predictionScore !== null ? predictionScore : entityScore),
);
