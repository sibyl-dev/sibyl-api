import { combineReducers } from 'redux';
import sidebar from './sidebar';
import entities from './entities';
const dashBoardReducers = combineReducers({
  sidebar,
  entities,
});

export default dashBoardReducers;
