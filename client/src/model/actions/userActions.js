import { api } from '../api/api';
import { getCurrentUserID } from '../selectors/entities';

export function setUserActionRecording(userActions) {
  return function (dispatch, getState) {
    const userID = getCurrentUserID(getState());
    if (userActions === undefined) {
      return;
    }

    const payLoad = {
      timestamp: new Date().getTime(),
      user_id: userID,
      event: userActions,
    };
    api.post('/logging/', payLoad);
  };
}
