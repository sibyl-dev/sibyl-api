import { api } from '../api/api';
import { getCurrentUserID, getCurrentEntityID } from '../selectors/entities';

export function setUserActionRecording(userActions) {
  return function (dispatch, getState) {
    const userID = getCurrentUserID(getState());
    if (userActions === undefined) {
      return;
    }

    const eid = getCurrentEntityID(getState());

    const payLoad = {
      timestamp: new Date().getTime(),
      user_id: userID,
      event: userActions,
      eid,
    };
    api.post('/logging/', payLoad);
  };
}
