import createReducer from '../store/createReducer';

const initialState = {
  isEntityDataLoading: true,
  entityData: [],
};
function GET_ENTITY_REQUEST(nextState) {
  nextState.isEntityDataLoading = true;
}
function GET_ENTITY_SUCCESS(nextState, action) {
  nextState.entityData = action.result;
  nextState.isEntityDataLoading = false;
}

function GET_ENTITY_FAILURE(nextState) {
  nextState.entityData = [];
  nextState.isEntityDataLoading = false;
}

export default createReducer(initialState, {
  GET_ENTITY_REQUEST,
  GET_ENTITY_SUCCESS,
  GET_ENTITY_FAILURE,
});
