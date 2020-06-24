export function toggleSidebarStateAction(sidebarState) {
  return function (dispatch) {
    dispatch({
      type: 'TOGGLE_SIDEBAR_STATE',
      isSidebarCollapsed: sidebarState,
    });
  };
}
