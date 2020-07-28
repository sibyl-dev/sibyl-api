import Cookies from 'universal-cookie';
import { api } from '../api/api';
import { getFeaturesAction, getCategoriesAction } from './features';
import { getCurrentEntityID, getActivePredictionScore } from '../selectors/entities';

export const modelID = '5f0dc12ea69e913b28b44292';

export function setEntityIdAction(entityID) {
  return function (dispatch) {
    const cookies = new Cookies();
    cookies.remove('entityID');
    cookies.set('entityID', entityID, { path: '/' });
    const action = {
      type: 'SET_ENTITY_ID',
      entityID: parseInt(entityID),
    };
    dispatch(action);
  };
}

export function getEntityContributionsAction() {
  return function (dispatch, getState) {
    const entityID = getCurrentEntityID(getState());
    dispatch({ type: 'GET_ENTITY_CONTRIBUTIONS_REQUEST' });

    api
      .post(`/contributions/`, { eid: entityID, model_id: modelID })
      .then((response) => response.json())
      .then((data) => {
        dispatch({ type: 'GET_ENTITY_CONTRIBUTIONS_SUCCESS', entityContributions: data.contributions });
      })
      .catch((error) => dispatch({ type: 'GET_ENTITY_CONTRIBUTIONS_FAILURE', error }));
  };
}

export function getEntityPredictionScoreAction() {
  return function (dispatch, getState) {
    const entityID = getCurrentEntityID(getState());
    const action = {
      type: 'GET_ENTITY_SCORE',
      promise: api.get(`/prediction/?model_id=${modelID}&eid=${entityID}`),
    };
    dispatch(action);
  };
}

export function getEntityFeatureDistributionAction() {
  return function (dispatch, getState) {
    dispatch({ type: 'GET_ENTITY_DISTRIBUTIONS_REQUEST' });
    const predictionScore = getActivePredictionScore(getState());
    api
      .post(`/feature_distributions/`, { prediction: predictionScore, model_id: modelID })
      .then((response) => response.json())
      .then((entityData) => {
        dispatch({ type: 'GET_ENTITY_DISTRIBUTIONS_SUCCESS', entityDistributions: entityData.distributions });
      })
      .catch((err) => dispatch('GET_ENTITY_DISTRIBUTIONS_FAILURE', err));
  };
}

export function setPredictionScoreAction(predictionScore) {
  return function (dispatch) {
    const setActiveScoreAction = {
      type: 'SET_PREDICTION_SCORE',
      predictionScore,
    };

    dispatch(setActiveScoreAction).then(dispatch(getEntityFeatureDistributionAction()));
  };
}

export function getEntityAction() {
  return function (dispatch, getState) {
    const entityID = getCurrentEntityID(getState());

    const action = {
      type: 'GET_ENTITY_DATA',
      promise: api.get(`/entities/${entityID}/`),
    };

    dispatch(action);
    dispatch(getCategoriesAction());
    dispatch(getFeaturesAction());
    dispatch(getEntityContributionsAction());
    dispatch(getEntityPredictionScoreAction());
  };
}
