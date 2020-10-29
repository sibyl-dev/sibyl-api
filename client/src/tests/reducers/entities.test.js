import reducer from '../../model/reducers/entities';
import { generateTestsForPromiseReducers, generateTestsForSetReducers } from '../helpers/reducers.helpers';

const defaultState = {
  isEntityDataLoading: true,
  isEntityContributionsLoading: true,
  isEntityDistributionsLoading: true,
  isEntityScoreLoading: true,
  isModelsLoading: true,
  entityScore: null,
  entityData: [],
  entityContributions: {},
  entityDistributions: {},
  entityID: null,
  userID: null,
  models: [],
  predictionScore: null,
  outcomeData: null,
  isOutcomeDataLoading: true,
};

const promiseReducers = [
  {
    name: 'GET_ENTITY_DATA',
    loading: 'isEntityDataLoading',
    key: 'entityData',
    sendData: { result: [1, 2] },
    testData: [1, 2],
    failData: [],
  },
  {
    name: 'GET_MODELS',
    loading: 'isModelsLoading',
    key: 'models',
    sendData: { result: { models: [3, 2] } },
    testData: [3, 2],
    failData: [],
  },
  {
    name: 'GET_ENTITY_CONTRIBUTIONS',
    loading: 'isEntityContributionsLoading',
    key: 'entityContributions',
    sendData: { entityContributions: [3, 2] },
    testData: [3, 2],
    failData: {},
  },
  {
    name: 'GET_ENTITY_SCORE',
    loading: 'isEntityScoreLoading',
    key: 'entityScore',
    sendData: { result: { output: 5 } },
    testData: 5,
    failData: null,
  },
  {
    name: 'GET_ENTITY_DISTRIBUTIONS',
    loading: 'isEntityDistributionsLoading',
    key: 'entityDistributions',
    sendData: { entityDistributions: 'test' },
    testData: 'test',
    failData: {},
  },
  {
    name: 'GET_OUTCOME_COUNT',
    loading: 'isOutcomeDataLoading',
    key: 'outcomeData',
    sendData: { outcomeData: { distributions: [1, 2] } },
    testData: [1, 2],
    failData: null,
  },
];

const setReducers = [
  {
    name: 'SET_USER_ID',
    description: 'updates the user id',
    key: 'userID',
    sendData: 'test123',
    testData: 'test123',
  },
  {
    name: 'SET_ENTITY_ID',
    description: 'updates the entity id',
    key: 'entityID',
    sendData: 'test123',
    testData: 'test123',
  },
  {
    name: 'SET_PREDICTION_SCORE',
    description: 'updates the prediction score',
    key: 'predictionScore',
    sendData: 'test123',
    testData: 'test123',
  },
];

describe('Entities Reducer', () => {
  it('returns initial state', () => {
    expect(reducer(undefined, {})).toEqual(defaultState);
  });

  generateTestsForSetReducers(reducer, defaultState, setReducers);

  generateTestsForPromiseReducers(reducer, defaultState, promiseReducers);
});
