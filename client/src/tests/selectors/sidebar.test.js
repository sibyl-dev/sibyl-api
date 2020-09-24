import { getIsSidebarCollapsed, getPageName } from '../../model/selectors/sidebar';

const initialState = {
  sidebar: {
    isSidebarCollapsed: false,
    pageName: 'Score',
  },
};

const randomPageState = {
  sidebar: {
    isSidebarCollapsed: false,
    pageName: 'Random Page',
  },
};

describe('Sidebar Selectors', () => {
  describe('getIsSidebarCollapsed()', () => {
    it("returns the sidebar's collapsed state", () => {
      expect(getIsSidebarCollapsed(initialState)).toEqual(false);
    });
  });
  describe('getPageName()', () => {
    it("returns the sidebar's collapsed state", () => {
      expect(getPageName(randomPageState)).toEqual('Random Page');
    });
  });
});
