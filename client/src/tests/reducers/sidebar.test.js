import reducer from '../../model/reducers/sidebar';
import { generateTestsForSetReducers } from '../helpers/reducers.helpers';

const defaultState = {
  isSidebarCollapsed: false,
  pageName: 'Score',
};

describe('Sidebar Reducer', () => {
  it('returns initial state', () => {
    expect(reducer(undefined, {})).toEqual(defaultState);
  });

  describe('Sidebar Changers', () => {
    generateTestsForSetReducers(reducer, defaultState, [
      {
        name: 'TOGGLE_SIDEBAR_STATE',
        description: 'updates isSidebarCollapsed',
        key: 'isSidebarCollapsed',
        sendData: true,
        testData: true,
      },
      {
        name: 'SET_ACTIVE_PAGE',
        description: 'updates pageName',
        key: 'pageName',
        sendData: 'new Page',
        testData: 'new Page',
      },
    ]);
  });
});
