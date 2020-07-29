import Cookies from 'universal-cookie';
import { api } from '../api/api';
import { getCurrentEntityID } from '../selectors/entitites';

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

export function getEntityAction() {
  return function (dispatch, getState) {
    let entityID = getCurrentEntityID(getState());
    const cookies = new Cookies();

    if (entityID === null) {
      entityID = cookies.get('entityID');
    }

    const action = {
      type: 'GET_ENTITY_DATA',
      promise: api.get(`/entities/${entityID}`),
    };
    dispatch(action);
  };
}
