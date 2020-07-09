import createReducer from '../store/createReducer';

const initialState = {
  isEntityDataLoading: true,
  entityData: [],
  entityID: null,
};
function GET_ENTITY_DATA_REQUEST(nextState) {
  nextState.isEntityDataLoading = true;
}
function GET_ENTITY_DATA_SUCCESS(nextState, action) {
  nextState.entityData = action.result;
  nextState.isEntityDataLoading = false;
}

function GET_ENTITY_DATA_FAILURE(nextState) {
  nextState.entityData = [];
  nextState.isEntityDataLoading = false;
}

function SET_ENTITY_ID(nextState, { entityID }) {
  nextState.entityID = entityID;
}

export default createReducer(initialState, {
  GET_ENTITY_DATA_REQUEST,
  GET_ENTITY_DATA_SUCCESS,
  GET_ENTITY_DATA_FAILURE,
  SET_ENTITY_ID,
});
