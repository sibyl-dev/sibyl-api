export function toggleSidebarStateAction(sidebarState) {
  return function (dispatch) {
    dispatch({
      type: 'TOGGLE_SIDEBAR_STATE',
      isSidebarCollapsed: sidebarState,
    });
  };
}

export function setActivePageAction(pageName) {
  return function (dispatch) {
    dispatch({
      type: 'SET_ACTIVE_PAGE',
      pageName,
    });
  };
}
