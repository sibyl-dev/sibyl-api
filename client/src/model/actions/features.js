import { api } from '../api/api';
import { modelID } from './entities';
import { getCurrentEntityID } from '../selectors/entities';
import { getModelPredictionPayload } from '../selectors/features';

export function getCategoriesAction() {
  return function (dispatch) {
    const action = {
      type: 'GET_CATEGORIES',
      promise: api.get('/categories/'),
    };
    dispatch(action);
  };
}

export function getFeaturesImportanceAction() {
  return function (dispatch) {
    const action = {
      type: 'GET_FEATURES_IMPORTANCES',
      promise: api.get(`/importance/?model_id=${modelID}`),
    };
    dispatch(action);
  };
}

export function getFeaturesAction() {
  return function (dispatch) {
    const action = {
      type: 'GET_FEATURES_DATA',
      promise: api.get('/features/'),
    };

    dispatch(action).then(dispatch(getFeaturesImportanceAction()));
  };
}

export function updateFeaturePredictionScore(featuresData) {
  return function (dispatch, getState) {
    const entityID = getCurrentEntityID(getState());
    const payLoad = {
      eid: entityID,
      model_id: modelID,
      changes: featuresData,
    };

    api
      .post('/modified_prediction/', payLoad)
      .then((response) => response.json())
      .then((score) => dispatch({ type: 'UPDATE_FEATURE_PREDICTION_SUCCESS', newFeatureScore: score.prediction }));
  };
}

export function getModelPredictionAction() {
  return function (dispatch, getState) {
    const entityID = getCurrentEntityID(getState());
    const { currentFeatures, reversedFeatures } = getModelPredictionPayload(getState());
    const currentPredictionPayload = {
      eid: entityID,
      model_id: modelID,
      changes: currentFeatures,
    };

    const reversePredictionPayload = {
      eid: entityID,
      model_id: modelID,
      changes: reversedFeatures,
    };
    dispatch({ type: 'GET_MODEL_PREDICTION_REQUEST' });

    api
      .post('/single_change_predictions/', currentPredictionPayload)
      .then((res) => res.json())
      .then((prediction) => {
        api
          .post('/single_change_predictions/', reversePredictionPayload)
          .then((response) => response.json())
          .then((reversePredict) => {
            dispatch({
              type: 'GET_MODEL_PREDICTION_SUCCESS',
              currentPrediction: prediction.changes,
              reversedPrediction: reversePredict.changes,
            });
          });
      })
      .catch((error) => dispatch({ type: 'GET_MODEL_PREDICTION_FAILURE', error }));
  };
}

export function setFilterCriteriaAction(filterValue) {
  return function (dispatch) {
    dispatch({ type: 'SET_FILTER_CRITERIA', filterCriteria: filterValue });
  };
}
