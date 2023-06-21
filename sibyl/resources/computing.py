import json
import logging
import os
import pickle

import pandas as pd
from flask import request
from flask_restful import Resource

from sibyl import g
from sibyl import global_explanation as ge
from sibyl import helpers
from sibyl.db import schema

LOGGER = logging.getLogger(__name__)


class SingleChangePredictions(Resource):
    def post(self):
        """
        Get the resulting model prediction after making changes, one at a time, to an entity
        ---
        tags:
          - computing
        security:
          - tokenAuth: []
        requestBody:
           required: true
           content:
             application/json:
               schema:
                 type: object
                 properties:
                   eid:
                     type: string
                   model_id:
                     type: string
                   changes:
                     type: array
                     items:
                       type: array
                       items:
                         oneOf:
                           type: string
                           type: number
                 required: ['eid', 'model_id', 'changes']
        responses:
          200:
            description: Resulting predictions after making changes
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    changes:
                        type: array
                        items:
                            type: number
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/entity-get-200.json'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        attrs = ["eid", "model_id", "changes"]
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
            d["eid"] = str(d["eid"])
            d["model_id"] = str(d["model_id"])
            for change in d["changes"]:
                change[0] = str(change[0])
                try:
                    change[1] = float(change[1])
                except:
                    pass
                if schema.Feature.find_one(name=change[0]) is None:
                    LOGGER.exception("Invalid feature %s" % change[0])
                    return {"message": "Invalid feature {}".format(change[0])}, 400
                if schema.Feature.find_one(name=change[0]).type == "binary" and change[1] not in [
                    0,
                    1,
                ]:
                    LOGGER.exception(
                        "Feature %s is binary, change value of %s is invalid."
                        % (change[0], change[1])
                    )
                    return {
                        "message": "Feature {} is binary, invalid change value".format(change[0])
                    }, 400
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 400

        eid = d["eid"]
        model_id = d["model_id"]
        changes = d["changes"]
        entity = schema.Entity.find_one(eid=eid)
        if entity is None:
            LOGGER.exception("Error getting entity. Entity %s does not exist.", eid)
            return {"message": "Entity {} does not exist".format(eid)}, 400
        entity_features = pd.DataFrame(entity.features, index=[0])

        model_doc = schema.Model.find_one(id=model_id)
        if model_doc is None:
            LOGGER.exception("Error getting model. Model %s does not exist.", model_id)
            return {"message": "Model {} does not exist".format(model_id)}, 400
        explainer_bytes = model_doc.explainer
        if explainer_bytes is None:
            LOGGER.exception("Model %s explainer has not been trained. ", model_id)
            return {"message": "Model {} does not have trained explainer".format(model_id)}, 400

        try:
            explainer = pickle.loads(explainer_bytes)
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 500

        predictions = []
        for change in changes:
            feature = change[0]
            value = change[1]
            modified = entity_features.copy()
            modified[feature] = value
            prediction = explainer.predict(modified)[0].tolist()
            predictions.append([feature, prediction])
        return {"changes": predictions}


class ModifiedPrediction(Resource):
    def post(self):
        """
        Get the resulting model prediction after making all changes
        ---
        tags:
          - computing
        security:
          - tokenAuth: []
        requestBody:
           required: true
           content:
             application/json:
               schema:
                 type: object
                 properties:
                   eid:
                     type: string
                   model_id:
                     type: string
                   changes:
                     type: array
                     items:
                       type: array
                       items:
                         oneOf:
                           type: string
                           type: number
                 required: ['eid', 'model_id', 'changes']
        responses:
          200:
            description: Resulting predictions after making changes
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    changes:
                        type: number
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/entity-get-200.json'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        attrs = ["eid", "model_id", "changes"]
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
            d["eid"] = str(d["eid"])
            d["model_id"] = str(d["model_id"])
            for change in d["changes"]:
                change[0] = str(change[0])
                try:
                    change[1] = float(change[1])
                except:
                    pass
                if schema.Feature.find_one(name=change[0]) is None:
                    LOGGER.exception("Invalid feature %s" % change[0])
                    return {"message": "Invalid feature {}".format(change[0])}, 400
                if schema.Feature.find_one(name=change[0]).type == "binary" and change[1] not in [
                    0,
                    1,
                ]:
                    LOGGER.exception(
                        "Feature %s is binary, change value of %s is invalid."
                        % (change[0], change[1])
                    )
                    return {
                        "message": "Feature {} is binary, invalid change value".format(change[0])
                    }, 400
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 400

        eid = d["eid"]
        model_id = d["model_id"]
        changes = d["changes"]
        entity = schema.Entity.find_one(eid=eid)
        if entity is None:
            LOGGER.exception("Error getting entity. Entity %s does not exist.", eid)
            return {"message": "Entity {} does not exist".format(eid)}, 400
        entity_features = pd.DataFrame(entity.features, index=[0])

        model_doc = schema.Model.find_one(id=model_id)
        if model_doc is None:
            LOGGER.exception("Error getting model. Model %s does not exist.", model_id)
            return {"message": "Model {} does not exist".format(model_id)}, 400
        explainer_bytes = model_doc.explainer
        if explainer_bytes is None:
            LOGGER.exception("Model %s explainer has not been trained. ", model_id)
            return {"message": "Model {} does not have trained explainer".format(model_id)}, 400

        try:
            explainer = pickle.loads(explainer_bytes)
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 500

        modified = entity_features.copy()
        for change in changes:
            feature = change[0]
            value = change[1]
            modified[feature] = value
        prediction = explainer.predict(modified)[0].tolist()
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
        attrs = ["prediction", "model_id"]
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
            return {"message": str(e)}, 400

        prediction = d["prediction"]
        model_id = d["model_id"]

        # CHECK FOR PRECOMPUTED VALUES
        distribution_filepath = g["config"]["feature_distribution_location"]
        if distribution_filepath is not None:
            distribution_filepath = os.path.normpath(distribution_filepath)
            with open(distribution_filepath, "r") as f:
                all_distributions = json.load(f)
            return {"distributions": all_distributions[str(prediction)]["distributions"]}

        # LOAD IN AND VALIDATE MODEL DATA
        success, payload = helpers.load_model(
            model_id, include_explainer=True, include_dataset=True
        )
        if success:
            model, dataset, explainer = payload
        else:
            message, error_code = payload
            return message, error_code

        # LOAD IN FEATURES
        feature_docs = schema.Feature.find()
        features = [
            {"name": feature_doc.name, "type": feature_doc.type} for feature_doc in feature_docs
        ]
        features = pd.DataFrame(features)

        # FIND CATEGORICAL FEATURES
        boolean_features = features[features["type"].isin(["binary", "categorical"])]["name"]
        categorical_dataset = dataset[boolean_features]

        numeric_features = features[features["type"] == "numeric"]["name"]
        numeric_dataset = dataset[numeric_features]

        distributions = {}
        rows = ge.get_rows_by_output(prediction, explainer.predict, dataset, row_labels=None)
        if len(rows) == 0:
            LOGGER.exception("No data with that prediction: %s", prediction)
            return {"message": "No data with that prediction: {}".format(prediction)}, 400

        cat_summary = ge.summary_categorical(categorical_dataset.iloc[rows])
        num_summary = ge.summary_numeric(numeric_dataset.iloc[rows])

        for i, name in enumerate(boolean_features):
            distributions[name] = {
                "type": "categorical",
                "metrics": [cat_summary[0][i].tolist(), cat_summary[1][i].tolist()],
            }
        for i, name in enumerate(numeric_features):
            distributions[name] = {"type": "numeric", "metrics": num_summary[i]}

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
        attrs = ["prediction", "model_id"]
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
            return {"message": str(e)}, 400

        prediction = d["prediction"]
        model_id = d["model_id"]

        distribution_filepath = g["config"]["feature_distribution_location"]
        if distribution_filepath is not None:
            distribution_filepath = os.path.normpath(distribution_filepath)
            with open(distribution_filepath, "r") as f:
                all_distributions = json.load(f)
            return {"count:": all_distributions[str(prediction)]["total cases"]}

        # LOAD IN AND VALIDATE MODEL DATA
        success, payload = helpers.load_model(
            model_id, include_explainer=True, include_dataset=True
        )
        if success:
            model, dataset, explainer = payload
        else:
            message, error_code = payload
            return message, error_code

        rows = ge.get_rows_by_output(prediction, explainer.predict, dataset, row_labels=None)

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
        attrs = ["prediction", "model_id"]
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
            return {"message": str(e)}, 400

        prediction = d["prediction"]

        distribution_filepath = g["config"]["feature_distribution_location"]
        if distribution_filepath is not None:
            distribution_filepath = os.path.normpath(distribution_filepath)
            with open(distribution_filepath, "r") as f:
                all_distributions = json.load(f)
            outcome_metrics = all_distributions[str(prediction)]["distributions"][
                "PRO_PLSM_NEXT730_DUMMY"
            ]
            return {"distributions": {"PRO_PLSM_NEXT730_DUMMY": outcome_metrics}}
        else:
            LOGGER.exception("Not implemented - Please provide precomputed document")
            return {"message": "Not implemented - Please provide precomputed document"}, 501


