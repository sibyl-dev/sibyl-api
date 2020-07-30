import React, { Component } from 'react';
import { connect } from 'react-redux';
import { getIsSidebarCollapsed } from './model/selectors/sidebar';
import Sidebar from './components/Sidebar/Sidebar';
import Header from './components/Header/Header';
import Dashboard from './components/Dashboard/Dashboard';
import { setEntityIdAction, getEntityAction } from './model/actions/entities';
import { getCurrentEntityID } from './model/selectors/entities';
import './assets/sass/main.scss';

class App extends Component {
  componentDidMount() {
    this.getEntityDetails();
  }

  getEntityDetails() {
    let { currentEntityID } = this.props;
    const { location } = this.props;
    if (location.pathname.includes('entity')) {
      let entityID = this.props.location.pathname.split('/')[2];

      if (currentEntityID !== entityID) {
        this.props.setEntityID(entityID);
      }
    }

    this.props.getFeaturesList();
  }

  render() {
    const { isSidebarCollapsed, location } = this.props;
    const dashContainerClassNames = isSidebarCollapsed ? 'dash-container full-width' : 'dash-container';

    return (
      <div className="main-wrapper">
        <Sidebar />
        <div className={dashContainerClassNames}>
          <Header />
          <Dashboard location={location} />
        </div>
        <div className="clear" />
      </div>
    );
  }
}

export default connect(
  (state) => ({
    isSidebarCollapsed: getIsSidebarCollapsed(state),
    currentEntityID: getCurrentEntityID(state),
  }),
  (dispatch) => ({
    setEntityID: (entityID) => dispatch(setEntityIdAction(entityID)),
    getFeaturesList: () => dispatch(getEntityAction()),
  }),
)(App);
