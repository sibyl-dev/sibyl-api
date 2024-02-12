import base64
import logging

import numpy as np
import pandas as pd
from flask import request
from flask_restful import Resource

from sibyl import helpers
from sibyl.db import schema
from sibyl.resources.computing import Attrs, get_and_validate_params, get_entities_table

LOGGER = logging.getLogger(__name__)


def first(dict_):
    return dict_[next(iter(dict_))]


def get_model(model_doc, basic=True):
    model = {"model_id": model_doc.model_id}
    if not basic:
        model["description"] = model_doc.description
        model["performance"] = model_doc.performance
    return model


class Model(Resource):
    def get(self, model_id):
        """
        Get a Model by ID
        ---
        tags:
          - model
        parameters:
          - name: model_id
            in: path
            schema:
              type: string
            required: true
            description: ID of the model to get information about
        responses:
          200:
            description: Information about the model
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Model'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        model = schema.Model.find_one(model_id=model_id)
        if model is None:
            LOGGER.exception("Error getting model. Model %s does not exist.", model_id)
            return {"message": "Model {} does not exist".format(model_id)}, 400

        return get_model(model, basic=False), 200

    def put(self, model_id):
        """
        Update or create a model by id.
        ---
        description:
          "Note: Does not currently support updating realapp."
        tags:
          - model
        parameters:
          - name: model_id
            in: path
            schema:
              type: string
            required: true
            description: Name of the model to update/create
        requestBody:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FullModelNoRealapp'
        responses:
          200:
            description: Information about update model
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Model'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        model_data = request.json
        model = schema.Model.find_one(model_id=model_id)
        if "training_set_id" in model_data:
            training_set = schema.TrainingSet.find_one(id=model_data.pop("training_set_id"))
            model_data["training_set"] = training_set
        if "realapp" in model_data:
            model_data["realapp"] = base64.b64decode(model_data["realapp"])
        if model is None:
            model_data["model_id"] = model_id
            model = schema.Model(**model_data)
            model.save()
        else:
            model.modify(**model_data)
            model = model.save()
        return get_model(model, basic=False), 200


class Models(Resource):
    def get(self):
        """
        Get all Models
        ---
        tags:
          - model
        responses:
          200:
            description: All models
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    models:
                      type: array
                      items:
                        type: object
                        properties:
                          model_id:
                            type: string
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        documents = schema.Model.find()
        try:
            model = [get_model(document, basic=True) for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 500
        else:
            return {"models": model}, 200


class Importance(Resource):
    def get(self):
        """
        Get Model feature importances
        ---
        tags:
          - model
        parameters:
          - name: model_id
            in: path
            schema:
              type: string
            required: true
            description: ID of the model to get importances for
        responses:
          200:
            description: Feature importance for the model
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    importances:
                      type: array
                      items:
                        type: object
                        properties:
                          feature:
                            type: string
                          importance:
                            type: float
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        model_id = request.args.get("model_id", None)
        model = schema.Model.find_one(model_id=model_id)
        if model is None:
            LOGGER.exception("Error getting model. Model %s does not exist.", model_id)
            return {"message": "Model {} does not exist".format(model_id)}, 400

        importances = model.importances
        return {"importances": importances}, 200


class Prediction(Resource):
    def get(self):
        """
        Get a model prediction
        ---
        tags:
          - model
        parameters:
          - name: model_id
            in: query
            schema:
              type: string
            required: true
            description: ID of the model to use to predict
          - name: eid
            in: query
            schema:
              type: string
            required: true
            description: ID of the entity to predict on
          - name: row_id
            in: query
            schema:
              type: string
            description: ID of row to predict on (defaults to first row)
        responses:
          200:
            description: Prediction
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    output:
                      type: number
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        model_id = request.args.get("model_id", None)
        eid = request.args.get("eid", None)
        row_id = request.args.get("row_id", None)

        entity = schema.Entity.find_one(eid=eid)
        if entity is None:
            LOGGER.exception("Error getting entity. Entity %s does not exist.", eid)
            return {"message": "Entity {} does not exist".format(eid)}, 400
        if row_id is not None:
            if row_id not in entity.features:
                LOGGER.exception("row_id %s does not exist for entity %s", (row_id, eid))
                return {
                    "message": "row_id {} does not exist for entity {}".format(row_id, eid)
                }, 400
            entity_features = pd.DataFrame(entity.features[row_id], index=[0])
        else:
            entity_features = pd.DataFrame(first(entity.features), index=[0])

        success, payload = helpers.load_realapp(model_id)
        if success:
            realapp = payload[0]
        else:
            message, error_code = payload
            return message, error_code

        prediction = realapp.predict(entity_features)[0].tolist()
        return {"output": prediction}, 200


class MultiPrediction(Resource):
    def post(self):
        """
        Get multiple model predictions.
        ---
        description:
          If given multiple eids, return one prediction per eid (first row).
          If given one eid, return one prediction per row_id.
          Only one of eids and row_ids can contain more than one element.
        tags:
          - model
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
                    description: row_ids to select from the given eid
                  return_proba:
                    type: boolean
                required: ['eids', 'model_id']
        responses:
          200:
            description: Model predictions
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    predictions:
                      type: array
                      items:
                        type: number
          400:
            $ref: '#/components/responses/ErrorMessage'
        """

        def numpy_decoder(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        attr_info = [
            Attrs("eids", type=None),
            Attrs("model_id"),
            Attrs("row_ids", type=None, required=False),
            Attrs("return_proba", type=bool, required=False, default=False),
        ]

        eids, model_id, row_ids, return_proba = get_and_validate_params(attr_info)
        entities = get_entities_table(eids, row_ids)
        success, payload = helpers.load_realapp(model_id)
        if success:
            realapp = payload[0]
        else:
            message, error_code = payload
            return message, error_code
        if return_proba:
            prediction_probs = realapp.predict_proba(entities)
            # the probability of the predicted class is the largest in the output probabilities
            predictions = {
                key: numpy_decoder(np.max(prediction_probs[key])) for key in prediction_probs
            }
        else:
            predictions = realapp.predict(entities)
            predictions = {key: numpy_decoder(predictions[key]) for key in predictions}
        return {"predictions": predictions}, 200
