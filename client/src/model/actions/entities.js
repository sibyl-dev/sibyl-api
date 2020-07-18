import Cookies from 'universal-cookie';
import { api } from '../api/api';
import { getFeaturesAction, getCategoriesAction } from './features';
import { getCurrentEntityID } from '../selectors/entities';

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

export function getEntityAction() {
  return function (dispatch, getState) {
    const entityID = getCurrentEntityID(getState());

    const action = {
      type: 'GET_ENTITY_DATA',
      promise: api.get(`/entities/${entityID}/`),
    };

    dispatch(action)
      .then(dispatch(getCategoriesAction()))
      .then(dispatch(getFeaturesAction()))
      .then(dispatch(getEntityContributionsAction()))
      .then(dispatch(getEntityPredictionScoreAction()));
  };
}
