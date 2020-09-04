import json
import logging
import os

import pandas as pd
from flask import request
from flask_restful import Resource

from sibyl.sibyl import global_explanation as ge
from sibyl.sibyl import local_feature_explanation as lfe
from sibylapp import g
from sibylapp.db import schema
from sibylapp.resources import helpers

LOGGER = logging.getLogger(__name__)


class Similarities(Resource):
    def get(self):
        """
        @api {get} /similar_entities/ Get similar entities
        @apiName GetSimilarities
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription Get a list of similar entities.

        @apiParam {String} eid ID of the entity.
        @apiParam {Number} number Number of similar entities to search for.

        @apiSuccess {String[]} entities List of entity IDs.
        """


class SingleChangePredictions(Resource):
    def post(self):
        """
        @api {post} /single_change_predictions/ Post single prediction
        @apiName PostSinglePrediction
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription Get the list of updated predictions after making
        single changes.

        @apiParam {String} eid ID of entity to predict on.
        @apiParam {String} model_id ID of model to use for predictions.
        @apiParam {2-Tuple[]} changes List of features to change and
            their new values.
        @apiParam {String} changes.item1 Name of the feature to change.
        @apiParam {String} changes.item2 Changed Value of the feature.

        @apiSuccess {2-Tuple[]} changes List of features to change and
            their new values.
        @apiSuccess {String} changes.item1 Name of the feature to change.
        @apiSuccess {String} changes.item2 New prediction of the feature.
        """
        attrs = ['eid', 'model_id', 'changes']
        d = {}
        body = request.json
        for attr in attrs:
            d[attr] = None
            if body is not None:
                d[attr] = body.get(attr)
            else:
                if attr in request.form:
                    d[attr] = request.form[attr]
        # validate data type
        try:
            d['eid'] = str(d['eid'])
            d['model_id'] = str(d['model_id'])
            for change in d['changes']:
                change[0] = str(change[0])
                change[1] = float(change[1])
                if schema.Feature.find_one(name=change[0]) is None:
                    LOGGER.exception('Invalid feature %s' % change[0])
                    return {'message': 'Invalid feature {}'.format(change[0])
                            }, 400
                if schema.Feature.find_one(
                        name=change[0]).type == "binary" and change[1] not in [0, 1]:
                    LOGGER.exception('Feature %s is binary, change value of %s is invalid.'
                                     % (change[0], change[1]))
                    return {'message': 'Feature {} is binary, invalid change value'.format(
                            change[0])}, 400
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 400

        eid = d["eid"]
        model_id = d["model_id"]
        changes = d["changes"]
        entity = schema.Entity.find_one(eid=eid)
        if entity is None:
            LOGGER.exception('Error getting entity. Entity %s does not exist.', eid)
            return {'message': 'Entity {} does not exist'.format(eid)}, 400
        entity_features = pd.DataFrame(entity.features, index=[0])

        success, payload = helpers.load_model(model_id)
        if success:
            model, transformer = payload
        else:
            message, error_code = payload
            return message, error_code
        entity_features = transformer.transform(entity_features)

        predictions = []
        for change in changes:
            feature = change[0]
            value = change[1]
            modified = entity_features.copy()
            modified[feature] = value
            prediction = model.predict(modified)[0].tolist()
            predictions.append([feature, prediction])
        return {"changes": predictions}


class ModifiedPrediction(Resource):
    def post(self):
        """
        @api {post} /modified_prediction/ Post multiple prediction
        @apiName PostMultiplePrediction
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription  Get the modified prediction under different conditions

        @apiParam {String} eid ID of entity to predict on.
        @apiParam {String} model_id ID of model to use for predictions.
        @apiParam {2-Tuple[]} changes List of features to change and
            their new values.
        @apiParam {String} changes.item1 Name of the feature to change.
        @apiParam {String} changes.item2 Changed Value of the feature.

        @apiSuccess {Number} prediction New prediction after making
            the requested changes.
        """
        attrs = ['eid', 'model_id', 'changes']
        d = {}
        body = request.json
        for attr in attrs:
            d[attr] = None
            if body is not None:
                d[attr] = body.get(attr)
            else:
                if attr in request.form:
                    d[attr] = request.form[attr]
        # validate data type
        try:
            d['eid'] = str(d['eid'])
            d['model_id'] = str(d['model_id'])
            for change in d['changes']:
                change[0] = str(change[0])
                change[1] = float(change[1])
                if schema.Feature.find_one(name=change[0]) is None:
                    LOGGER.exception('Invalid feature %s' % change[0])
                    return {'message': 'Invalid feature {}'.format(change[0])
                            }, 400
                if schema.Feature.find_one(
                        name=change[0]).type == "binary" and change[1] not in [0, 1]:
                    LOGGER.exception('Feature %s is binary, change value of %s is invalid.'
                                     % (change[0], change[1]))
                    return {'message': 'Feature {} is binary, invalid change value'.format(
                        change[0])}, 400
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 400

        eid = d["eid"]
        model_id = d["model_id"]
        changes = d["changes"]
        entity = schema.Entity.find_one(eid=eid)
        if entity is None:
            LOGGER.exception('Error getting entity. Entity %s does not exist.', eid)
            return {'message': 'Entity {} does not exist'.format(eid)}, 400
        entity_features = pd.DataFrame(entity.features, index=[0])

        success, payload = helpers.load_model(model_id)
        if success:
            model, transformer = payload
        else:
            message, error_code = payload
            return message, error_code

        entity_features = transformer.transform(entity_features)

        modified = entity_features.copy()
        for change in changes:
            feature = change[0]
            value = change[1]
            modified[feature] = value
        prediction = model.predict(modified)[0].tolist()
        return {"prediction": prediction}


