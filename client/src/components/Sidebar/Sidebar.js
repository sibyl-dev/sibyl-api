import React, { Component } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { connect } from 'react-redux';
import { toggleSidebarStateAction, setActivePageAction } from '../../model/actions/sidebar';
import { getIsSidebarCollapsed } from '../../model/selectors/sidebar';
import {
  IndicatorIcon,
  ScoreIcon,
  DetailsIcon,
  SandboxIcon,
  SimilarChildrenIcon,
  ModelIcon,
  MetLogo,
} from '../../assets/icons/icons';
import './Sidebar.scss';

class Sidebar extends Component {
  render() {
    const { toggleSidebarState, isSidebarCollapsed, setActivePage } = this.props;

    return (
      <div className={`sidebar ${!isSidebarCollapsed && `expanded`}`}>
        <div className="logo">
          <MetLogo state={!isSidebarCollapsed && `full`} />
        </div>
        <ul className="menu">
          <li onClick={() => toggleSidebarState(!isSidebarCollapsed)}>
            <IndicatorIcon dir={!isSidebarCollapsed && 'left'} />
          </li>
          <li>
            <NavLink exact to="/" activeClassName="active" onClick={() => setActivePage('Score')}>
              <ScoreIcon />
              <span>Score</span>
            </NavLink>
          </li>
          <li>
            <NavLink exact to="/details" activeClassName="active" onClick={() => setActivePage('Details')}>
              <DetailsIcon />
              <span>Details</span>
            </NavLink>
          </li>
          <li>
            <NavLink exact to="/sandbox" onClick={() => setActivePage('Sandbox')}>
              <SandboxIcon />
              <span>Sandbox</span>
            </NavLink>
          </li>
          <li>
            <NavLink exact to="/similar-children" onClick={() => setActivePage('Similar Children')}>
              <SimilarChildrenIcon />
              <span>Similar Children</span>
            </NavLink>
          </li>
          <li>
            <NavLink exact to="/model" onClick={() => setActivePage('Model')}>
              <ModelIcon />
              <span>About Model</span>
            </NavLink>
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
