import createReducer from '../store/createReducer';
const initialState = {
  isSidebarCollapsed: true,
};

function TOGGLE_SIDEBAR_STATE(nextState, { isSidebarCollapsed }) {
  nextState.isSidebarCollapsed = isSidebarCollapsed;
}

export default createReducer(initialState, {
  TOGGLE_SIDEBAR_STATE,
});
