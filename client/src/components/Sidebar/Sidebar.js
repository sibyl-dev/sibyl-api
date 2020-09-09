import React, { Component } from 'react';
import Cookies from 'universal-cookie';
import { NavLink } from 'react-router-dom';
import { connect } from 'react-redux';
import { toggleSidebarStateAction, setActivePageAction } from '../../model/actions/sidebar';
import { getIsSidebarCollapsed } from '../../model/selectors/sidebar';
import {
  IndicatorIcon,
  // ScoreIcon,
  DetailsIcon,
  // SandboxIcon,
  // SimilarChildrenIcon,
  ModelIcon,
  MetLogo,
} from '../../assets/icons/icons';

import './Sidebar.scss';

class Sidebar extends Component {
  render() {
    const { toggleSidebarState, isSidebarCollapsed, setActivePage } = this.props;
    const sidebarClassNames = isSidebarCollapsed ? 'sidebar' : 'sidebar expanded';
    const cookies = new Cookies();
    const entityID = cookies.get('entityID') || 0;

    return (
      <div className={sidebarClassNames}>
        <div className="logo">
          <MetLogo state={!isSidebarCollapsed && `full`} />
        </div>

        <ul className="menu">
          <li onClick={() => toggleSidebarState(!isSidebarCollapsed)} className="sidebar-trigger">
            <IndicatorIcon dir={!isSidebarCollapsed && 'left'} />
          </li>
          {/* <li>
            <NavLink exact to="/" activeClassName="active" onClick={() => setActivePage('Score')}>
              <ScoreIcon />
              <span>Score</span>
            </NavLink>
          </li> */}
          <li>
            <NavLink exact to={`/entity/${entityID}`} activeClassName="active" onClick={() => setActivePage('Details')}>
              <DetailsIcon />
              <span>Details</span>
            </NavLink>
          </li>
          {/* <li>
            <NavLink exact to="/sandbox" onClick={() => setActivePage('Sandbox')}>
              <SandboxIcon />
              <span>Sandbox</span>
            </NavLink>
          </li> */}
          {/*
          Temporarily 'disabled'
          <li>
            <NavLink exact to="/similar-children" onClick={() => setActivePage('Similar Children')}>
              <SimilarChildrenIcon />
              <span>Similar Children</span>
            </NavLink>
          </li> */}
          <li className="model">
            <button type="button" className="clean about-model" onClick={() => toggleSidebarState(!isSidebarCollapsed)}>
              <ModelIcon />
              <span>About Model</span>
              <IndicatorIcon dir="right" />
            </button>
            {/* <ul>
              <li>
                <NavLink
                  exact
                  to="/global-feature-importance"
                  onClick={() => setActivePage('Global Feature Importance')}
                >
                  <span>Global Feature Importance</span>
                </NavLink>
              </li>
              <li>
                <NavLink exact to="/feature-distribution" onClick={() => setActivePage('Feature Distribution')}>
                  <span>Feature Distribution</span>
                </NavLink>
              </li>
            </ul> */}
          </li>
        </ul>
      </div>
    );
  }
}

export default connect(
  (state) => ({
    isSidebarCollapsed: getIsSidebarCollapsed(state),
  }),
  (dispatch) => ({
    toggleSidebarState: (sidebarState) => dispatch(toggleSidebarStateAction(sidebarState)),
    setActivePage: (pageName) => dispatch(setActivePageAction(pageName)),
  }),
)(Sidebar);