class FeatureDistributions(Resource):
    def post(self):
        """
        @api {post} /feature_distributions/ Get feature distributions
        @apiName PostFeatureDistributions
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription Get the distributions of all features

        @apiParam {Number} prediction Prediction Prediction to look at distributions for.
        @apiParam {String} model_id ID of model to use for predictions.

        @apiSuccess {Object} distributions Information about the distributions of each
            feature for each feature.
        @apiSuccess {String} distributions.key Feature name
        @apiSuccess {String="numeric","categorical"} distributions.type Feature type
        @apiSuccess {5-tuple} distributions.metrics If type is "numeric":[min, 1st quartile,
            median, 3rd quartile, max] <br>. If type is "categorical":
            [[values],[counts]]
        """
        # LOAD IN PARAMETERS
        attrs = ['prediction', 'model_id']
        attrs_type = [int, str]
        d = dict()
        body = request.json
        for attr in attrs:
            d[attr] = None
            if body is not None:
                d[attr] = body.get(attr)
            else:
                if attr in request.form:
                    d[attr] = request.form[attr]

        # VALIDATE DATA TYPES
        try:
            for i, attr in enumerate(attrs):
                d[attr] = attrs_type[i](d[attr])
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 400

        prediction = d["prediction"]
        model_id = d["model_id"]

        # CHECK FOR PRECOMPUTED VALUES
        distribution_filepath = g['config']['feature_distribution_location']
        if distribution_filepath is not None:
            distribution_filepath = os.path.normpath(distribution_filepath)
            with open(distribution_filepath, 'r') as f:
                all_distributions = json.load(f)
            return {"distributions": all_distributions[str(prediction)]['distributions']}

        # LOAD IN AND VALIDATE MODEL DATA
        success, payload = helpers.load_model(model_id, include_dataset=True)
        if success:
            model, transformer, dataset = payload
        else:
            message, error_code = payload
            return message, error_code

        # LOAD IN FEATURES
        feature_docs = schema.Feature.find()
        features = [{"name": feature_doc.name, "type": feature_doc.type}
                    for feature_doc in feature_docs]
        features = pd.DataFrame(features)

        # FIND CATEGORICAL FEATURES
        boolean_features = features[
            features['type'].isin(['binary', 'categorical'])]["name"]
        categorical_dataset = dataset[boolean_features]

        numeric_features = features[
            features['type'] == 'numeric']["name"]
        numeric_dataset = dataset[numeric_features]

        distributions = {}
        rows = ge.get_rows_by_output(prediction, model.predict, dataset,
                                     row_labels=None, transformer=transformer)
        if len(rows) == 0:
            LOGGER.exception('No data with that prediction: %s', prediction)
            return {'message': 'No data with that prediction: {}'.format(prediction)}, 400

        cat_summary = ge.summary_categorical(categorical_dataset.iloc[rows])
        num_summary = ge.summary_numeric(numeric_dataset.iloc[rows])

        for (i, name) in enumerate(boolean_features):
            distributions[name] = {"type": "categorical",
                                   "metrics": [cat_summary[0][i].tolist(),
                                               cat_summary[1][i].tolist()]}
        for (i, name) in enumerate(numeric_features):
            distributions[name] = {"type": "numeric",
                                   "metrics": num_summary[i]}

        return {"distributions": distributions}