class FeatureContributions(Resource):
    def post(self):
        """
        Get feature contributions
        ---
        tags:
          - computing
        security:
          - tokenAuth: []
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  eid:
                    type: string
                  model_id:
                    type: string
                required: ['eid', 'model_id']
        responses:
          200:
            description: Feature contributions
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    contributions:
                        type: array
                        items:
                            type: number
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/entity-get-200.json'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """

        # LOAD IN AND CHECK ATTRIBUTES:
        attrs = ["eid", "model_id"]
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
            return {"message": str(e)}, 400

        eid = d["eid"]
        model_id = d["model_id"]

        # LOAD IN AND VALIDATE ENTITY
        entity = schema.Entity.find_one(eid=str(eid))
        if entity is None:
            LOGGER.exception("Error getting entity. Entity %s does not exist.", eid)
            return {"message": "Entity {} does not exist".format(eid)}, 400
        entity_features = pd.DataFrame(entity.features, index=[0])
        if entity_features is None:
            LOGGER.exception("Entity %s has no features. ", eid)
            return {"message": "Entity {} does not have features.".format(eid)}, 400

        # LOAD IN AND VALIDATE MODEL DATA
        success, payload = helpers.load_model(model_id, include_explainer=True)
        if success:
            model, explainer = payload
        else:
            message, error_code = payload
            return message, error_code

        contributions = explainer.produce_feature_contributions(entity_features)[0]
        keys = list(contributions["Feature Name"])
        contribution_dict = dict(zip(keys, contributions["Contribution"]))
        return {"contributions": contribution_dict}, 200


