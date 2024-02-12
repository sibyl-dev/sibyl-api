import logging
from collections import namedtuple

import pandas as pd
from flask import request
from flask_restful import Resource

from sibyl import helpers
from sibyl.db import schema

LOGGER = logging.getLogger(__name__)

Attrs = namedtuple(
    "Attrs",
    ["name", "required", "type", "validation", "default"],
    defaults=[True, str, None, None],
)


def get_features_for_row(features, row_id):
    if row_id is None:
        return features[next(iter(features))]
    else:
        if row_id not in features:
            LOGGER.exception("row_id %s does not exist for entity", row_id)
            return {"message": "row_id {} does not exist for entity".format(row_id)}, 400
        return features[row_id]


def get_features_for_rows(features, row_ids):
    return [features[row_id] for row_id in row_ids]


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
    body = request.json
    results = []
    for attr in attr_info:
        if body is not None:
            result = body.get(attr.name)
        elif attr.name in request.form:
            result = request.form[attr.name]
        elif not attr.required:
            result = attr.default
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


def get_entity_table(eid, row_id):
    entity = schema.Entity.find_one(eid=eid)
    if entity is None:
        LOGGER.exception("Error getting entity. Entity %s does not exist.", eid)
        return {"message": "Entity {} does not exist".format(eid)}, 400
    return pd.DataFrame(get_features_for_row(entity.features, row_id), index=[eid])


def get_entities_table(eids, row_ids, all_rows=False):
    if not all_rows:
        if row_ids is None:
            entities = [
                dict(get_features_for_row(entity.features, row_ids), **{"eid": entity.eid})
                for entity in schema.Entity.objects(eid__in=eids)
            ]
        elif len(eids) > 1 and len(row_ids) > 1:
            LOGGER.exception("Only one of eids and row_ids can have more than one element")
            return {"message": "Only one of eids and row_ids can have more than one element"}, 400
        elif len(eids) > 1:
            entities = [
                dict(get_features_for_row(entity.features, row_ids[0]), **{"eid": entity.eid})
                for entity in schema.Entity.objects(eid__in=eids)
            ]
        else:
            entity = schema.Entity.find_one(eid=eids[0])
            entities = [dict(entity.features[row_id], **{"eid": row_id}) for row_id in row_ids]

    else:
        entity_dict = schema.Entity.objects(eid=eids[0]).first().features
        # We mislabel the row_ids as eids intentionally here to take advantage of the
        #  underlying RealApp object having the id column set to "eid"
        entities = [dict(entity_dict[row_id], **{"eid": row_id}) for row_id in entity_dict]
    return pd.DataFrame(entities)


class SingleChangePredictions(Resource):
    def post(self):
        """
        Get the resulting model predictions after changing the value of a single feature
        of an entity for each feature-value pair provided in the request.
        ---
        tags:
          - computing
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
                   return_proba:
                     type: boolean
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
                          type: ["string", "number"]
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        attr_info = [
            Attrs("eid"),
            Attrs("model_id"),
            Attrs("row_id", False),
            Attrs("changes", type=None, validation=validate_changes),
            Attrs("return_proba", required=False, type=bool, default=False),
        ]

        eid, model_id, row_id, changes, return_proba = get_and_validate_params(attr_info)

        entity_features = get_entity_table(eid, row_id)

        success, payload = helpers.load_realapp(model_id)
        if success:
            realapp = payload[0]
        else:
            return payload

        predictions = []
        for feature, change in changes.items():
            modified = entity_features.copy()
            modified[feature] = change
            if return_proba:
                prediction = realapp.predict_proba(modified, as_dict=False).max().tolist()[0]
            else:
                prediction = realapp.predict(modified, as_dict=False).tolist()[0]
            predictions.append([feature, prediction])
        return {"predictions": predictions}, 200


class ModifiedPrediction(Resource):
    def post(self):
        """
        Get the resulting model prediction after making all changes
        ---
        tags:
          - computing
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
                   return_proba:
                     type: boolean
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
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        attr_info = [
            Attrs("eid"),
            Attrs("model_id"),
            Attrs("row_id", False),
            Attrs("changes", type=None, validation=validate_changes),
            Attrs("return_proba", required=False, type=bool, default=False),
        ]

        eid, model_id, row_id, changes, return_proba = get_and_validate_params(attr_info)

        entity_features = get_entity_table(eid, row_id)

        success, payload = helpers.load_realapp(model_id)
        if success:
            realapp = payload[0]
        else:
            return payload

        modified = entity_features.copy()
        for feature, change in changes.items():
            modified[feature] = change
        if return_proba:
            prediction = realapp.predict_proba(modified, as_dict=False).max().tolist()[0]
        else:
            prediction = realapp.predict(modified, as_dict=False).tolist()[0]
        return {"prediction": prediction}, 200


