import React, { Component } from 'react';
import { connect } from 'react-redux';
import { getIsSidebarCollapsed } from './model/selectors/sidebar';
import Sidebar from './components/Sidebar/Sidebar';
import Header from './components/Header/Header';
import Dashboard from './components/Dashboard/Dashboard';
import { setEntityIdAction, getEntityAction, setUserIdAction, getModelIDAction } from './model/actions/entities';
import { getCurrentEntityID, getCurrentUserID } from './model/selectors/entities';
import './assets/sass/main.scss';

class App extends Component {
  componentDidMount() {
    this.getEntityDetails();
  }

  getEntityDetails() {
    const { currentEntityID, setUserID, currentUserID, setEntityID, loadModelID, getFeaturesList } = this.props;
    const { location } = this.props;

    if (location.search.includes('user_id')) {
      const userID = location.search.split('=')[1];
      if (currentUserID !== userID) {
        setUserID(userID);
      }
    }

    if (location.pathname.includes('entity')) {
      const entityID = this.props.location.pathname.split('/')[2];

      if (currentEntityID !== entityID) {
        setEntityID(entityID)
          .then(() => loadModelID())
          .then(() => getFeaturesList());

        return;
      }
    }

    loadModelID().then(() => getFeaturesList());
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
    currentUserID: getCurrentUserID(state),
  }),
  (dispatch) => ({
    setEntityID: (entityID) => dispatch(setEntityIdAction(entityID)),
    setUserID: (userID) => dispatch(setUserIdAction(userID)),
    loadModelID: (modelID) => dispatch(getModelIDAction(modelID)),
    getFeaturesList: () => dispatch(getEntityAction()),
  }),
)(App);