class MultiFeatureContributions(Resource):
    def post(self):
        """
        Get feature contributions for multiple eids
        ---
        tags:
          - computing
        security:
          - tokenAuth: []
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  eids:
                    type: array
                    items:
                        type: string
                  model_id:
                    type: string
                required: ['eids', 'model_id']
        responses:
          200:
            description: Feature contributions
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    contributions:
                        type: array
                        items:
                            type: number
          400:
            $ref: '#/components/responses/ErrorMessage'
        """

        # LOAD IN AND CHECK ATTRIBUTES:
        attrs = ["eids", "model_id"]
        d = dict()
        body = request.json
        for attr in attrs:
            d[attr] = None
            if body is not None:
                d[attr] = body.get(attr)
            else:
                if attr in request.form:
                    d[attr] = request.form[attr]

        eids = d["eids"]
        model_id = d["model_id"]

        entities = [
            dict(entity.features, **{"eid": entity.eid})
            for entity in schema.Entity.objects(eid__in=eids)
        ]
        entities = pd.DataFrame(entities)
        success, payload = helpers.load_model(model_id, include_explainer=True)
        if success:
            _, explainer = payload
        else:
            message, error_code = payload
            return message, error_code

        contributions = explainer.produce_feature_contributions(entities)
        contributions_json = {
            eid: contributions[eid].set_index("Feature Name").to_json(orient="index")
            for eid in contributions
        }

        return {"contributions": contributions_json}, 200


class SimilarEntities(Resource):
    def post(self):
        """
        Get nearest neighbors for list of eids
        ---
        tags:
          - computing
        security:
          - tokenAuth: []
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  eids:
                    type: array
                    items:
                        type: string
                  model_id:
                    type: string
                required: ['eids', 'model_id']
        responses:
          200:
            description: Feature contributions
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    contributions:
                        type: array
                        items:
                            type: number
          400:
            $ref: '#/components/responses/ErrorMessage'
        """

        # LOAD IN AND CHECK ATTRIBUTES:
        attrs = ["eids", "model_id"]
        d = dict()
        body = request.json
        for attr in attrs:
            d[attr] = None
            if body is not None:
                d[attr] = body.get(attr)
            else:
                if attr in request.form:
                    d[attr] = request.form[attr]

        eids = d["eids"]
        model_id = d["model_id"]

        entities = [
            dict(entity.features, **{"eid": entity.eid})
            for entity in schema.Entity.objects(eid__in=eids)
        ]
        entities = pd.DataFrame(entities)
        success, payload = helpers.load_model(
            model_id, include_dataset=True, include_explainer=True
        )
        if success:
            _, dataset, explainer = payload
        else:
            message, error_code = payload
            return message, error_code

        target = schema.Model.find_one(id=model_id).training_set.target
        y = dataset[target]
        X = dataset.drop(target, axis=1)
        similar_entities = explainer.produce_similar_examples(entities, x_train_orig=X, y_orig=y)
        for eid in similar_entities:
            similar_entities[eid]["X"] = similar_entities[eid]["X"].to_json(orient="index")
            similar_entities[eid]["y"] = similar_entities[eid]["y"].to_json(orient="index")

        return {"similar_entities": similar_entities}, 200
