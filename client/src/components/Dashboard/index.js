import React from 'react';
import { Switch, Route } from 'react-router-dom';
import Score from '../Score/Score';
import Details from '../Details/Details';
import './Dashboard.scss';

const NotFound = () => {
  return <p>Not found</p>;
};

const Dashboard = () => {
  return (
    <div className="dashboard">
      <Switch>
        <Route path="/details" component={Details} />
        <Route path="/" exact component={Score} />
        <Route path="*" component={NotFound} />
      </Switch>
    </div>
  );
};

export default Dashboard;
