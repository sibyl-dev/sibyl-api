import reducer from '../../model/reducers/sidebar';

const defaultState = {
  isSidebarCollapsed: false,
  pageName: 'Score',
};

describe('Sidebar Reducer', () => {
  it('returns initial state', () => {
    expect(reducer(undefined, {})).toEqual(defaultState);
  });

  describe('Sidebar Changers', () => {
    describe('TOGGLE_SIDEBAR_STATE', () => {
      it('updates isSidebarCollapsed', () => {
        const updateSidebarAction = {
          type: 'TOGGLE_SIDEBAR_STATE',
          isSidebarCollapsed: true,
        };
        expect(reducer(defaultState, updateSidebarAction)).toEqual({
          ...defaultState,
          isSidebarCollapsed: true,
        });
      });
    });
    describe('SET_ACTIVE_PAGE', () => {
      it('updates pageName', () => {
        const updateSidebarAction = {
          type: 'SET_ACTIVE_PAGE',
          pageName: 'new Page',
        };
        expect(reducer(defaultState, updateSidebarAction)).toEqual({
          ...defaultState,
          pageName: 'new Page',
        });
      });
    });
  });
});
