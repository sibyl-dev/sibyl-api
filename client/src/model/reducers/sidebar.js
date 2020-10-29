import createReducer from '../store/createReducer';

const initialState = {
  isSidebarCollapsed: false,
  pageName: 'Score',
};

function TOGGLE_SIDEBAR_STATE(nextState, { isSidebarCollapsed }) {
  nextState.isSidebarCollapsed = isSidebarCollapsed;
}

function SET_ACTIVE_PAGE(nextState, { pageName }) {
  nextState.pageName = pageName;
}

export default createReducer(initialState, {
  TOGGLE_SIDEBAR_STATE,
  SET_ACTIVE_PAGE,
});
