import { api } from '../api/api';
import { getCurrentEntityID } from '../selectors/entities';

export function setUserActionRecording(userActions) {
  return function (dispatch, getState) {
    const entityID = getCurrentEntityID(getState());
    if (userActions === undefined) {
      return;
    }

    const payLoad = {
      timestamp: new Date().getTime(),
      user_id: entityID,
      event: userActions,
    };
    api.post('/logging/', payLoad);
  };
}