class FeatureContributions(Resource):
    def post(self):
        """
        Get feature contributions
        ---
        tags:
          - computing
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
          400:
            $ref: '#/components/responses/ErrorMessage'
        """

        attr_info = [Attrs("eid"), Attrs("model_id"), Attrs("row_id", False)]
        eid, model_id, row_id = get_and_validate_params(attr_info)

        entity_features = get_entity_table(eid, row_id)

        # LOAD IN AND VALIDATE MODEL DATA
        success, payload = helpers.load_realapp(model_id)
        if success:
            realapp = payload[0]
        else:
            return payload

        contributions = realapp.produce_feature_contributions(entity_features)[0]
        contributions_json = contributions.set_index("Feature Name").to_dict(orient="index")
        return {"result": contributions_json}, 200


def get_contributions(realapp, entities):
    contributions, values = realapp.produce_feature_contributions(entities, format_output=False)
    contributions_json = contributions.to_dict(orient="index")
    values_json = values.to_dict(orient="index")

    return {"contributions": contributions_json, "values": values_json}, 200


class MultiFeatureContributions(Resource):
    def post(self):
        """
        Get feature contributions for multiple eids, or for multiple row_ids in a single entity
        ---
        tags:
          - computing
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
                  row_ids:
                    type: array
                    items:
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
                      properties:
                        Feature Name:
                            type: string
                        Feature Value:
                          type: ["string", "number"]
                        Contribution:
                          type: number
                        Average\\/Mode:
                          type: ["string", "number"]
          400:
            $ref: '#/components/responses/ErrorMessage'
        """

        attr_info = [
            Attrs("eids", type=None),
            Attrs("model_id"),
            Attrs("row_ids", type=None, required=False),
        ]
        eids, model_id, row_ids = get_and_validate_params(attr_info)

        entities = get_entities_table(eids, row_ids)
        success, payload = helpers.load_realapp(model_id)
        if success:
            realapp = payload[0]
        else:
            return payload

        return get_contributions(realapp, entities)


class ModifiedFeatureContribution(Resource):
    def post(self):
        """
        Get the feature contribution of an entity modified by changes
        ---
        tags:
          - computing
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
                      properties:
                        Feature Value:
                          type: ["string", "number"]
                        Contribution:
                          type: number
                        Average\\/Mode:
                          type: ["string", "number"]
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

        entity_features = get_entity_table(eid, row_id)
        success, payload = helpers.load_realapp(model_id)
        if success:
            realapp = payload[0]
        else:
            return payload

        modified = entity_features.copy()
        for feature, change in changes.items():
            modified[feature] = change
        return get_contributions(realapp, modified)


class SimilarEntities(Resource):
    def post(self):
        """
        Get nearest neighbors for list of eids, or for all rows in a single eid
        ---
        tags:
          - computing
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

        attr_info = [Attrs("eids", type=None), Attrs("model_id"), Attrs("row_id", required=False)]
        eids, model_id, row_id = get_and_validate_params(attr_info)
        if row_id is None:
            entities = get_entities_table(eids, row_id)
        else:
            entities = get_entities_table(eids, [row_id])
        success, payload = helpers.load_realapp(model_id, include_dataset=True)
        if success:
            realapp, dataset = payload
        else:
            return payload

        y = dataset["y"]
        X = dataset.drop("y", axis=1)
        similar_entities = realapp.produce_similar_examples(
            entities, x_train_orig=X, y_train=y, standardize=True
        )

        for eid in similar_entities:
            similar_entities[eid]["X"] = similar_entities[eid]["X"].to_dict(orient="index")
            similar_entities[eid]["y"] = similar_entities[eid]["y"].to_dict()
            similar_entities[eid]["Input"] = similar_entities[eid]["Input"].to_dict()

        return {"similar_entities": similar_entities}, 200
