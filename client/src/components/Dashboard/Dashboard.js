import React from 'react';
import { Switch, Route } from 'react-router-dom';
import Score from '../Score/Score';
import Details from '../Details/Details';
import './Dashboard.scss';
import Sandbox from '../Sandbox/Sandbox';
import NotFound from '../common/NotFound';
import Model from '../Model/Model';
import FeatureImportance from '../Model/FeatureImportance';
import GlobalFeatures from '../Model/GlobalFeatures';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <Switch>
        <Route path="/details" component={Details} />
        <Route path="/sandbox" exact component={Sandbox} />
        <Route path="/model" component={Model} />
        <Route path="/global-feature-importance" component={FeatureImportance} />
        <Route path="/feature-distribution" component={GlobalFeatures} />
        <Route path="/" exact component={Score} />
        <Route path="*" component={NotFound} />
      </Switch>
    </div>
  );
};

export default Dashboard;
