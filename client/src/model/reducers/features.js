import createReducer from '../store/createReducer';
const initialState = {
  isFeaturesLoading: true,
  featuresData: [],
  isCategoriesLoading: true,
  categories: [],
  featuresImportances: {},
  newFeatureScore: null,
  isModelPredictionLoading: true,
  currendModelPredition: [],
  reversedModelPrediction: [],
  filterCriteria: '',
  sortContribDir: 'asc',
  currentFilterValue: 'all',
  filterValue: 'all',
  filterCategs: null,
  contribFilters: 'all',
};

function GET_FEATURES_DATA_REQUEST(nextState) {
  nextState.isFeaturesLoading = true;
}

function GET_FEATURES_DATA_SUCCESS(nextState, action) {
  nextState.featuresData = action.result.features;
  nextState.isFeaturesLoading = false;
}

function GET_FEATURES_DATA_FAILURE(nextState) {
  nextState.featuresData = [];
  nextState.isFeaturesLoading = false;
}

// ------------------
function GET_CATEGORIES_REQUEST(nextState) {
  nextState.isCategoriesLoading = true;
}

function GET_CATEGORIES_SUCCESS(nextState, action) {
  nextState.isCategoriesLoading = false;
  nextState.categories = action.result.categories;
}

function GET_CATEGORIES_FAILURE(nextState) {
  nextState.isCategoriesLoading = false;
  nextState.categories = [];
}

// ------------------
function GET_FEATURES_IMPORTANCES_SUCCESS(nextState, action) {
  nextState.featuresImportances = action.result.importances;
}

// ------------------
function UPDATE_FEATURE_PREDICTION_SUCCESS(nextState, { newFeatureScore }) {
  nextState.newFeatureScore = newFeatureScore;
}

// ------------------
function GET_MODEL_PREDICTION_REQUEST(nextState) {
  nextState.isModelPredictionLoading = true;
}

function GET_MODEL_PREDICTION_SUCCESS(nextState, { currentPrediction, reversedPrediction }) {
  nextState.currendModelPredition = currentPrediction;
  nextState.reversedModelPrediction = reversedPrediction;
  nextState.isModelPredictionLoading = false;
}

function GET_MODEL_PREDICTION_FAILURE(nextState) {
  nextState.isModelPredictionLoading = false;
  nextState.currendModelPredition = [];
  nextState.reversedModelPrediction = [];
}

// ------------------
// when entering search string within the search field (filter by feature name)
function SET_FILTER_CRITERIA(nextState, { filterCriteria }) {
  nextState.filterCriteria = filterCriteria;
}

// ------------------
function SET_FEATURE_CONTRIB_SORT_DIRECTION(nextState, { sortContribDir }) {
  nextState.sortContribDir = sortContribDir;
}

// ------------------
// when selecting a filter value from dropdown (filter by feature type: numeric, binary)
function SET_FILTER_VALUE(nextState, { filterValue }) {
  nextState.filterValue = filterValue;
}

// ------------------
function SET_FILTER_CATEGS(nextState, { filterCategs }) {
  nextState.filterCategs = filterCategs;
}

// ------------------
function SET_CONTRIB_FILTERS(nextState, { contribFilters }) {
  nextState.contribFilters = contribFilters;
}

export default createReducer(initialState, {
  GET_FEATURES_DATA_REQUEST,
  GET_FEATURES_DATA_SUCCESS,
  GET_FEATURES_DATA_FAILURE,
  GET_CATEGORIES_REQUEST,
  GET_CATEGORIES_SUCCESS,
  GET_CATEGORIES_FAILURE,
  GET_FEATURES_IMPORTANCES_SUCCESS,
  UPDATE_FEATURE_PREDICTION_SUCCESS,
  GET_MODEL_PREDICTION_REQUEST,
  GET_MODEL_PREDICTION_SUCCESS,
  GET_MODEL_PREDICTION_FAILURE,
  SET_FILTER_CRITERIA,
  SET_FEATURE_CONTRIB_SORT_DIRECTION,
  SET_FILTER_VALUE,
  SET_FILTER_CATEGS,
  SET_CONTRIB_FILTERS,
});
