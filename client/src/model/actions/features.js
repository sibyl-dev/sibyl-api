import { api } from '../api/api';
import { modelID } from './entities';

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
