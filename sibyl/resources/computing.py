import json
import logging
import os
from collections import namedtuple

import pandas as pd
from flask import request
from flask_restful import Resource

from sibyl import helpers
from sibyl.db import schema

LOGGER = logging.getLogger(__name__)

Attrs = namedtuple("Attrs", ["name", "required", "type", "validation"], defaults=[True, str, None])


def get_features_for_row(features, row_id):
    if row_id is None:
        return features[next(iter(features))]
    else:
        if row_id not in features:
            LOGGER.exception("row_id %s does not exist for entity", (row_id))
            return {"message": "row_id {} does not exist for entity".format(row_id)}, 400
        return features[row_id]


def str_convert(s):
    return str(s) if s is not None else None


def get_and_validate_params(attr_info):
    """
    Get the parameters from the request body
    Args:
        attr_info (Attr named tuple):
            ("name" (string), "required" (boolean), "type" (type), "validation" (function))
            attr_type defaults to string
            required defaults to true
            validation defaults to none
    Returns:
        **args
            All parameters in attr (None if not required and not given)
    """
    d = {}
    body = request.json
    results = []
    for attr in attr_info:
        if body is not None:
            result = body.get(attr.name)
        elif attr.name in request.form:
            result = request.form[attr.name]
        elif not attr.required:
            result = None
        else:
            LOGGER.exception("Missing required parameter %s", attr.name)
            return {"message: Missing required parameter {}".format(attr.name)}, 400

        if result is not None:
            if attr.type is not None:
                try:
                    result = attr.type(result)
                except ValueError as e:
                    LOGGER.exception(e)
                    return {
                        "message: Error converting attr {} ({})".format(attr.name, str(e))
                    }, 400
            if attr.validation is not None:
                attr.validation(result)
        results.append(result)

    return results


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
                   row_id:
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
        attr_info = [
            Attrs("eid"),
            Attrs("model_id"),
            Attrs("row_id", False),
            Attrs("changes", type=None, validation=validate_changes),
        ]

        eid, model_id, row_id, changes = get_and_validate_params(attr_info)

        entity = schema.Entity.find_one(eid=eid)
        if entity is None:
            LOGGER.exception("Error getting entity. Entity %s does not exist.", eid)
            return {"message": "Entity {} does not exist".format(eid)}, 400
        entity_features = pd.DataFrame(get_features_for_row(entity.features, row_id), index=[0])

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
                   row_id:
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
        attr_info = [
            Attrs("eid"),
            Attrs("model_id"),
            Attrs("row_id", False),
            Attrs("changes", type=None, validation=validate_changes),
        ]

        eid, model_id, row_id, changes = get_and_validate_params(attr_info)

        entity = schema.Entity.find_one(eid=eid)
        if entity is None:
            LOGGER.exception("Error getting entity. Entity %s does not exist.", eid)
            return {"message": "Entity {} does not exist".format(eid)}, 400
        entity_features = pd.DataFrame(get_features_for_row(entity.features, row_id), index=[0])

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
                  row_id:
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

        attr_info = [Attrs("eid"), Attrs("model_id"), Attrs("row_id", False)]
        eid, model_id, row_id = get_and_validate_params(attr_info)

        # LOAD IN AND VALIDATE ENTITY
        entity = schema.Entity.find_one(eid=str(eid))
        if entity is None:
            LOGGER.exception("Error getting entity. Entity %s does not exist.", eid)
            return {"message": "Entity {} does not exist".format(eid)}, 400
        entity_features = pd.DataFrame(get_features_for_row(entity.features, row_id), index=[0])
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
        Get feature contributions for multiple eids, or for all rows in a single entity
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

        attr_info = [Attrs("eids", type=None), Attrs("model_id"), Attrs("row_id", False)]
        eids, model_id, row_id = get_and_validate_params(attr_info)

        if len(eids) > 1:
            entities = [
                dict(get_features_for_row(entity.features, None), **{"eid": entity.eid})
                for entity in schema.Entity.objects(eid__in=eids)
            ]
        else:
            entity_dict = schema.Entity.objects(eid=eids[0]).first().features
            # We mislabel the row_ids as eids intentionally here to take advantage of the
            #  underlying RealApp object having the id column set to "eid"
            entities = [dict(entity_dict[row_id], **{"eid": row_id}) for row_id in entity_dict]
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
                   row_id:
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
        attr_info = [
            Attrs("eid"),
            Attrs("model_id"),
            Attrs("row_id", False),
            Attrs("changes", type=None, validation=validate_changes),
        ]

        eid, model_id, row_id, changes = get_and_validate_params(attr_info)

        entity = schema.Entity.find_one(eid=eid)
        if entity is None:
            LOGGER.exception("Error getting entity. Entity %s does not exist.", eid)
            return {"message": "Entity {} does not exist".format(eid)}, 400
        entity_features = pd.DataFrame(get_features_for_row(entity.features, row_id), index=[0])
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
        Get nearest neighbors for list of eids, or for all rows in a single eid
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

        attr_info = [Attrs("eids", type=None), Attrs("model_id")]
        eids, model_id = get_and_validate_params(attr_info)

        if len(eids) > 1:
            entities = [
                dict(get_features_for_row(entity.features, None), **{"eid": entity.eid})
                for entity in schema.Entity.objects(eid__in=eids)
            ]
        else:
            entity_dict = schema.Entity.objects(eid=eids[0]).first().features
            # We mislabel the row_ids as eids intentionally here to take advantage of the
            #  underlying RealApp object having the id column set to "eid"
            entities = [dict(entity_dict[row_id], **{"eid": row_id}) for row_id in entity_dict]
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
            similar_entities[eid]["Input"] = similar_entities[eid]["Input"].to_json(orient="index")

        return {"similar_entities": similar_entities}, 200
