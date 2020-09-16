import { api } from '../api/api';
import { getCurrentEntityID, getSelectedModelID } from '../selectors/entities';
import { getModelPredictionPayload } from '../selectors/features';
import { setUserActionRecording } from './userActions';

export function getCategoriesAction() {
  return function (dispatch) {
    const action = {
      type: 'GET_CATEGORIES',
      promise: api.get('/categories/'),
    };
    dispatch(action);
  };
}

export function getFeaturesImportanceAction() {
  return function (dispatch, getState) {
    const modelID = getSelectedModelID(getState());
    const action = {
      type: 'GET_FEATURES_IMPORTANCES',
      promise: api.get(`/importance/?model_id=${modelID}`),
    };
    dispatch(action);
  };
}

export function getFeaturesAction() {
  return function (dispatch) {
    const action = {
      type: 'GET_FEATURES_DATA',
      promise: api.get('/features/'),
    };

    dispatch(action)
      .then(dispatch(getFeaturesImportanceAction()))
      .then(() => dispatch(getModelPredictionAction()));
  };
}

export function updateFeaturePredictionScore(featuresData) {
  return function (dispatch, getState) {
    const state = getState();
    const entityID = getCurrentEntityID(state);
    const modelID = getSelectedModelID(state);

    const payLoad = {
      eid: entityID,
      model_id: modelID,
      changes: featuresData,
    };

    api
      .post('/modified_prediction/', payLoad)
      .then((response) => response.json())
      .then((score) => dispatch({ type: 'UPDATE_FEATURE_PREDICTION_SUCCESS', newFeatureScore: score.prediction }));

    let actionString = JSON.stringify(featuresData).replaceAll(',', ';');

    const userRecordPayload = {
      element: 'experiment_with_changes',
      action: 'text',
      details: actionString,
    };
    dispatch(setUserActionRecording(userRecordPayload));
  };
}

export function getModelPredictionAction() {
  return function (dispatch, getState) {
    const state = getState();
    const entityID = getCurrentEntityID(state);
    const modelID = getSelectedModelID(state);

    const { currentFeatures, reversedFeatures } = getModelPredictionPayload(getState());
    const currentPredictionPayload = {
      eid: entityID,
      model_id: modelID,
      changes: currentFeatures,
    };

    const reversePredictionPayload = {
      eid: entityID,
      model_id: modelID,
      changes: reversedFeatures,
    };
    dispatch({ type: 'GET_MODEL_PREDICTION_REQUEST' });

    api
      .post('/single_change_predictions/', currentPredictionPayload)
      .then((res) => res.json())
      .then((prediction) => {
        api
          .post('/single_change_predictions/', reversePredictionPayload)
          .then((response) => response.json())
          .then((reversePredict) => {
            dispatch({
              type: 'GET_MODEL_PREDICTION_SUCCESS',
              currentPrediction: prediction.changes,
              reversedPrediction: reversePredict.changes,
            });
          });
      })
      .catch((error) => dispatch({ type: 'GET_MODEL_PREDICTION_FAILURE', error }));
  };
}

export function setFilterCriteriaAction(filterValue) {
  return function (dispatch) {
    dispatch({ type: 'SET_FILTER_CRITERIA', filterCriteria: filterValue });
    const userRecordPayload = {
      element: 'details_search_bar',
      action: 'type',
      details: filterValue,
    };
    dispatch(setUserActionRecording(userRecordPayload));
  };
}

export function sortFeaturesByContribAction(direction) {
  return function (dispatch) {
    dispatch({ type: 'SET_FEATURE_CONTRIB_SORT_DIRECTION', sortContribDir: direction });

    const userRecordPayload = {
      element: direction === 'asc' ? 'details_contrib_sorted_ascending' : 'details_contrib_sorted_descending',
      action: 'click',
    };
    dispatch(setUserActionRecording(userRecordPayload));
  };
}

