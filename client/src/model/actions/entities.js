import Cookies from 'universal-cookie';
import { api } from '../api/api';
import { getFeaturesAction, getCategoriesAction } from './features';
import {
  getCurrentEntityID,
  getActivePredictionScore,
  getPredictionScore,
  getCurrentModelID,
} from '../selectors/entities';
import { setUserActionRecording } from './userActions';

export function setEntityIdAction(entityID) {
  return function (dispatch) {
    const cookies = new Cookies();
    cookies.remove('entityID');
    cookies.set('entityID', entityID, { path: '/' });
    const action = {
      type: 'SET_ENTITY_ID',
      entityID,
    };
    return dispatch(action);
  };
}

export function setUserIdAction(userID) {
  return function (dispatch) {
    const cookies = new Cookies();
    cookies.remove('entityID');
    cookies.set('userID', userID, { path: '/' });
    const action = {
      type: 'SET_USER_ID',
      userID,
    };

    return dispatch(action);
  };
}

export function getModelIDAction() {
  return function (dispatch) {
    dispatch({ type: 'GET_MODEL_ID_REQUEST' });

    return api
      .get(`/{path_to_model_id_endpoint}`)
      .then((response) => response.json())
      .then((data) => dispatch({ type: 'GET_MODEL_ID_SUCCESS', modelID: data }))
      .catch(() => dispatch({ type: 'GET_MODEL_ID_FAILURE' }));
  };
}

export function getEntityContributionsAction() {
  return function (dispatch, getState) {
    const entityID = getCurrentEntityID(getState());
    const modelID = getCurrentModelID(getState());
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
    const modelID = getCurrentModelID(getState());

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
    const modelID = getCurrentModelID(getState());
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
  return function (dispatch, getState) {
    const currentPredictionScore = getPredictionScore(getState());

    if (predictionScore === currentPredictionScore) {
      return;
    }

    const setActiveScoreAction = {
      type: 'SET_PREDICTION_SCORE',
      predictionScore,
    };

    dispatch(setActiveScoreAction)
      .then(dispatch(getEntityFeatureDistributionAction()))
      .then(dispatch(getOutcomeCountAction()));

    const userRecordPayload = {
      element: 'score_bar',
      action: 'filter',
      details: predictionScore,
    };

    dispatch(setUserActionRecording(userRecordPayload));
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

export function getOutcomeCountAction() {
  return function (dispatch, getState) {
    const predictionScore = getPredictionScore(getState());

    if (predictionScore === null) {
      return;
    }

    const modelID = getCurrentModelID(getState());

    return api
      .post('/outcome_count/', { prediction: predictionScore, model_id: modelID })
      .then((data) => data.json())
      .then((outcomeData) => dispatch({ type: 'GET_OUTCOME_COUNT_SUCCESS', outcomeData }));
  };
}
