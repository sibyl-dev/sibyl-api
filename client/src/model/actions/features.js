import { api } from '../api/api';

export function getCategoriesAction() {
  return function (dispatch) {
    const action = {
      type: 'GET_CATEGORIES',
      promise: api.get('/categories'),
    };
    dispatch(action);
  };
}

export function getFeaturesAction() {
  return function (dispatch) {
    const action = {
      type: 'GET_FEATURES_DATA',
      promise: api.get('/features'),
    };

    dispatch(action);
  };
}
