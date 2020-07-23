import { api } from '../api/api';
import { modelID } from './entities';
import { getCurrentEntityID } from '../selectors/entities';

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