class PredictionCount(Resource):
    def post(self):
        """
        @api {post} /prediction_count/ Get prediction count
        @apiName PostPredictionCount
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription Get the number of entities that were predicted as a certain value

        @apiParam {Number} prediction Prediction to look at counts for
        @apiParam {String} model_id ID of model to use for predictions.

        @apiSuccess {Number} count Number of entities who are predicted as prediction in
            the training set
        """
        attrs = ['prediction', 'model_id']
        attrs_type = [int, str]
        d = dict()
        body = request.json
        for attr in attrs:
            d[attr] = None
            if body is not None:
                d[attr] = body.get(attr)
            else:
                if attr in request.form:
                    d[attr] = request.form[attr]

        # validate data type
        try:
            for i, attr in enumerate(attrs):
                d[attr] = attrs_type[i](d[attr])
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 400

        prediction = d["prediction"]
        model_id = d["model_id"]

        distribution_filepath = g['config']['feature_distribution_location']
        if distribution_filepath is not None:
            distribution_filepath = os.path.normpath(distribution_filepath)
            with open(distribution_filepath, 'r') as f:
                all_distributions = json.load(f)
            return {"count:":
                    all_distributions[str(prediction)]["total cases"]}

        # LOAD IN AND VALIDATE MODEL DATA
        success, payload = helpers.load_model(model_id, include_dataset=True)
        if success:
            model, transformer, dataset = payload
        else:
            message, error_code = payload
            return message, error_code

        rows = ge.get_rows_by_output(prediction, model.predict, dataset,
                                     row_labels=None, transformer=transformer)

        count = len(rows)

        return {"count": count}


class OutcomeCount(Resource):
    def post(self):
        """
        @api {post} /outcome_count/ Get outcome count
        @apiName PostOutcomeCount
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription Get the distributions of entity outcomes
                        that were predicted as a certain value

        @apiParam {Number} prediction Prediction Prediction to look at counts for
        @apiParam {String} model_id ID of model to use for predictions.

        @apiSuccess {Object} distributions Information about the distributions of each
                                           outcome.
        @apiSuccess {String} distributions.key Outcome name
        @apiSuccess {String="numeric","category"} distributions.type Outcome type
        @apiSuccess {5-tuple} distributions.metrics If type is "numeric":
                                                        [min, 1st quartile, median,
                                                        3rd quartile, max] <br>
                                                    If type is "categorical" or "binary":
                                                        [[values],[counts]]
        """
        attrs = ['prediction', 'model_id']
        attrs_type = [int, str]
        d = dict()
        body = request.json
        for attr in attrs:
            d[attr] = None
            if body is not None:
                d[attr] = body.get(attr)
            else:
                if attr in request.form:
                    d[attr] = request.form[attr]

        # validate data type
        try:
            for i, attr in enumerate(attrs):
                d[attr] = attrs_type[i](d[attr])
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 400

        prediction = d["prediction"]

        distribution_filepath = g['config']['feature_distribution_location']
        if distribution_filepath is not None:
            distribution_filepath = os.path.normpath(distribution_filepath)
            with open(distribution_filepath, 'r') as f:
                all_distributions = json.load(f)
            outcome_metrics = all_distributions[
                str(prediction)]["distributions"]["PRO_PLSM_NEXT730_DUMMY"]
            return {"distributions": {"PRO_PLSM_NEXT730_DUMMY": outcome_metrics}}
        else:
            LOGGER.exception("Not implemented - Please provide precomputed document")
            return {'message': "Not implemented - Please provide precomputed document"}, 501


class FeatureContributions(Resource):
    def post(self):
        """
        @api {post} /contributions/ Get feature contributions
        @apiName GetFeatureContributions
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription  get the contributions of all features

        @apiParam {String} eid ID of the entity to compute.
        @apiParam {String} model_id ID of the model to compute.

        @apiSuccess {Object} contributions Feature contribution object (key-value pair).
        @apiSuccess {Number} contributions.[key] Contribution value of the feature [key].
        """

        # LOAD IN AND CHECK ATTRIBUTES:
        attrs = ['eid', 'model_id']
        attrs_type = [str, str]
        d = dict()
        body = request.json
        for attr in attrs:
            d[attr] = None
            if body is not None:
                d[attr] = body.get(attr)
            else:
                if attr in request.form:
                    d[attr] = request.form[attr]

        # validate data type
        try:
            for i, attr in enumerate(attrs):
                d[attr] = attrs_type[i](d[attr])
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 400

        eid = d["eid"]
        model_id = d["model_id"]

        # LOAD IN AND VALIDATE ENTITY
        entity = schema.Entity.find_one(eid=str(eid))
        if entity is None:
            LOGGER.exception('Error getting entity. Entity %s does not exist.', eid)
            return {'message': 'Entity {} does not exist'.format(eid)}, 400
        entity_features = pd.DataFrame(entity.features, index=[0])
        if entity_features is None:
            LOGGER.exception('Entity %s has no features. ', eid)
            return {'message': 'Entity {} does not have features.'.format(eid)}, 400

        # LOAD IN AND VALIDATE MODEL DATA
        success, payload = helpers.load_model(model_id, include_explainer=True)
        if success:
            model, transformer, explainer = payload
        else:
            message, error_code = payload
            return message, error_code

        contributions = lfe.get_contributions(
            entity_features, explainer, transformer).iloc[0].tolist()
        keys = list(entity_features.keys())
        contribution_dict = dict(zip(keys, contributions))
        return {"contributions": contribution_dict}, 200
