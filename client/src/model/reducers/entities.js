import createReducer from '../store/createReducer';

const initialState = {
  isEntityDataLoading: true,
  isEntityContributionsLoading: true,
  isEntityDistributionsLoading: true,
  isEntityScoreLoading: true,
  entityScore: null,
  entityData: [],
  entityContributions: {},
  entityDistributions: {},
  entityID: null,
  userID: null,
  predictionScore: null,
  outcomeData: null,
  isOutcomeDataLoading: true,
};

function GET_ENTITY_DATA_REQUEST(nextState) {
  nextState.isEntityDataLoading = true;
}
function GET_ENTITY_DATA_SUCCESS(nextState, action) {
  nextState.entityData = action.result;
  nextState.isEntityDataLoading = false;
}

function GET_ENTITY_DATA_FAILURE(nextState) {
  nextState.entityData = [];
  nextState.isEntityDataLoading = false;
}

// -------
function SET_USER_ID(nextState, { userID }) {
  nextState.userID = userID;
}

// -------
function SET_ENTITY_ID(nextState, { entityID }) {
  nextState.entityID = entityID;
}

// -------
function GET_ENTITY_CONTRIBUTIONS_REQUEST(nextState) {
  nextState.isEntityContributionsLoading = true;
}

function GET_ENTITY_CONTRIBUTIONS_SUCCESS(nextState, action) {
  nextState.entityContributions = action.entityContributions;
  nextState.isEntityContributionsLoading = false;
}

function GET_ENTITY_CONTRIBUTIONS_FAILURE(nextState) {
  nextState.isEntityContributionsLoading = false;
  nextState.entityContributions = {};
}

// -------
function GET_ENTITY_SCORE_REQUEST(nextState) {
  nextState.isEntityScoreLoading = true;
}

function GET_ENTITY_SCORE_SUCCESS(nextState, action) {
  nextState.isEntityScoreLoading = false;
  nextState.entityScore = action.result.output;
}

function GET_ENTITY_SCORE_FAILURE(nextState) {
  nextState.isEntityContributionsLoading = false;
  nextState.entityScore = null;
}

// -------
function GET_ENTITY_DISTRIBUTIONS_REQUEST(nextState) {
  nextState.isEntityDistributionsLoading = true;
}

function GET_ENTITY_DISTRIBUTIONS_SUCCESS(nextState, { entityDistributions }) {
  nextState.entityDistributions = entityDistributions;
  nextState.isEntityDistributionsLoading = false;
}

function GET_ENTITY_DISTRIBUTIONS_FAILURE(nextState) {
  nextState.isEntityDistributionsLoading = false;
}

// -------
function SET_PREDICTION_SCORE(nextState, { predictionScore }) {
  nextState.predictionScore = predictionScore;
}

// ------------------
function GET_OUTCOME_COUNT_REQUEST(nextState) {
  nextState.isOutcomeDataLoading = true;
}

// ------------------
function GET_OUTCOME_COUNT_SUCCESS(nextState, { outcomeData }) {
  nextState.outcomeData = outcomeData.distributions;
  nextState.isOutcomeDataLoading = false;
}

export default createReducer(initialState, {
  GET_ENTITY_DATA_REQUEST,
  GET_ENTITY_DATA_SUCCESS,
  GET_ENTITY_DATA_FAILURE,
  SET_ENTITY_ID,
  GET_ENTITY_CONTRIBUTIONS_REQUEST,
  GET_ENTITY_CONTRIBUTIONS_SUCCESS,
  GET_ENTITY_CONTRIBUTIONS_FAILURE,
  GET_ENTITY_SCORE_REQUEST,
  GET_ENTITY_SCORE_SUCCESS,
  GET_ENTITY_SCORE_FAILURE,
  GET_ENTITY_DISTRIBUTIONS_REQUEST,
  GET_ENTITY_DISTRIBUTIONS_SUCCESS,
  GET_ENTITY_DISTRIBUTIONS_FAILURE,
  SET_PREDICTION_SCORE,
  GET_OUTCOME_COUNT_REQUEST,
  GET_OUTCOME_COUNT_SUCCESS,
  SET_USER_ID,
});
