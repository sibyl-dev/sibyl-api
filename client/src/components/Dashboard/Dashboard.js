import React from 'react';
import { Switch, Route } from 'react-router-dom';
import Score from '../Score/Score';
import Details from '../Details/Details';
import './Dashboard.scss';
import Sandbox from '../Sandbox/Sandbox';
import NotFound from '../common/NotFound';
import Model from '../Model/Model';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <Switch>
        <Route path="/details" component={Details} />
        <Route path="/sandbox" exact component={Sandbox} />
        <Route path="/model" component={Model} />
        <Route path="/" exact component={Score} />
        <Route path="*" component={NotFound} />
      </Switch>
    </div>
  );
};

export default Dashboard;
