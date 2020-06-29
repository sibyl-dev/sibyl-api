import React, { Component } from 'react';
import { connect } from 'react-redux';
import { getIsSidebarCollapsed } from './model/selectors/sidebar';
import Sidebar from './components/Sidebar/Sidebar';
import Header from './components/Header/Header';
import Dashboard from './components/Dashboard/Dashboard';
import './assets/sass/main.scss';

class App extends Component {
  render() {
    const { isSidebarCollapsed } = this.props;
    const dashContainerClassNames = isSidebarCollapsed ? 'dash-container full-width' : 'dash-container';
    return (
      <div className="main-wrapper">
        <Sidebar />
        <div className={dashContainerClassNames}>
          <Header />
          <Dashboard />
        </div>
        <div className="clear"></div>
      </div>
    );
  }
}

export default connect((state) => ({
  isSidebarCollapsed: getIsSidebarCollapsed(state),
}))(App);
