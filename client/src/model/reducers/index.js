import { combineReducers } from 'redux';
import sidebar from './sidebar';
import entities from './entities';
import features from './features';

const dashBoardReducers = combineReducers({
  sidebar,
  entities,
  features,
});

export default dashBoardReducers;