export function setFilterValuesAction(filterValue) {
  return function (dispatch) {
    dispatch({ type: 'SET_FILTER_VALUE', filterValue });
  };
}

export function setFilterCategsAction(categs) {
  return function (dispatch) {
    const filterCategs = categs !== null ? categs.map((currentCateg) => currentCateg.value) : null;
    dispatch({ type: 'SET_FILTER_CATEGS', filterCategs });
    const updatedFiltes = JSON.stringify(filterCategs).replaceAll(',', ';');

    const userRecordPayload = {
      element: 'category_filter',
      action: 'filter',
      details: updatedFiltes,
    };
    dispatch(setUserActionRecording(userRecordPayload));
  };
}

export function setContribFiltersAction(contribFilters) {
  return function (dispatch) {
    dispatch({ type: 'SET_CONTRIB_FILTERS', contribFilters });
  };
}

export function setSortPredDirection(direction) {
  return function (dispatch) {
    dispatch({ type: 'SET_SORT_DIFF_DIR', sortDiffDirection: null }).then(() =>
      dispatch({ type: 'SET_SORT_PRED_DIR', sortPredDirection: direction }),
    );
    const userRecordPayload = {
      element: direction === 'asc' ? 'sandbox_pred_sorted_ascending' : 'sandbox_pred_sorted_descending',
      action: 'click',
    };
    dispatch(setUserActionRecording(userRecordPayload));
  };
}

export function setSortDiffDirectionAction(direction) {
  return function (dispatch) {
    dispatch({ type: 'SET_SORT_PRED_DIR', sortPredDirection: null }).then(() =>
      dispatch({ type: 'SET_SORT_DIFF_DIR', sortDiffDirection: direction }),
    );
    const userRecordPayload = {
      element: direction === 'asc' ? 'sandbox_diff_sorted_ascending' : 'sandbox_diff_sorted_descending',
      action: 'click',
    };
    dispatch(setUserActionRecording(userRecordPayload));
  };
}

export function setModelPredictFilterValueAction(value) {
  return function (dispatch) {
    dispatch({ type: 'SET_MODEL_PRED_FILTER_VALUE', modelPredFilterValue: value });
  };
}

export function setModelPredDiffFilterAction(filterValue) {
  return function (dispatch) {
    dispatch({ type: 'SET_MODEL_PRED_DIFF_FILTER', diffFilterVal: filterValue });
  };
}

export function setFeatureTypeFilterAction(featureType, filters) {
  return function (dispatch) {
    dispatch({ type: 'SET_FEATURE_TYPE_FILTERS', featureFilters: { featureType, filters } });
  };
}

export function setFeatureTypeSortContribDirAction(featureType, direction) {
  return function (dispatch) {
    dispatch({ type: 'SET_FEATURE_TYPE_SORT_CONTRIB_DIR', featureSortDir: { featureType, direction } });
    const userRecordPayload = {
      element: direction === 'asc' ? 'details_contrib_sorted_ascending' : 'details_contrib_sorted_descending',
      action: 'click',
    };
    dispatch(setUserActionRecording(userRecordPayload));
  };
}

export function setFeatureTypeFilterCategsAction(featureType, categs) {
  return function (dispatch) {
    const filterCategs = categs !== null ? categs.map((currentCateg) => currentCateg.value) : null;
    dispatch({ type: 'SET_FEATURE_TYPE_FILTER_CATEGS', featureTypeFilterCategs: { featureType, filterCategs } });
    const userRecordPayload = {
      element: 'category_filter',
      action: 'filter',
      details: filterCategs,
    };
    dispatch(setUserActionRecording(userRecordPayload));
  };
}

export function setFeatureImpSortDirAction(direction) {
  return function (dispatch) {
    const action = {
      type: 'SET_FEATURE_IMPORTANCE_SORT_DIR',
      sortDir: direction,
    };

    dispatch(action);
  };
}
