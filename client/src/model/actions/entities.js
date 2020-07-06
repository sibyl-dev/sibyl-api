import { api } from '../api/api';

export function getEntityAction(entityID) {
  return function (dispatch) {
    const action = {
      type: 'GET_ENTITY',
      promise: api.get(`/entities/${entityID}`),
    };
    dispatch(action);
  };
}
