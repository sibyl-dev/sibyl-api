import React from 'react';
import { Switch, Route } from 'react-router-dom';
// import Score from '../Score/Score';
import Details from '../Details/Details';
import './Dashboard.scss';
import Sandbox from '../Sandbox/Sandbox';
import NotFound from '../common/NotFound';
import Model from '../Model/Model';
import FeatureImportance from '../Model/FeatureImportance';
import FeatureDistribution from '../Model/FeatureDistribution';

const Dashboard = (props) => {
  const { location } = props;

  return (
    <div className="dashboard">
      <Switch location={location}>
        <Route path="/entity/:id" component={Details} />
        <Route path="/sandbox" exact component={Sandbox} />
        <Route path="/model" component={Model} />
        <Route path="/global-feature-importance" component={FeatureImportance} />
        <Route path="/feature-distribution" component={FeatureDistribution} />
        {/* <Route path="/" exact component={Score} /> */}
        <Route path="*" component={NotFound} />
      </Switch>
    </div>
  );
};

export default Dashboard;
