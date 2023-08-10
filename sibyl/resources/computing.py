import json
import logging
import os

import pandas as pd
from flask import request
from flask_restful import Resource

from sibyl import g
from sibyl import global_explanation as ge
from sibyl import helpers
from sibyl.db import schema

LOGGER = logging.getLogger(__name__)


def validate_changes(changes):
    """
    Helper function for validating changes to entity.
    """
    for feature, change in changes.items():
        if schema.Feature.find_one(name=feature) is None:
            LOGGER.exception(f"Invalid feature {feature}")
            return {"message": f"Invalid feature {feature}"}, 400

        if isinstance(change, (int, float)):
            change = float(change)

        if schema.Feature.find_one(name=feature).type == "binary" and change not in [
            0,
            1,
        ]:
            LOGGER.exception(f"Feature {feature} is binary, change value of {change} is invalid.")
            return {"message": f"Feature {feature} is binary, invalid change value"}, 400


class SingleChangePredictions(Resource):
    def post(self):
        """
        Get the resulting model predictions after changing the value of a single feature
        of an entity for each feature-value pair provided in the request.
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
                     $ref: '#/components/schemas/Changes'
                 required: ['eid', 'model_id', 'changes']
        responses:
          200:
            description: Resulting predictions after making changes
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    predictions:
                      type: array
                      items:
                        type: array
                        items:
                          oneOf:
                            type: string
                            type: number
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/singlechangepredictions-get-200.json'
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
            eid = str(d["eid"])
            model_id = str(d["model_id"])
            changes = d["changes"]
            validate_changes(changes)
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 400

        entity = schema.Entity.find_one(eid=eid)
        if entity is None:
            LOGGER.exception("Error getting entity. Entity %s does not exist.", eid)
            return {"message": "Entity {} does not exist".format(eid)}, 400
        entity_features = pd.DataFrame(entity.features, index=[0])

        success, payload = helpers.load_explainer(model_id)
        if success:
            explainer = payload[0]
        else:
            return payload

        predictions = []
        for feature, change in changes.items():
            modified = entity_features.copy()
            modified[feature] = change
            prediction = explainer.predict(modified)[0].tolist()
            predictions.append([feature, prediction])
        return {"predictions": predictions}, 200


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
                     $ref: '#/components/schemas/Changes'
                 required: ['eid', 'model_id', 'changes']
        responses:
          200:
            description: Resulting predictions after making changes
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    prediction:
                      type: number
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/modifiedprediction-get-200.json'
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
            eid = str(d["eid"])
            model_id = str(d["model_id"])
            changes = d["changes"]
            validate_changes(changes)
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 400

        entity = schema.Entity.find_one(eid=eid)
        if entity is None:
            LOGGER.exception("Error getting entity. Entity %s does not exist.", eid)
            return {"message": "Entity {} does not exist".format(eid)}, 400
        entity_features = pd.DataFrame(entity.features, index=[0])

        success, payload = helpers.load_explainer(model_id)
        if success:
            explainer = payload[0]
        else:
            return payload

        modified = entity_features.copy()
        for feature, change in changes.items():
            modified[feature] = change
        prediction = explainer.predict(modified)[0].tolist()
        return {"prediction": prediction}, 200


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
            return {"distributions": all_distributions[str(prediction)]["distributions"]}, 200

        # LOAD IN AND VALIDATE MODEL DATA
        success, payload = helpers.load_explainer(model_id, include_dataset=True)
        if success:
            explainer, dataset = payload
        else:
            return payload

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

        return {"distributions": distributions}, 200


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
            return {"count:": all_distributions[str(prediction)]["total cases"]}, 200

        # LOAD IN AND VALIDATE MODEL DATA
        success, payload = helpers.load_explainer(model_id, include_dataset=True)
        if success:
            explainer, dataset = payload
        else:
            return payload

        rows = ge.get_rows_by_output(prediction, explainer.predict, dataset, row_labels=None)
        count = len(rows)

        return {"count": count}, 200


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
            return {"distributions": {"PRO_PLSM_NEXT730_DUMMY": outcome_metrics}}, 200
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
                      type: object
                      additionalProperties:
                        type: number
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/contributions-post-200.json'
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
        success, payload = helpers.load_explainer(model_id)
        if success:
            explainer = payload[0]
        else:
            return payload

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
                      type: object
                      additionalProperties:
                        type: object
                        additionalProperties:
                          type: object
                          properties:
                            Feature Value:
                              oneOf:
                                type: string
                                type: number
                            Contribution:
                              type: number
                            Average\\/Mode:
                              oneOf:
                                type: string
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
        success, payload = helpers.load_explainer(model_id)
        if success:
            explainer = payload[0]
        else:
            return payload

        contributions = explainer.produce_feature_contributions(entities)
        contributions_json = {
            eid: contributions[eid].set_index("Feature Name").to_json(orient="index")
            for eid in contributions
        }

        return {"contributions": contributions_json}, 200


class ModifiedFeatureContribution(Resource):
    def post(self):
        """
        Get the feature contribution of an entity modified by changes
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
                     $ref: '#/components/schemas/Changes'
                 required: ['eid', 'model_id', 'changes']
        responses:
          200:
            description: Resulting feature contribution after making changes to entity
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    contribution:
                      type: object
                      additionalProperties:
                        type: object
                        properties:
                          Feature Value:
                            oneOf:
                              type: string
                              type: number
                          Contribution:
                            type: number
                          Average\\/Mode:
                            oneOf:
                              type: string
                              type: number
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/modifiedcontribution-post-200.json'
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
            eid = str(d["eid"])
            model_id = str(d["model_id"])
            changes = d["changes"]
            validate_changes(changes)
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 400

        entity = schema.Entity.find_one(eid=eid)
        if entity is None:
            LOGGER.exception("Error getting entity. Entity %s does not exist.", eid)
            return {"message": "Entity {} does not exist".format(eid)}, 400
        entity_features = pd.DataFrame(entity.features, index=[0])
        success, payload = helpers.load_explainer(model_id)
        if success:
            explainer = payload[0]
        else:
            return payload

        modified = entity_features.copy()
        for feature, change in changes.items():
            modified[feature] = change
        contribution = explainer.produce_feature_contributions(modified)[0]
        contribution_json = contribution.set_index("Feature Name").to_json(orient="index")
        return {"contribution": contribution_json}, 200


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
        success, payload = helpers.load_explainer(model_id, include_dataset=True)
        if success:
            explainer, dataset = payload
        else:
            return payload

        y = dataset["y"]
        X = dataset.drop("y", axis=1)
        similar_entities = explainer.produce_similar_examples(
            entities, x_train_orig=X, y_train=y, standardize=True
        )
        for eid in similar_entities:
            similar_entities[eid]["X"] = similar_entities[eid]["X"].to_json(orient="index")
            similar_entities[eid]["y"] = similar_entities[eid]["y"].to_json(orient="index")

        return {"similar_entities": similar_entities}, 200
